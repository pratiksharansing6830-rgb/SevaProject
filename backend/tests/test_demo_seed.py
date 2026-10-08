from uuid import uuid4

import pytest

from app.db.directory_models import Organization, Service, ServiceType
from app.services.demo_seed import PLACES, build_plan, remove_demo_directory, seed_demo_directory

FORBIDDEN_KEYS = {
    'child_id', 'child_name', 'family_id', 'family_name', 'home_location', 'guardian',
    'primary_guardian_user_id', 'health_records', 'protection_records',
    'private_migration_information', 'migration_history', 'password_hash', 'user_id',
}
REQUIRED_SERVICE_TYPES = {
    'EDUCATION', 'HEALTHCARE', 'NUTRITION', 'PROTECTION', 'CHILD_SUPPORT', 'WELLBEING',
    'INCLUSION', 'GOVERNMENT_SCHEME', 'SOCIAL_SUPPORT', 'DOCUMENTATION', 'HOUSING_SUPPORT',
}


def centre(city):
    place = next(item for item in PLACES if item.city == city)
    return place.latitude, place.longitude


@pytest.fixture()
def citizen(client):
    suffix = f'{uuid4().int % 10_000_000_000:010d}'
    payload = {
        'full_name': 'Demo Citizen',
        'email': f'citizen-{suffix}@example.com',
        'mobile_number': f'+919{suffix[:9]}',
        'password': 'securepass123',
        'confirm_password': 'securepass123',
        'role': 'CITIZEN',
    }
    assert client.post('/api/v1/auth/register', json=payload).status_code == 201
    login = client.post('/api/v1/auth/login', json={'identifier': payload['email'], 'password': payload['password']})
    assert login.status_code == 200, login.text
    return {'Authorization': f"Bearer {login.json()['access_token']}"}


def nearby(client, headers, city, service_type, radius=10):
    lat, lon = centre(city)
    return client.get(
        '/api/v1/services/nearby',
        headers=headers,
        params={'latitude': lat, 'longitude': lon, 'radius': radius, 'service_type': service_type},
    )


def test_seed_runs(db_session):
    result = seed_demo_directory(db_session)
    assert result['created_organizations'] == len(build_plan())
    assert result['created_services'] == sum(len(item['services']) for item in build_plan())


def test_repeated_seed_creates_no_duplicates(db_session):
    seed_demo_directory(db_session)
    orgs = db_session.query(Organization).count()
    services = db_session.query(Service).count()
    again = seed_demo_directory(db_session)
    assert again == {'created_organizations': 0, 'created_services': 0}
    assert db_session.query(Organization).count() == orgs
    assert db_session.query(Service).count() == services


def test_all_demo_organizations_are_unverified_active_and_marked_demo(db_session):
    seed_demo_directory(db_session)
    organizations = db_session.query(Organization).all()
    assert organizations
    for org in organizations:
        assert org.is_verified is False
        assert org.is_active is True
        assert 'DEMO' in org.organization_name
        assert org.contact_email.endswith('@demo.example')


def test_all_required_service_types_exist(db_session):
    seed_demo_directory(db_session)
    present = {row.service_type for row in db_session.query(Service).all()}
    assert REQUIRED_SERVICE_TYPES <= present
    assert present <= {item.value for item in ServiceType}


def test_all_destination_and_origin_places_are_covered(db_session):
    seed_demo_directory(db_session)
    cities = {row.city_or_village for row in db_session.query(Organization).all()}
    assert cities == {place.city for place in PLACES}


def test_nearby_search_returns_demo_services_nearest_first(client, db_session, citizen):
    seed_demo_directory(db_session)
    response = nearby(client, citizen, 'Pune', 'EDUCATION')
    assert response.status_code == 200, response.text
    items = response.json()
    assert items
    assert all('DEMO' in item['organization_name'] for item in items)
    assert all(item['service_type'] == 'EDUCATION' for item in items)
    assert all(item['is_verified'] is False for item in items)
    distances = [item['distance_km'] for item in items]
    assert distances == sorted(distances)


@pytest.mark.parametrize(
    'city,service_type',
    [
        ('Pune', 'EDUCATION'),
        ('Nashik', 'HEALTHCARE'),
        ('Bhiwandi', 'NUTRITION'),
        ('Mumbai', 'CHILD_SUPPORT'),
        ('Pimpri-Chinchwad', 'INCLUSION'),
    ],
)
def test_demo_scenario_destinations_find_the_right_service(client, db_session, citizen, city, service_type):
    seed_demo_directory(db_session)
    response = nearby(client, citizen, city, service_type)
    assert response.status_code == 200, response.text
    items = response.json()
    assert items, f'no {service_type} demo service near {city}'
    assert all(item['service_type'] == service_type for item in items)
    assert all(item['city_or_village'] == city for item in items)


def test_service_type_filter_excludes_other_types(client, db_session, citizen):
    seed_demo_directory(db_session)
    response = nearby(client, citizen, 'Pune', 'HEALTHCARE')
    assert {item['service_type'] for item in response.json()} == {'HEALTHCARE'}


def test_demo_nearby_response_has_no_private_fields(client, db_session, citizen):
    seed_demo_directory(db_session)
    items = nearby(client, citizen, 'Pune', 'EDUCATION').json()
    assert items
    for item in items:
        assert not (set(item.keys()) & FORBIDDEN_KEYS)


def test_remove_only_deletes_demo_records(db_session):
    seed_demo_directory(db_session)
    db_session.add(Organization(organization_name='Real Looking Org', organization_type='OTHER'))
    db_session.commit()
    remove_demo_directory(db_session)
    names = [org.organization_name for org in db_session.query(Organization).all()]
    assert names == ['Real Looking Org']