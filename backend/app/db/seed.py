"""Safe development seeding for initial roles and dev staff accounts."""
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.role import Role
from app.models.user import User


def seed_database(db: Session) -> None:
    """Idempotently seed default roles and development test accounts."""
    # 1. Seed Roles
    roles = {
        "ADMIN": "Hospital Administrator with full system and staff access",
        "DOCTOR": "Attending physician with access to patient clinical charts and review",
    }
    role_objs: dict[str, Role] = {}
    for role_name, description in roles.items():
        stmt = select(Role).where(Role.name == role_name)
        role = db.scalars(stmt).first()
        if not role:
            role = Role(
                id=uuid.uuid4(),
                name=role_name,
                description=description,
            )
            db.add(role)
            db.flush()
            print(f"Created role: {role_name}")
        role_objs[role_name] = role

    # 2. Seed Development Test Users (Dev-only default passwords)
    dev_users = [
        {
            "email": "admin@medikiosk.local",
            "full_name": "Dr. Sarah Connor (Admin)",
            "phone": "+1-555-0199",
            "password": "AdminPassword123!",
            "role": "ADMIN",
        },
        {
            "email": "doctor@medikiosk.local",
            "full_name": "Dr. John Watson (Doctor)",
            "phone": "+1-555-0123",
            "password": "DoctorPassword123!",
            "role": "DOCTOR",
        },
    ]

    for u_data in dev_users:
        stmt = select(User).where(User.email == u_data["email"])
        user = db.scalars(stmt).first()
        if not user:
            user = User(
                id=uuid.uuid4(),
                email=u_data["email"],
                full_name=u_data["full_name"],
                phone=u_data["phone"],
                password_hash=hash_password(u_data["password"]),
                role_id=role_objs[u_data["role"]].id,
                is_active=True,
            )
            db.add(user)
            print(f"Created dev staff user: {u_data['email']} ({u_data['role']})")

    db.commit()
    print("Database seeding completed successfully.")


if __name__ == "__main__":
    with SessionLocal() as session:
        seed_database(session)
