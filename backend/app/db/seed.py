"""Safe development seeding for initial roles, dev staff accounts, hospitals, streams, and departments."""
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.department import Department
from app.models.hospital import Hospital
from app.models.medical_stream import MedicalStream
from app.models.role import Role
from app.models.user import User


def seed_database(db: Session) -> None:
    """Idempotently seed default roles, test accounts, hospital, streams, and departments."""
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

    # 2. Seed Default Hospital
    default_hospital_code = "HOSP-001"
    stmt = select(Hospital).where(Hospital.code == default_hospital_code)
    hospital = db.scalars(stmt).first()
    if not hospital:
        hospital = Hospital(
            id=uuid.uuid4(),
            name="MediKiosk General Hospital",
            code=default_hospital_code,
            address="100 Hospital Way, Medical Enclave",
            city="New Delhi",
            state="Delhi",
            country="India",
            phone="+91-11-26588500",
            email="info@medikiosk-hospital.in",
            is_active=True,
        )
        db.add(hospital)
        db.flush()
        print(f"Created hospital: {hospital.name} ({hospital.code})")

    # 3. Seed Development Test Users (Dev-only default passwords)
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
                hospital_id=hospital.id,
                email=u_data["email"],
                full_name=u_data["full_name"],
                phone=u_data["phone"],
                password_hash=hash_password(u_data["password"]),
                role_id=role_objs[u_data["role"]].id,
                is_active=True,
            )
            db.add(user)
            print(f"Created dev staff user: {u_data['email']} ({u_data['role']})")
        elif user.hospital_id is None:
            user.hospital_id = hospital.id

    # 4. Seed Medical Streams
    streams = [
        {
            "code": "MODERN_MEDICINE",
            "name": "Modern Medicine",
            "description": "Allopathic MBBS clinical case-taking and diagnostics",
        },
        {
            "code": "AYUSH",
            "name": "AYUSH / Ayurveda",
            "description": "Traditional Ayurvedic holistic assessment (Prakriti, Agni, Dosha)",
        },
    ]
    for s_data in streams:
        stmt = select(MedicalStream).where(MedicalStream.code == s_data["code"])
        stream = db.scalars(stmt).first()
        if not stream:
            stream = MedicalStream(
                id=uuid.uuid4(),
                code=s_data["code"],
                name=s_data["name"],
                description=s_data["description"],
                is_active=True,
            )
            db.add(stream)
            print(f"Created medical stream: {stream.name} ({stream.code})")

    # 5. Seed Departments
    departments = [
        {
            "code": "GEN_MED",
            "name": "General Medicine",
            "description": "Primary healthcare, fever, diabetes, routine infections, general symptoms",
            "stream_code": "MODERN_MEDICINE",
        },
        {
            "code": "CARDIO",
            "name": "Cardiology",
            "description": "Heart conditions, chest pain, palpitations, hypertension",
            "stream_code": "MODERN_MEDICINE",
        },
        {
            "code": "NEURO",
            "name": "Neurology",
            "description": "Headaches, seizures, numbness, dizziness, neuropathy",
            "stream_code": "MODERN_MEDICINE",
        },
        {
            "code": "ORTHO",
            "name": "Orthopedics",
            "description": "Joint pain, fractures, backache, mobility issues",
            "stream_code": "MODERN_MEDICINE",
        },
        {
            "code": "DERMA",
            "name": "Dermatology",
            "description": "Skin rashes, allergies, infections, hair/nail issues",
            "stream_code": "MODERN_MEDICINE",
        },
        {
            "code": "AYURVEDA",
            "name": "Ayurveda & Panchakarma",
            "description": "Constitutional balance, chronic wellness, digestive & Vata/Pitta/Kapha disorders",
            "stream_code": "AYUSH",
        },
    ]

    for d_data in departments:
        stmt = select(Department).where(
            Department.code == d_data["code"],
            Department.hospital_id == hospital.id,
        )
        dept = db.scalars(stmt).first()
        if not dept:
            dept = Department(
                id=uuid.uuid4(),
                hospital_id=hospital.id,
                code=d_data["code"],
                name=d_data["name"],
                description=d_data["description"],
                stream_code=d_data["stream_code"],
                is_active=True,
            )
            db.add(dept)
            print(f"Created department: {dept.name} ({dept.code})")

    db.commit()
    print("Database seeding completed successfully.")


if __name__ == "__main__":
    with SessionLocal() as session:
        seed_database(session)
