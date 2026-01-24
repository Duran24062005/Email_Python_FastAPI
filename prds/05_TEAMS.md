# PRD: Teams Feature - Structure Preparation

## 1. Overview

This PRD documents the **prepared structure** for the Teams feature. **Note: The functionality is NOT yet implemented** - only the database models and relationships have been created to support future team management capabilities.

## 2. Purpose

Teams will allow users to:
- Organize into groups for collaboration
- Share resources within a team context
- Manage team-specific permissions and roles
- Maintain separation between teams while allowing global admin access

## 3. Current Status

**Status**: Structure Prepared, Functionality Not Implemented

The following has been completed:
- Database models (`Team`, `user_team` association table)
- Relationships between User and Team models
- Helper methods in User model for team operations
- Database schema ready for team functionality

The following is **NOT yet implemented**:
- API endpoints for team management
- Team creation/deletion endpoints
- Team member management endpoints
- Team-specific permissions/authorization
- Team-based resource access control

## 4. Database Structure

### 4.1 Team Model

**Table**: `team`

**Fields**:
- `id`: Primary key (auto-increment)
- `name`: Team name (required, indexed, max 100 chars)
- `description`: Optional team description (text)
- `owner_id`: Foreign key to `user.id` (the user who created the team)
- `created_at`: Timestamp (auto-generated)
- `updated_at`: Timestamp (auto-updated)
- `deleted_at`: Soft delete timestamp (nullable)

**Relationships**:
- `owner`: Many-to-one relationship with User (team creator)
- `members`: Many-to-many relationship with User (team members)

### 4.2 User-Team Association

**Table**: `user_team`

**Fields**:
- `user_id`: Foreign key to `user.id` (primary key)
- `team_id`: Foreign key to `team.id` (primary key)
- `role_in_team`: String (default: "member") - Current values: "owner", "member"
- `joined_at`: Timestamp (auto-generated when user joins)

**Purpose**:
- Links users to teams
- Stores team-specific role (owner, member)
- Extensible for future team-specific roles (e.g., "admin", "viewer", "editor")

### 4.3 User Model Extensions

**New Relationships**:
- `teams`: List of teams the user belongs to (via `user_team`)
- `owned_teams`: List of teams the user owns/created

**New Helper Methods**:
- `has_team(team_id: int) -> bool`: Check if user belongs to a team
- `is_team_owner(team_id: int) -> bool`: Check if user owns a team
- `get_teams() -> list[Team]`: Get all teams user belongs to

## 5. Design Decisions

### 5.1 Global Roles vs Team Roles

- **Global Roles**: Admin, User (system-wide permissions)
- **Team Roles**: Owner, Member (team-specific permissions)
- Teams do NOT override global roles - they are complementary
- Admin users can access all teams regardless of membership

### 5.2 Team Ownership

- Each team has exactly one owner (the creator)
- Owner has full control over the team
- Ownership can be transferred (future feature)
- Owner cannot be removed from team (must transfer ownership first)

### 5.3 Soft Delete

- Teams support soft delete via `deleted_at` field
- Soft-deleted teams are hidden from normal queries
- Admin users can view/restore soft-deleted teams (future feature)

## 6. Future Implementation Plan

### Phase 1: Basic Team Management (Not Started)
- Create team endpoint
- List user's teams endpoint
- Get team details endpoint
- Delete team endpoint (soft delete)

### Phase 2: Team Member Management (Not Started)
- Add member to team endpoint
- Remove member from team endpoint
- List team members endpoint
- Update member role endpoint

### Phase 3: Team Permissions (Not Started)
- Team-specific permission system
- Resource access control by team
- Team-based email sending limits

### Phase 4: Advanced Features (Not Started)
- Transfer team ownership
- Team invitations
- Team activity logs
- Team templates and resources

## 7. API Endpoints (Planned, Not Implemented)

### 7.1 Team Management
```
POST   /api/v1/teams              - Create team
GET    /api/v1/teams              - List user's teams
GET    /api/v1/teams/{id}         - Get team details
PUT    /api/v1/teams/{id}         - Update team
DELETE /api/v1/teams/{id}         - Delete team (soft)
```

### 7.2 Team Members
```
POST   /api/v1/teams/{id}/members        - Add member
GET    /api/v1/teams/{id}/members        - List members
PUT    /api/v1/teams/{id}/members/{uid}  - Update member role
DELETE /api/v1/teams/{id}/members/{uid}  - Remove member
```

## 8. Security Considerations

### 8.1 Access Control (Future)
- Only team owner can modify team
- Only team owner can add/remove members
- Team members can view team details
- Admin users have full access to all teams

### 8.2 Data Isolation (Future)
- Users can only see teams they belong to (unless admin)
- Team resources are isolated from other teams
- Global admin can access all teams

## 9. Migration Notes

### 9.1 Database Migration
The team structure has been added to the database schema. When implementing functionality:
1. Ensure all existing users can continue working normally
2. Teams are optional - users don't need to belong to any team
3. Existing emails and resources are not affected by team structure

### 9.2 Backward Compatibility
- All existing functionality remains unchanged
- Teams are additive, not replacing existing features
- Global roles (admin/user) continue to work as before

## 10. Testing Strategy (Future)

When implementing team functionality:
- Unit tests for team model and relationships
- Integration tests for team API endpoints
- Authorization tests for team access control
- Performance tests for team queries

## 11. Notes

- This PRD documents the **prepared structure only**
- No team functionality is currently available via API
- The database schema is ready for implementation
- Implementation should follow the existing code patterns (async, SOLID principles)
