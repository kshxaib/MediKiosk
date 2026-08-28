"""Safe development seeding for initial roles, dev staff accounts, hospitals, streams, and departments."""
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.clinical_workflow import ClinicalWorkflow
from app.models.question import Question
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


    # 6. Seed Clinical Workflows
    # 6a. Modern Medicine - General Medicine Intake
    stmt_mod_stream = select(MedicalStream).where(MedicalStream.code == "MODERN_MEDICINE")
    mod_stream = db.scalars(stmt_mod_stream).first()

    stmt_gen_med = select(Department).where(Department.code == "GEN_MED", Department.hospital_id == hospital.id)
    gen_med_dept = db.scalars(stmt_gen_med).first()

    if mod_stream and gen_med_dept:
        stmt_wf = select(ClinicalWorkflow).where(ClinicalWorkflow.code == "MOD_GEN_MED_V1")
        wf_mod = db.scalars(stmt_wf).first()
        if not wf_mod:
            wf_mod = ClinicalWorkflow(
                id=uuid.uuid4(),
                medical_stream_id=mod_stream.id,
                department_id=gen_med_dept.id,
                name="General Medicine Clinical Intake Workflow",
                code="MOD_GEN_MED_V1",
                description="Comprehensive outpatient intake: chief complaint, onset, severity, fever, progression.",
                version="1.0.0",
                is_active=True,
            )
            db.add(wf_mod)
            db.flush()
            print(f"Created clinical workflow: {wf_mod.name} ({wf_mod.code})")

        # Questions for Modern Medicine
        mod_questions = [
            {
                "code": "q_001",
                "text": "What is your primary health concern or symptom today?",
                "type": "TEXT",
                "category": "CHIEF_COMPLAINT",
                "sequence": 1,
                "required": True,
            },
            {
                "code": "q_002",
                "text": "When did this symptom or discomfort start?",
                "type": "TEXT",
                "category": "ONSET",
                "sequence": 2,
                "required": True,
            },
            {
                "code": "q_003",
                "text": "How would you rate the severity of your discomfort on a scale of 1 (mild) to 10 (severe)?",
                "type": "NUMBER",
                "category": "SEVERITY",
                "sequence": 3,
                "required": True,
                "validation_rules": {"min": 1, "max": 10},
            },
            {
                "code": "q_004",
                "text": "Do you currently have a fever, chills, or elevated body temperature?",
                "type": "YES_NO",
                "category": "FEVER_CHECK",
                "sequence": 4,
                "required": True,
                "options": ["YES", "NO", "NOT SURE"],
            },
            {
                "code": "q_005",
                "text": "How has your condition progressed over the last 24 hours?",
                "type": "SINGLE_CHOICE",
                "category": "PROGRESSION",
                "sequence": 5,
                "required": True,
                "options": ["Getting Better", "Staying About the Same", "Getting Worse", "Fluctuating"],
            },
        ]

        for q_data in mod_questions:
            stmt_q = select(Question).where(
                Question.workflow_id == wf_mod.id,
                Question.question_code == q_data["code"],
                Question.language == "en",
            )
            q = db.scalars(stmt_q).first()
            if not q:
                q = Question(
                    id=uuid.uuid4(),
                    workflow_id=wf_mod.id,
                    question_code=q_data["code"],
                    question_text=q_data["text"],
                    question_type=q_data["type"],
                    category=q_data.get("category"),
                    sequence=q_data["sequence"],
                    is_required=q_data["required"],
                    language="en",
                    validation_rules=q_data.get("validation_rules"),
                    options=q_data.get("options"),
                )
                db.add(q)
                print(f"Created question: {q_data['code']} for workflow {wf_mod.code}")

    # 6b. AYUSH - Ayurveda Clinical Intake
    stmt_ayush_stream = select(MedicalStream).where(MedicalStream.code == "AYUSH")
    ayush_stream = db.scalars(stmt_ayush_stream).first()

    stmt_ayurveda_dept = select(Department).where(Department.code == "AYURVEDA", Department.hospital_id == hospital.id)
    ayurveda_dept = db.scalars(stmt_ayurveda_dept).first()

    if ayush_stream and ayurveda_dept:
        stmt_wf_ay = select(ClinicalWorkflow).where(ClinicalWorkflow.code == "AYUSH_AYURVEDA_V1")
        wf_ay = db.scalars(stmt_wf_ay).first()
        if not wf_ay:
            wf_ay = ClinicalWorkflow(
                id=uuid.uuid4(),
                medical_stream_id=ayush_stream.id,
                department_id=ayurveda_dept.id,
                name="Ayurvedic Holistic Intake Workflow",
                code="AYUSH_AYURVEDA_V1",
                description="Traditional Ayurvedic clinical assessment: chief complaint, Agni, Nidra, Vata/Pitta/Kapha symptoms.",
                version="1.0.0",
                is_active=True,
            )
            db.add(wf_ay)
            db.flush()
            print(f"Created clinical workflow: {wf_ay.name} ({wf_ay.code})")

        ay_questions = [
            {
                "code": "ay_001",
                "text": "What is the primary health issue or imbalance you are experiencing today?",
                "type": "TEXT",
                "category": "CHIEF_COMPLAINT",
                "sequence": 1,
                "required": True,
            },
            {
                "code": "ay_002",
                "text": "How is your digestive fire (Agni) and appetite?",
                "type": "SINGLE_CHOICE",
                "category": "AGNI",
                "sequence": 2,
                "required": True,
                "options": ["Good / Regular (Sama)", "Irregular / Variable (Visham)", "High / Burning (Tikshna)", "Low / Sluggish (Manda)"],
            },
            {
                "code": "ay_003",
                "text": "How many hours of restful sleep (Nidra) do you get per night on average?",
                "type": "NUMBER",
                "category": "NIDRA",
                "sequence": 3,
                "required": True,
                "validation_rules": {"min": 0, "max": 24},
            },
            {
                "code": "ay_004",
                "text": "Do you experience severe joint stiffness, dryness, or cracking sounds?",
                "type": "YES_NO",
                "category": "VATA_CHECK",
                "sequence": 4,
                "required": True,
                "options": ["YES", "NO", "NOT SURE"],
            },
        ]

        for q_data in ay_questions:
            stmt_q = select(Question).where(
                Question.workflow_id == wf_ay.id,
                Question.question_code == q_data["code"],
                Question.language == "en",
            )
            q = db.scalars(stmt_q).first()
            if not q:
                q = Question(
                    id=uuid.uuid4(),
                    workflow_id=wf_ay.id,
                    question_code=q_data["code"],
                    question_text=q_data["text"],
                    question_type=q_data["type"],
                    category=q_data.get("category"),
                    sequence=q_data["sequence"],
                    is_required=q_data["required"],
                    language="en",
                    validation_rules=q_data.get("validation_rules"),
                    options=q_data.get("options"),
                )
                db.add(q)
                print(f"Created question: {q_data['code']} for workflow {wf_ay.code}")

    db.commit()
    print("Database seeding completed successfully.")


if __name__ == "__main__":
    with SessionLocal() as session:
        seed_database(session)
