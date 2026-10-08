from uuid import uuid4

import pytest

from app.db.models import User, UserRole
from app.services.geo import haversine_km, postgis_available

# Search point in Pune.
LAT, LON = 18.52, 73.85

EXPECTED_KEYS = {
    'organization_id', 'organization_name', 'organization_type', 'description', 'address',
    'district', 'taluka', 'city_or_village', 'latitude', 'longitude', 'service_id',
    'service_name', 'service_type', 'service_description', 'eligibility',
    'contact_information', 'distance_km', 'is_verified',
}
FORBIDDEN_KEYS = {
    'child_id', 'child_name', 'family_id', 'family_name', 'home_location', 'guardian',
    'primary_guardian_user_id', 'health_records', 'protection_records',
    'private_migration_information', 'migration_history', 'password_hash', 'email', 'user_id',
}


def make_user(client, db_session, role):
    suffix = f'{uuid4().int % 10_000_000_000:010d}'
    payload = {
        'full_name': f'Test {role.title()}',
        'email': f'{role.lower()}-{suffix}@example.com',
        'mobile_number': f'+919{suffix[:9]}',
        'password': 'securepass123',
        'confirm_password': 'securepass123',
        'role': 'CITIZEN',
    }
    assert client.post('/api/v1/auth/register', json=payload).status_code == 201
    if role != 'CITIZEN':
        user = db_session.query(User).filter(User.email == payload['email']).one()
        user.role = UserRole(role)
        db_session.commit()
    login = client.post('/api/v1/auth/login', json={'identifier': payload['email'], 'password': payload['password']})
    assert login.status_code == 200, login.text
    return {'Authorization': f"Bearer {login.json()['access_token']}"}


@pytest.fixture()
def admin(client, db_session):
    return make_user(client, db_session, 'ADMIN')


@pytest.fixture()
def citizen(client, db_session):
    return make_user(client, db_session, 'CITIZEN')


def create_org(client, headers, **overrides):
    data = {
        'organization_name': 'DEMO Test Organization',
        'organization_type': 'SCHOOL',
        'district': 'Pune',
        'taluka': 'Haveli',
        'city_or_village': 'Pune',
        'latitude': 18.5210,
        'longitude': 73.8570,
    }
    data.update(overrides)
    response = client.post('/api/v1/organizations', headers=headers, json=data)
    assert response.status_code == 201, response.text
    return response.json()


def create_service(client, headers, organization_id, **overrides):
    data = {'service_name': 'Test service', 'service_type': 'EDUCATION'}
    data.update(overrides)
    response = client.post(f'/api/v1/organizations/{organization_id}/services', headers=headers, json=data)
    assert response.status_code == 201, response.text
    return response.json()


def nearby(client, headers, **params):
    query = {'latitude': LAT, 'longitude': LON}
    query.update(params)
    return client.get('/api/v1/services/nearby', headers=headers, params=query)


@pytest.fixture()
def three_places(client, admin):
    """Near (~0.1 km), mid (~8.6 km) and far (Mumbai, ~120 km) from the search point."""
    near = create_org(client, admin, organization_name='DEMO Near', latitude=18.5210, longitude=73.8570)
    mid = create_org(client, admin, organization_name='DEMO Mid', organization_type='HEALTHCARE',
                     latitude=18.5679, longitude=73.9143)
    far = create_org(client, admin, organization_name='DEMO Far', district='Mumbai', taluka='Mumbai City',
                     latitude=19.0760, longitude=72.8777)
    create_service(client, admin, near['id'], service_name='Near service', service_type='EDUCATION')
    create_service(client, admin, mid['id'], service_name='Mid service', service_type='HEALTHCARE')
    create_service(client, admin, far['id'], service_name='Far service', service_type='NUTRITION')
    return near, mid, far


# ------------------------------------------------------------------- distance math

def test_haversine_known_distances():
    assert haversine_km(18.52, 73.85, 18.52, 73.85) == pytest.approx(0.0, abs=1e-9)
    assert haversine_km(0, 0, 1, 0) == pytest.approx(111.195, abs=0.01)
    assert haversine_km(19.0760, 72.8777, 18.5204, 73.8567) == pytest.approx(120.2, abs=1.0)


def test_haversine_is_symmetric():
    a = haversine_km(19.0760, 72.8777, 18.5204, 73.8567)
    b = haversine_km(18.5204, 73.8567, 19.0760, 72.8777)
    assert a == pytest.approx(b)


def test_haversine_rejects_invalid_coordinates():
    with pytest.raises(ValueError):
        haversine_km(91, 0, 0, 0)
    with pytest.raises(ValueError):
        haversine_km(0, 181, 0, 0)


def test_postgis_not_required(db_session):
    # The test database is SQLite, so the PostGIS branch must report "unavailable".
    assert postgis_available(db_session) is False


# --------------------------------------------------------------------- discovery

def test_nearby_valid_coordinates(client, citizen, three_places):
    response = nearby(client, citizen, radius=10)
    assert response.status_code == 200, response.text
    names = [item['service_name'] for item in response.json()]
    assert names == ['Near service', 'Mid service']


