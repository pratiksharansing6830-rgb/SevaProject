from datetime import date

from sqlalchemy.orm import Session

from app.db.continuity_models import (
    Child,
    ChildProtectionRecord,
    EducationRecord,
    Family,
    FamilyMember,
    HealthcareContinuity,
    InclusionRecord,
    MigrationRecord,
    NutritionRecord,
    WellBeingRecord,
)
from app.db.database import SessionLocal
from app.db.models import User, UserRole
from app.services.continuity import refresh_child_continuity


def years_ago(years: int) -> date:
    today = date.today()
    return today.replace(year=today.year - years)


def seed(db: Session) -> str:
    existing = db.query(Family).filter(Family.family_name == 'DEMO DATA - Demo Migrant Family').first()
    if existing:
        return f'Demo family already exists: {existing.family_reference_id}'
    guardian = db.query(User).filter(User.role == UserRole.CITIZEN, User.is_active.is_(True)).first()
    if guardian is None:
        return 'Create a citizen account before running the demo seed.'

    family = Family(
        family_reference_id='DEMO-' + guardian.id.hex[:10].upper(),
        primary_guardian_user_id=guardian.id,
        family_name='DEMO DATA - Demo Migrant Family',
        contact_mobile=guardian.mobile_number,
        current_district='Pune',
        current_taluka='Haveli',
        current_village_or_city='Pune City',
        preferred_language='Marathi',
    )
    db.add(family)
    db.flush()
    db.add(FamilyMember(family_id=family.id, user_id=guardian.id, relationship_type='GUARDIAN'))
    migration = MigrationRecord(
        family_id=family.id,
        from_district='Nashik',
        from_taluka='Nashik',
        from_location='Nashik City',
        to_district='Pune',
        to_taluka='Haveli',
        to_location='Pune City',
        migration_date=date.today(),
        migration_reason='Seasonal work',
        status='ACTIVE',
    )
    db.add(migration)
    db.flush()

    children = [
        Child(family_id=family.id, first_name='Aarav', last_name='Demo', date_of_birth=years_ago(12), gender='UNDISCLOSED', education_status='ENROLLED', current_class='7', preferred_language='Marathi'),
        Child(family_id=family.id, first_name='Mira', last_name='Demo', date_of_birth=years_ago(8), gender='UNDISCLOSED', education_status='PENDING', current_class='3', preferred_language='Marathi'),
    ]
    db.add_all(children)
    db.flush()
    for child in children:
        db.add(FamilyMember(family_id=family.id, child_id=child.id, relationship_type='CHILD'))

    first_child = children[0]
    db.add_all([
        EducationRecord(child_id=first_child.id, current_school_name='Pune Community School', current_school_location='Pune', current_class='7', enrollment_status='ENROLLED', transfer_status='COMPLETED'),
        HealthcareContinuity(child_id=first_child.id, healthcare_provider_name='Community Health Centre', healthcare_location='Pune', continuity_status='FOLLOW_UP_RECOMMENDED'),
        NutritionRecord(child_id=first_child.id, nutrition_service_name='Community Nutrition Centre', nutrition_service_location='Pune', service_status='CONNECTED'),
        ChildProtectionRecord(child_id=first_child.id, protection_status='REVIEW_REQUIRED', support_contact_available=True, followup_required=True),
        WellBeingRecord(child_id=first_child.id, support_status='PENDING'),
        InclusionRecord(child_id=first_child.id, requirement_present=False, support_type='OTHER', support_status='CONNECTED'),
    ])
    db.flush()
    for child in children:
        refresh_child_continuity(db, child, migration)
    db.commit()
    return f'DEMO DATA seeded: {family.family_reference_id}'


if __name__ == '__main__':
    with SessionLocal() as session:
        print(seed(session))