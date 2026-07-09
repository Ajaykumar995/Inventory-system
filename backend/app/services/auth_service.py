from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.auth.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)
from app.repository.user_repository import UserRepository
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.utils.constants import DEFAULT_ROLES, UserRole


class AuthService:
    """Business logic for authentication and user management."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.user_repo = UserRepository(db)

    def register(self, user_data: UserCreate) -> UserResponse:
        """
        Register a new user.

        Business rule: First user becomes Admin (bootstrap).
        Subsequent registrations default to Employee unless Admin assigns role.
        """
        self.user_repo.seed_roles(DEFAULT_ROLES)

        if self.user_repo.get_by_email(user_data.email):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

        if self.user_repo.get_by_username(user_data.username):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already taken")

        _, total_users = self.user_repo.list_users(limit=1)
        if total_users == 0:
            role_name = UserRole.ADMIN.value
        else:
            # Public registration always creates employees; admins assign roles later.
            role_name = UserRole.EMPLOYEE.value

        role = self.user_repo.get_role_by_name(role_name)
        if role is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role not found")

        hashed = get_password_hash(user_data.password)
        user = self.user_repo.create_user(user_data, hashed, role)
        return UserResponse.model_validate(user)

    def create_user(self, user_data: UserCreate) -> UserResponse:
        """Admin-only: create a user with a specific role."""
        self.user_repo.seed_roles(DEFAULT_ROLES)

        if self.user_repo.get_by_email(user_data.email):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
        if self.user_repo.get_by_username(user_data.username):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already taken")

        try:
            role_name = UserRole(user_data.role_name).value
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid role. Allowed: {[r.value for r in UserRole]}",
            ) from exc

        role = self.user_repo.get_role_by_name(role_name)
        if role is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role not found")

        hashed = get_password_hash(user_data.password)
        user = self.user_repo.create_user(user_data, hashed, role)
        return UserResponse.model_validate(user)

    def list_roles(self) -> list[dict]:
        self.user_repo.seed_roles(DEFAULT_ROLES)
        return DEFAULT_ROLES

    def login(self, credentials: LoginRequest) -> TokenResponse:
        user = self.user_repo.get_by_username(credentials.username)
        if user is None or not verify_password(credentials.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
            )

        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is deactivated")

        user.last_login = datetime.now(UTC)
        self.db.commit()

        token_data = {"sub": str(user.id), "role": user.role.name}
        return TokenResponse(
            access_token=create_access_token(token_data),
            refresh_token=create_refresh_token(token_data),
        )

    def refresh_token(self, refresh_token: str) -> TokenResponse:
        try:
            payload = decode_token(refresh_token)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

        if payload.get("type") != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")

        user = self.user_repo.get_by_id(int(payload["sub"]))
        if user is None or not user.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")

        token_data = {"sub": str(user.id), "role": user.role.name}
        return TokenResponse(
            access_token=create_access_token(token_data),
            refresh_token=create_refresh_token(token_data),
        )

    def get_current_user_profile(self, user_id: int) -> UserResponse:
        user = self.user_repo.get_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return UserResponse.model_validate(user)

    def update_user(self, user_id: int, user_data: UserUpdate) -> UserResponse:
        user = self.user_repo.get_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        role = None
        if user_data.role_name is not None:
            try:
                role_name = UserRole(user_data.role_name).value
            except ValueError as exc:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid role. Allowed: {[r.value for r in UserRole]}",
                ) from exc
            role = self.user_repo.get_role_by_name(role_name)
            if role is None:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role not found")

        updated = self.user_repo.update_user(user, user_data, role)
        return UserResponse.model_validate(updated)

    def list_users(self, page: int = 1, page_size: int = 20) -> dict:
        skip = (page - 1) * page_size
        users, total = self.user_repo.list_users(skip=skip, limit=page_size)
        return {
            "items": [UserResponse.model_validate(u) for u in users],
            "total": total,
            "page": page,
            "page_size": page_size,
        }
