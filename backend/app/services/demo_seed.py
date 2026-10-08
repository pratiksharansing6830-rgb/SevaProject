"""Fictional DEMO directory data for Sahaayak (Part 4.5).

Every organization here is FICTIONAL, is_verified = False, and has "— DEMO" in its name.
Coordinates are approximate city-centre points plus a small offset; they represent service
locations only. No family home coordinates exist anywhere in this data.
Safe to run repeatedly: records are matched by deterministic names and never duplicated.
"""
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.db.directory_models import Organization, Service

DEMO_SUFFIX = '— DEMO'
DEMO_DOMAIN = 'demo.example'
FICTIONAL_NOTE = 'This is a fictional DEMO record for demonstrating the platform. It is not a real institution.'


@dataclass(frozen=True)
class Place:
    city: str
    district: str
    taluka: str
    latitude: float
    longitude: float
    kind: str  # 'destination' or 'origin'


PLACES: tuple[Place, ...] = (
    # Destination / work regions
    Place('Mumbai', 'Mumbai', 'Mumbai City', 19.0760, 72.8777, 'destination'),
    Place('Thane', 'Thane', 'Thane', 19.2183, 72.9781, 'destination'),
    Place('Bhiwandi', 'Thane', 'Bhiwandi', 19.2967, 73.0631, 'destination'),
    Place('Pune', 'Pune', 'Pune City', 18.5204, 73.8567, 'destination'),
    Place('Pimpri-Chinchwad', 'Pune', 'Haveli', 18.6298, 73.7997, 'destination'),
    Place('Nashik', 'Nashik', 'Nashik', 19.9975, 73.7898, 'destination'),
    Place('Malegaon', 'Nashik', 'Malegaon', 20.5579, 74.5089, 'destination'),
    Place('Ahilyanagar', 'Ahilyanagar', 'Ahilyanagar', 19.0948, 74.7480, 'destination'),
    # Seasonal / origin districts
    Place('Beed', 'Beed', 'Beed', 18.9890, 75.7600, 'origin'),
    Place('Dharashiv', 'Dharashiv', 'Dharashiv', 18.1860, 76.0419, 'origin'),
    Place('Latur', 'Latur', 'Latur', 18.4088, 76.5604, 'origin'),
    Place('Parbhani', 'Parbhani', 'Parbhani', 19.2704, 76.7747, 'origin'),
    Place('Nanded', 'Nanded', 'Nanded', 19.1383, 77.3210, 'origin'),
    Place('Jalna', 'Jalna', 'Jalna', 19.8347, 75.8816, 'origin'),
    Place('Solapur', 'Solapur', 'Solapur', 17.6599, 75.9064, 'origin'),
)

# (service_name, service_type, description, eligibility)
ServiceSpec = tuple[str, str, str, str]


@dataclass(frozen=True)
class Template:
    slug: str
    name: str
    organization_type: str
    description: str
    offset: tuple[float, float]  # degrees (lat, lon) from the city centre; ~1 km per 0.009
    services: tuple[ServiceSpec, ...]


TEMPLATES: tuple[Template, ...] = (
    Template(
        'education', 'Migrant Child Education Support Centre', 'SCHOOL',
        'Helps children of seasonal workers continue schooling after moving.',
        (0.006, 0.004),
        (('Migrant Child Admission and Bridge Classes', 'EDUCATION',
          'Admission guidance, record transfer help and bridge classes.',
          'Children of seasonal or migrant worker families.'),),
    ),
    Template(
        'healthcare', 'Seasonal Worker Child Health Centre', 'HEALTHCARE',
        'Child health check-ups and follow-up for families who recently moved.',
        (-0.008, 0.006),
        (('Child Health Check-up and Immunisation Follow-up', 'HEALTHCARE',
          'Check-ups and help continuing immunisation schedules.',
          'Children in seasonal or migrant worker families.'),),
    ),
    Template(
        'nutrition', 'Migrant Child Nutrition Support Centre', 'NUTRITION_CENTER',
        'Nutrition support linkage for children while families are away from home.',
        (0.010, -0.007),
        (('Child Nutrition Support and Meal Linkage', 'NUTRITION',
          'Connects children to local nutrition and meal programmes.',
          'Children under 14 in migrating families.'),),
    ),
    Template(
        'protection', 'Child Protection & Safe Migration Centre', 'CHILD_SUPPORT',
        'Child safety follow-up and safe-migration counselling for families.',
        (-0.004, -0.010),
        (('Child Protection Follow-up', 'PROTECTION',
          'Follow-up support where a protection review is recommended.',
          'Children flagged for follow-up by authorised staff.'),
         ('Child Support and Safe Migration Counselling', 'CHILD_SUPPORT',
          'Counselling and referral for children and guardians.',
          'Any child or guardian in a migrating family.')),
    ),
    Template(
        'inclusion', 'Migrant Children Inclusion Support Centre', 'DISABILITY_SUPPORT',
        'Learning and accessibility support for children with additional needs.',
        (0.015, 0.012),
        (('Inclusion and Learning Support', 'INCLUSION',
          'Accessibility, learning and communication support.',
          'Children with disability or inclusion requirements.'),),
    ),
    Template(
        'documentation', 'Family Documentation Help Centre', 'COMMUNITY_SERVICE',
        'Help with documents and information about welfare schemes.',
        (-0.012, -0.004),
        (('Document Assistance Desk', 'DOCUMENTATION',
          'Help preparing and transferring family documents.',
          'Seasonal or migrant worker families.'),
         ('Welfare Scheme Information Desk', 'GOVERNMENT_SCHEME',
          'Information about schemes families may apply for.',
          'Seasonal or migrant worker families.')),
    ),
    Template(
        'family-support', 'Seasonal Worker Family Support Centre', 'NGO',
        'Social, well-being and temporary housing information for working families.',
        (0.003, -0.015),
        (('Family Social Support Desk', 'SOCIAL_SUPPORT',
          'General social support and referrals.', 'Seasonal worker families.'),
         ('Child and Family Well-being Support', 'WELLBEING',
          'Counselling and well-being support.', 'Children and guardians.'),
         ('Temporary Housing Information Desk', 'HOUSING_SUPPORT',
          'Information on temporary housing options.', 'Seasonal worker families.')),
    ),
)

