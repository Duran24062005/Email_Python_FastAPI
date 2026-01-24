# PRD: Email API Service - User Management System

## 1. Overview
This PRD outlines the user management system for administrators, including CRUD operations, role assignment, and user account management.

## 2. Objectives
- Enable admin users to manage user accounts
- Support role-based access control (RBAC)
- Provide user profile management
- Implement user account lifecycle (creation, activation, deactivation, deletion)
- Track user activity and permissions

## 3. Features

### 3.1 Get Current User Profile
- **Description**: Retrieve authenticated user's profile
- **Endpoint**: `GET /api/v1/users/me`
- **Requirements**:
  - Require authentication
  - Return user details with roles
  - Include verification status

### 3.2 Update User Profile
- **Description**: Update authenticated user's profile
- **Endpoint**: `PATCH /api/v1/users/me`
- **Requirements**:
  - Require authentication
  - Allow updating: first_name, last_name, phone, address
  - Prevent email/id changes
  - Update updated_at timestamp

### 3.3 List All Users (Admin)
- **Description**: Retrieve paginated list of all users
- **Endpoint**: `GET /api/v1/users?page=1&page_size=20`
- **Requirements**:
  - Require admin role
  - Pagination support
  - Filter by status (ACTIVE, PENDING_VERIFICATION, INACTIVE, SUSPENDED)
  - Option to include soft-deleted users
  - Return user details with roles

### 3.4 Get User Details (Admin)
- **Description**: Retrieve specific user by ID
- **Endpoint**: `GET /api/v1/users/{user_id}`
- **Requirements**:
  - Require admin role
  - Return full user details
  - Include user roles and permissions
  - Show timestamps (created_at, updated_at, deleted_at)

### 3.5 Soft Delete User (Admin)
- **Description**: Deactivate/soft-delete user account
- **Endpoint**: `DELETE /api/v1/users/{user_id}`
- **Requirements**:
  - Require admin role
  - Prevent self-deletion
  - Set deleted_at timestamp
  - Preserve user data
  - Revoke active sessions

### 3.6 Assign Role to User (Admin)
- **Description**: Assign a role to user
- **Endpoint**: `POST /api/v1/users/{user_id}/roles`
- **Requirements**:
  - Require admin role
  - Validate role existence
  - Prevent duplicate role assignments
  - Return updated user with roles

### 3.7 Remove Role from User (Admin)
- **Description**: Remove a role from user
- **Endpoint**: `DELETE /api/v1/users/{user_id}/roles/{role_id}`
- **Requirements**:
  - Require admin role
  - Validate user and role existence
  - Return updated user with roles
  - Prevent removing all admin roles

## 4. User Model Fields
- Basic: id, email, first_name, last_name, phone, address
- Status: status, email_verified_at, deleted_at
- Timestamps: created_at, updated_at
- Relations: roles (many-to-many)

## 5. Role and Permission System
- **Roles**: admin, editor, viewer, user
- **Permissions**: 
  - admin.access (all operations)
  - user.edit (edit own profile)
  - email.send (send emails)
  - email.view (view sent emails)
  - user.manage (admin: manage users)

## 6. User Account Lifecycle
1. Registration → PENDING_VERIFICATION
2. Email verification → ACTIVE
3. Deactivation by user → INACTIVE
4. Admin suspension → SUSPENDED
5. Soft delete → deleted_at set

## 7. Security Requirements
- Passwords never returned in API responses
- Email changes require verification
- Role changes logged to audit trail
- Admin actions require admin confirmation
- Session invalidation on role changes

## 8. Non-Functional Requirements
- **Performance**: List 1000 users in < 1 second
- **Scalability**: Support 100,000+ users
- **Data Integrity**: ACID compliance
- **Audit**: All changes logged

## 9. Error Handling
- User not found: 404
- Insufficient permissions: 403
- Invalid role: 400
- Self-deletion attempt: 400
- Database error: 500

## 10. Success Metrics
- User creation success rate > 99%
- Role assignment latency < 100ms
- Zero unauthorized access
- Admin satisfaction > 4/5

## 11. Timeline
- Phase 1: User CRUD (Week 1)
- Phase 2: Role management (Week 2)
- Phase 3: Audit logging (Week 3)
