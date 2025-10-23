from typing import Optional

from sqlmodel import Session, select

from app.models.auth import User


class UserCRUD:
    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """根据用户名查询用户"""
        statement = select(User).where(User.username == username)
        return db.execute(statement).scalar_one_or_none()

    @staticmethod
    def get_user_by_mobile_phone(db: Session, mobile_phone: str) -> Optional[User]:
        """根据手机号查询用户"""
        statement = select(User).where(User.mobile_phone == mobile_phone)
        return db.execute(statement).scalar_one_or_none()

    @staticmethod
    def create_user(db: Session, user: User) -> User:
        """创建用户"""
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def check_username_exists(db: Session, username: str) -> bool:
        """检查用户名是否存在"""
        return UserCRUD.get_user_by_username(db, username) is not None

    @staticmethod
    def check_mobile_phone_exists(db: Session, mobile_phone: str) -> bool:
        """检查手机号是否存在"""
        return UserCRUD.get_user_by_mobile_phone(db, mobile_phone) is not None

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """根据用户ID查询用户"""
        statement = select(User).where(User.id == user_id)
        return db.execute(statement).scalar_one_or_none()

    @staticmethod
    def update_user_password(db: Session, user_id: int, new_password_hash: str) -> Optional[User]:
        """更新用户密码"""
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.password_hash = new_password_hash
            db.add(user)
            db.commit()
            db.refresh(user)
        return user


# 创建全局实例
auth_crud = UserCRUD()
