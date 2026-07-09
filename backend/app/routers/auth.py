from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_min_role, require_roles
from app.database.session import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, RefreshTokenRequest, TokenResponse
from app.schemas.user import UserCreate, UserListResponse, UserResponse, UserUpdate
from app.services.auth_service import AuthService
from app.utils.constants import DEFAULT_ROLES, UserRole

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Annotated[Session, Depends(get_db)]) -> UserResponse:
    """
    Register a new user account.

    - First registered user automatically becomes **Admin** (system bootstrap).
    - Subsequent users get the requested role (default: employee).
    """
    return AuthService(db).register(user_data)


@router.post("/login", response_model=TokenResponse)
def login(credentials: LoginRequest, db: Annotated[Session, Depends(get_db)]) -> TokenResponse:
    """Authenticate with username/email and password. Returns JWT access + refresh tokens."""
    return AuthService(db).login(credentials)


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(body: RefreshTokenRequest, db: Annotated[Session, Depends(get_db)]) -> TokenResponse:
    """Exchange a valid refresh token for a new access + refresh token pair."""
    return AuthService(db).refresh_token(body.refresh_token)


@router.get("/me", response_model=UserResponse)
def get_me(current_user: Annotated[User, Depends(get_current_user)]) -> UserResponse:
    """Return the currently authenticated user's profile."""
    return UserResponse.model_validate(current_user)


@router.put("/me", response_model=UserResponse)
def update_me(
    user_data: UserUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> UserResponse:
    """Update own profile (cannot change role or active status)."""
    safe_update = UserUpdate(
        email=user_data.email,
        full_name=user_data.full_name,
        phone=user_data.phone,
    )
    return AuthService(db).update_user(current_user.id, safe_update)


@router.get("/roles")
def list_roles(db: Annotated[Session, Depends(get_db)]) -> list[dict[str, str]]:
    """List all available system roles."""
    return AuthService(db).list_roles()


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    user_data: UserCreate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_roles(UserRole.ADMIN))],
) -> UserResponse:
    """Create a new user with a specific role (Admin only)."""
    return AuthService(db).create_user(user_data)


@router.get("/users", response_model=UserListResponse)
def list_users(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_min_role(UserRole.STORE_MANAGER))],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> UserListResponse:
    """List all users (Store Manager and above)."""
    result = AuthService(db).list_users(page=page, page_size=page_size)
    return UserListResponse(**result)


@router.put("/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_roles(UserRole.ADMIN))],
) -> UserResponse:
    """Update any user including role and active status (Admin only)."""
    return AuthService(db).update_user(user_id, user_data)
