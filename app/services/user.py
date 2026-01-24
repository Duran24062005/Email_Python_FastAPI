"""User service with business logic for registration and management."""

from datetime import timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AlreadyExistsError, NotFoundError, ValidationError
from app.core.security import create_access_token, decode_token, hash_password
from app.models.user import User, UserStatus
from app.repositories.role import RoleRepository
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate, UserUpdate


class UserService:
    """Service class for user-related business logic."""

    # Token expiration for email verification (24 hours)
    EMAIL_VERIFICATION_EXPIRE_HOURS = 24

    async def register_user(
        self,
        db: AsyncSession,
        user_data: UserCreate,
    ) -> tuple[User, str]:
        """
        Register a new user.

        Args:
            db: Database session
            user_data: User registration data

        Returns:
            Tuple of (created user, verification token)

        Raises:
            AlreadyExistsError: If email is already registered
        """
        user_repo = UserRepository(db)

        # Check if email already exists (including pending verification users)
        existing_user = await user_repo.get_by_email(user_data.email)
        if existing_user:
            raise AlreadyExistsError("User", "email", user_data.email)

        # Hash password and create user
        hashed_password = hash_password(user_data.password)
        user = await user_repo.create(
            email=user_data.email,
            hashed_password=hashed_password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            phone=user_data.phone,
            address=user_data.address,
            _status=UserStatus.PENDING_VERIFICATION.value,
        )
        
        # Commit to ensure user is persisted before returning
        await db.commit()

        # Reload user with roles relationship
        reloaded_user = await user_repo.get_with_roles(user.id)
        assert reloaded_user is not None  # User was just created, must exist

        # Generate email verification token
        verification_token = self._create_verification_token(reloaded_user.id, reloaded_user.email)
        user = reloaded_user

        return user, verification_token

    async def verify_email(self, db: AsyncSession, token: str) -> User:
        """
        Verify user's email with token.

        Args:
            db: Database session
            token: Email verification token

        Returns:
            Updated user with verified email

        Raises:
            ValidationError: If token is invalid or expired
            NotFoundError: If user not found
        """
        # Decode and validate token
        payload = decode_token(token)
        if payload is None:
            raise ValidationError("Invalid or expired verification token")

        if payload.get("type") != "email_verification":
            raise ValidationError("Invalid token type")

        user_id = payload.get("sub")
        if user_id is None:
            raise ValidationError("Invalid token payload")

        user_repo = UserRepository(db)
        # Use get_with_roles to ensure user is found correctly
        user = await user_repo.get_with_roles(int(user_id))

        if user is None:
            raise NotFoundError("User", user_id)

        if user.email_verified_at is not None:
            raise ValidationError("Email already verified")

        # Verify email and activate account
        user = await user_repo.verify_email(user)
        # Commit to ensure changes are persisted
        await db.commit()
        return user

    async def get_user(self, db: AsyncSession, user_id: int) -> User:
        """
        Get a user by ID.

        Raises:
            NotFoundError: If user not found
        """
        user_repo = UserRepository(db)
        user = await user_repo.get_with_roles(user_id)

        if user is None:
            raise NotFoundError("User", user_id)

        return user

    async def get_user_by_email(self, db: AsyncSession, email: str) -> User:
        """
        Get a user by email.

        Raises:
            NotFoundError: If user not found
        """
        user_repo = UserRepository(db)
        user = await user_repo.get_by_email_with_roles(email)

        if user is None:
            raise NotFoundError("User", email)

        return user

    async def update_user(
        self,
        db: AsyncSession,
        user_id: int,
        user_data: UserUpdate,
    ) -> User:
        """
        Update user profile.

        Raises:
            NotFoundError: If user not found
        """
        user_repo = UserRepository(db)

        # Get only fields that were actually provided
        update_data = user_data.model_dump(exclude_unset=True)

        if not update_data:
            # Nothing to update, just return current user
            user = await user_repo.get_with_roles(user_id)
            if user is None:
                raise NotFoundError("User", user_id)
            return user

        user = await user_repo.update(user_id, **update_data)

        if user is None:
            raise NotFoundError("User", user_id)

        # Reload with roles
        return await user_repo.get_with_roles(user_id)  # type: ignore

    async def soft_delete_user(self, db: AsyncSession, user_id: int) -> User:
        """
        Soft delete a user.

        Raises:
            NotFoundError: If user not found or already deleted
        """
        user_repo = UserRepository(db)
        user = await user_repo.soft_delete(user_id)

        if user is None:
            raise NotFoundError("User", user_id)

        return user

    async def assign_role(
        self,
        db: AsyncSession,
        user_id: int,
        role_id: int,
    ) -> User:
        """
        Assign a role to a user.

        Raises:
            NotFoundError: If user or role not found
        """
        user_repo = UserRepository(db)
        role_repo = RoleRepository(db)

        user = await user_repo.get_with_roles(user_id)
        if user is None:
            raise NotFoundError("User", user_id)

        role = await role_repo.get(role_id)
        if role is None:
            raise NotFoundError("Role", role_id)

        return await user_repo.add_role(user, role)

    async def remove_role(
        self,
        db: AsyncSession,
        user_id: int,
        role_id: int,
    ) -> User:
        """
        Remove a role from a user.

        Raises:
            NotFoundError: If user or role not found
        """
        user_repo = UserRepository(db)
        role_repo = RoleRepository(db)

        user = await user_repo.get_with_roles(user_id)
        if user is None:
            raise NotFoundError("User", user_id)

        role = await role_repo.get(role_id)
        if role is None:
            raise NotFoundError("Role", role_id)

        return await user_repo.remove_role(user, role)

    async def get_users(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20,
        include_deleted: bool = False,
        status: UserStatus | None = None,
    ) -> tuple[list[User], int]:
        """
        Get paginated list of users.

        Returns:
            Tuple of (users list, total count)
        """
        user_repo = UserRepository(db)

        users = await user_repo.get_all_with_roles(
            skip=skip,
            limit=limit,
            include_deleted=include_deleted,
            status=status,
        )
        total = await user_repo.count(include_deleted=include_deleted)

        return users, total

    def _create_verification_token(self, user_id: int, email: str) -> str:
        """Create a JWT token for email verification."""
        return create_access_token(
            data={
                "sub": str(user_id),
                "email": email,
                "type": "email_verification",
            },
            expires_delta=timedelta(hours=self.EMAIL_VERIFICATION_EXPIRE_HOURS),
        )


# Singleton instance
user_service = UserService()