# Origin districts get a smaller set of centres.
ORIGIN_TEMPLATE_SLUGS = frozenset({'education', 'healthcare', 'family-support'})


def build_plan() -> list[dict]:
    plan: list[dict] = []
    counter = 0
    for place in PLACES:
        for template in TEMPLATES:
            if place.kind == 'origin' and template.slug not in ORIGIN_TEMPLATE_SLUGS:
                continue
            counter += 1
            city_slug = place.city.lower().replace(' ', '-')
            slug = f'{template.slug}-{city_slug}'
            phone = f'+91 00000 {counter:05d}'
            email = f'{slug}@{DEMO_DOMAIN}'
            organization = {
                'organization_name': f'{template.name} {DEMO_SUFFIX}, {place.city}',
                'organization_type': template.organization_type,
                'description': f'DEMO (fictional): {template.description} {FICTIONAL_NOTE}',
                'contact_phone': phone,
                'contact_email': email,
                'website': f'https://{DEMO_DOMAIN}/{slug}',
                'address': f'DEMO address {counter}, Fictional Lane, {place.city}',
                'district': place.district,
                'taluka': place.taluka,
                'city_or_village': place.city,
                'latitude': round(place.latitude + template.offset[0], 5),
                'longitude': round(place.longitude + template.offset[1], 5),
                'is_verified': False,
                'is_active': True,
            }
            services = [
                {
                    'service_name': name,
                    'service_type': service_type,
                    'description': f'DEMO (fictional): {description}',
                    'eligibility': eligibility,
                    'contact_information': f'DEMO contact only: {phone}, {email}',
                    'is_active': True,
                }
                for name, service_type, description, eligibility in template.services
            ]
            plan.append({'organization': organization, 'services': services})
    return plan


def seed_demo_directory(db: Session) -> dict[str, int]:
    """Create missing DEMO organizations/services. Existing ones are left exactly as they are."""
    created_organizations = 0
    created_services = 0
    for item in build_plan():
        data = item['organization']
        organization = (
            db.query(Organization).filter(Organization.organization_name == data['organization_name']).first()
        )
        if organization is None:
            organization = Organization(**data)
            db.add(organization)
            db.flush()
            created_organizations += 1
        for service_data in item['services']:
            exists = (
                db.query(Service)
                .filter(Service.organization_id == organization.id, Service.service_name == service_data['service_name'])
                .first()
            )
            if exists is None:
                db.add(Service(organization_id=organization.id, **service_data))
                created_services += 1
    db.commit()
    return {'created_organizations': created_organizations, 'created_services': created_services}


def remove_demo_directory(db: Session) -> dict[str, int]:
    """Delete only records whose organization name carries the DEMO marker."""
    organizations = db.query(Organization).filter(Organization.organization_name.like(f'%{DEMO_SUFFIX}%')).all()
    ids = [organization.id for organization in organizations]
    removed_services = 0
    if ids:
        removed_services = db.query(Service).filter(Service.organization_id.in_(ids)).delete(synchronize_session=False)
        db.query(Organization).filter(Organization.id.in_(ids)).delete(synchronize_session=False)
    db.commit()
    return {'removed_organizations': len(ids), 'removed_services': removed_services}