def test_nearest_first(client, citizen, three_places):
    response = nearby(client, citizen, radius=500)
    assert response.status_code == 200
    items = response.json()
    assert [i['service_name'] for i in items] == ['Near service', 'Mid service', 'Far service']
    distances = [i['distance_km'] for i in items]
    assert distances == sorted(distances)
    assert distances[0] < 1
    assert 8 < distances[1] < 9.5
    assert 115 < distances[2] < 125


def test_default_radius_is_10_km(client, citizen, three_places):
    response = client.get('/api/v1/services/nearby', headers=citizen, params={'latitude': LAT, 'longitude': LON})
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_radius_filtering(client, citizen, three_places):
    assert len(nearby(client, citizen, radius=1).json()) == 1
    assert len(nearby(client, citizen, radius=5).json()) == 1
    assert len(nearby(client, citizen, radius=10).json()) == 2
    assert len(nearby(client, citizen, radius=200).json()) == 3


def test_service_type_filtering(client, citizen, three_places):
    response = nearby(client, citizen, radius=500, service_type='HEALTHCARE')
    assert [i['service_name'] for i in response.json()] == ['Mid service']


def test_district_filtering(client, citizen, three_places):
    response = nearby(client, citizen, radius=500, district='mumbai')
    assert [i['service_name'] for i in response.json()] == ['Far service']


def test_taluka_filtering(client, citizen, three_places):
    response = nearby(client, citizen, radius=500, taluka='Haveli')
    assert [i['service_name'] for i in response.json()] == ['Near service', 'Mid service']


def test_inactive_organization_excluded(client, admin, citizen, three_places):
    near, _, _ = three_places
    assert client.put(f"/api/v1/organizations/{near['id']}", headers=admin, json={'is_active': False}).status_code == 200
    names = [i['service_name'] for i in nearby(client, citizen, radius=10).json()]
    assert names == ['Mid service']


def test_inactive_service_excluded(client, admin, citizen):
    org = create_org(client, admin)
    keep = create_service(client, admin, org['id'], service_name='Keep')
    drop = create_service(client, admin, org['id'], service_name='Drop')
    response = client.put(f"/api/v1/organizations/{org['id']}/services/{drop['id']}", headers=admin,
                          json={'is_active': False})
    assert response.status_code == 200
    items = nearby(client, citizen, radius=10).json()
    assert [i['service_id'] for i in items] == [keep['id']]


def test_organization_without_coordinates_excluded(client, admin, citizen):
    org = create_org(client, admin, latitude=None, longitude=None)
    create_service(client, admin, org['id'])
    assert nearby(client, citizen, radius=500).json() == []


def test_empty_result_when_no_data(client, citizen):
    response = nearby(client, citizen)
    assert response.status_code == 200
    assert response.json() == []


# -------------------------------------------------------------------- validation

@pytest.mark.parametrize('lat', [90.5, -91])
def test_invalid_latitude_rejected(client, citizen, lat):
    assert nearby(client, citizen, latitude=lat).status_code == 422


@pytest.mark.parametrize('lon', [180.5, -181])
def test_invalid_longitude_rejected(client, citizen, lon):
    assert nearby(client, citizen, longitude=lon).status_code == 422


@pytest.mark.parametrize('radius', [0, -5, 501])
def test_invalid_radius_rejected(client, citizen, radius):
    assert nearby(client, citizen, radius=radius).status_code == 422


def test_missing_coordinates_rejected(client, citizen):
    assert client.get('/api/v1/services/nearby', headers=citizen).status_code == 422
    assert client.get('/api/v1/services/nearby', headers=citizen, params={'latitude': LAT}).status_code == 422


def test_invalid_service_type_rejected(client, citizen):
    assert nearby(client, citizen, service_type='BOGUS').status_code == 422


# ----------------------------------------------------------- privacy and access

def test_response_has_only_public_fields(client, citizen, three_places):
    items = nearby(client, citizen, radius=500).json()
    assert items
    for item in items:
        assert set(item.keys()) == EXPECTED_KEYS
        assert not (set(item.keys()) & FORBIDDEN_KEYS)


def test_search_does_not_need_child_or_family(client, citizen, three_places):
    # No child_id / family_id parameter exists, and supplying one changes nothing.
    response = nearby(client, citizen, radius=10, child_id=str(uuid4()), family_id=str(uuid4()))
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_citizen_can_use_nearby(client, citizen, three_places):
    assert nearby(client, citizen).status_code == 200


@pytest.mark.parametrize('role', ['SCHOOL', 'HEALTHCARE', 'NGO_WORKER', 'GOVERNMENT', 'ADMIN'])
def test_other_roles_can_use_nearby(client, db_session, three_places, role):
    headers = make_user(client, db_session, role)
    assert nearby(client, headers).status_code == 200


def test_unauthenticated_rejected(client):
    response = client.get('/api/v1/services/nearby', params={'latitude': LAT, 'longitude': LON})
    assert response.status_code in (401, 403)


def test_existing_services_endpoint_unchanged(client, citizen, three_places):
    response = client.get('/api/v1/services', headers=citizen)
    assert response.status_code == 200
    assert len(response.json()) == 3