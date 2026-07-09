from sqlalchemy import or_, select
from sqlalchemy.orm import Session, joinedload

from app.models.role import Role
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class UserRepository:
    """Data access layer for User and Role entities."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, user_id: int) -> User | None:
        stmt = select(User).options(joinedload(User.role)).where(User.id == user_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_username(self, username: str) -> User | None:
        stmt = (
            select(User)
            .options(joinedload(User.role))
            .where(or_(User.username == username, User.email == username))
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_email(self, email: str) -> User | None:
        stmt = select(User).options(joinedload(User.role)).where(User.email == email)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_role_by_name(self, role_name: str) -> Role | None:
        stmt = select(Role).where(Role.name == role_name)
        return self.db.execute(stmt).scalar_one_or_none()

    def list_roles(self) -> list[Role]:
        stmt = select(Role).order_by(Role.id)
        return list(self.db.execute(stmt).scalars().all())

    def list_users(self, skip: int = 0, limit: int = 20) -> tuple[list[User], int]:
        count_stmt = select(User)
        total = len(self.db.execute(count_stmt).scalars().all())

        stmt = (
            select(User)
            .options(joinedload(User.role))
            .order_by(User.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        users = list(self.db.execute(stmt).unique().scalars().all())
        return users, total

    def create_user(self, user_data: UserCreate, hashed_password: str, role: Role) -> User:
        user = User(
            email=user_data.email.lower(),
            username=user_data.username.lower(),
            hashed_password=hashed_password,
            full_name=user_data.full_name,
            phone=user_data.phone,
            role_id=role.id,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return self.get_by_id(user.id)  # type: ignore[return-value]

    def update_user(self, user: User, user_data: UserUpdate, role: Role | None = None) -> User:
        if user_data.email is not None:
            user.email = user_data.email.lower()
        if user_data.full_name is not None:
            user.full_name = user_data.full_name
        if user_data.phone is not None:
            user.phone = user_data.phone
        if user_data.is_active is not None:
            user.is_active = user_data.is_active
        if role is not None:
            user.role_id = role.id

        self.db.commit()
        self.db.refresh(user)
        return self.get_by_id(user.id)  # type: ignore[return-value]

    def seed_roles(self, roles: list[dict[str, str]]) -> None:
        for role_data in roles:
            existing = self.get_role_by_name(role_data["name"])
            if existing is None:
                self.db.add(Role(name=role_data["name"], description=role_data["description"]))
        self.db.commit()
