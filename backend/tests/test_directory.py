from uuid import uuid4

import pytest

from app.db.models import User, UserRole

FORBIDDEN_KEYS = {
    'child_id', 'child_name', 'family_id', 'family_name', 'home_location',
    'health_records', 'protection_records', 'private_migration_information',
}


def make_user(client, db_session, role):
    """Register as CITIZEN, set the role directly in the DB, then log in for a fresh token."""
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


def org_payload(**overrides):
    data = {
        'organization_name': 'DEMO Beed Primary School',
        'organization_type': 'SCHOOL',
        'district': 'Beed',
        'taluka': 'Beed',
        'city_or_village': 'Beed',
        'latitude': 18.99,
        'longitude': 75.76,
        'contact_email': 'demo@example.org',
        'website': 'https://example.org',
    }
    data.update(overrides)
    return data


def create_org(client, headers, **overrides):
    response = client.post('/api/v1/organizations', headers=headers, json=org_payload(**overrides))
    assert response.status_code == 201, response.text
    return response.json()


def create_service(client, headers, organization_id, **overrides):
    data = {'service_name': 'Admission support', 'service_type': 'EDUCATION'}
    data.update(overrides)
    response = client.post(f'/api/v1/organizations/{organization_id}/services', headers=headers, json=data)
    assert response.status_code == 201, response.text
    return response.json()


def all_keys(obj):
    if isinstance(obj, dict):
        for key, value in obj.items():
            yield key
            yield from all_keys(value)
    elif isinstance(obj, list):
        for item in obj:
            yield from all_keys(item)


# ------------------------------------------------------------------ organization

def test_create_organization_defaults(client, admin):
    org = create_org(client, admin)
    assert org['is_active'] is True
    assert org['is_verified'] is False
    assert org['organization_type'] == 'SCHOOL'


def test_get_organizations(client, admin, citizen):
    create_org(client, admin)
    response = client.get('/api/v1/organizations', headers=citizen)
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_filter_organizations(client, admin, citizen):
    create_org(client, admin)
    create_org(client, admin, organization_name='DEMO Pune Clinic', organization_type='HEALTHCARE',
               district='Pune', taluka='Haveli', city_or_village='Pune', is_verified=True)
    get = lambda q: client.get(f'/api/v1/organizations{q}', headers=citizen).json()
    assert len(get('?organization_type=HEALTHCARE')) == 1
    assert len(get('?district=beed')) == 1
    assert len(get('?taluka=Haveli')) == 1
    assert len(get('?city_or_village=Pune')) == 1
    assert len(get('?is_verified=true')) == 1
    assert len(get('?is_verified=false')) == 1


def test_update_organization(client, admin):
    org = create_org(client, admin)
    response = client.put(f"/api/v1/organizations/{org['id']}", headers=admin,
                          json={'organization_name': 'DEMO Renamed', 'is_verified': True})
    assert response.status_code == 200
    assert response.json()['organization_name'] == 'DEMO Renamed'
    assert response.json()['is_verified'] is True


def test_update_unknown_organization_404(client, admin):
    response = client.put(f'/api/v1/organizations/{uuid4()}', headers=admin, json={'description': 'x'})
    assert response.status_code == 404


def test_update_rejects_null_required_field(client, admin):
    org = create_org(client, admin)
    response = client.put(f"/api/v1/organizations/{org['id']}", headers=admin, json={'organization_name': None})
    assert response.status_code == 422


def test_inactive_organization_hidden(client, admin, citizen):
    org = create_org(client, admin)
    create_service(client, admin, org['id'])
    assert client.put(f"/api/v1/organizations/{org['id']}", headers=admin, json={'is_active': False}).status_code == 200
    assert client.get('/api/v1/organizations', headers=citizen).json() == []
    assert client.get('/api/v1/services', headers=citizen).json() == []
    assert client.get(f"/api/v1/organizations/{org['id']}/services", headers=citizen).status_code == 404


@pytest.mark.parametrize('lat', [90.5, -91])
def test_invalid_latitude(client, admin, lat):
    response = client.post('/api/v1/organizations', headers=admin, json=org_payload(latitude=lat))
    assert response.status_code == 422


@pytest.mark.parametrize('lon', [180.5, -181])
def test_invalid_longitude(client, admin, lon):
    response = client.post('/api/v1/organizations', headers=admin, json=org_payload(longitude=lon))
    assert response.status_code == 422


def test_invalid_email_website_and_type(client, admin):
    assert client.post('/api/v1/organizations', headers=admin, json=org_payload(contact_email='nope')).status_code == 422
    assert client.post('/api/v1/organizations', headers=admin, json=org_payload(website='ftp://x')).status_code == 422
    assert client.post('/api/v1/organizations', headers=admin, json=org_payload(organization_type='BOGUS')).status_code == 422
    bad = org_payload()
    del bad['organization_name']
    assert client.post('/api/v1/organizations', headers=admin, json=bad).status_code == 422


# ----------------------------------------------------------------------- service

def test_create_and_get_services(client, admin, citizen):
    org = create_org(client, admin)
    service = create_service(client, admin, org['id'])
    assert service['organization_id'] == org['id']
    assert service['organization']['district'] == 'Beed'
    listed = client.get('/api/v1/services', headers=citizen)
    assert listed.status_code == 200
    assert len(listed.json()) == 1


def test_filter_services(client, admin, citizen):
    beed = create_org(client, admin)
    pune = create_org(client, admin, organization_name='DEMO Pune Clinic', organization_type='HEALTHCARE',
                      district='Pune', taluka='Haveli')
    create_service(client, admin, beed['id'])
    create_service(client, admin, pune['id'], service_name='Checkups', service_type='HEALTHCARE')
    get = lambda q: client.get(f'/api/v1/services{q}', headers=citizen).json()
    assert len(get('?service_type=HEALTHCARE')) == 1
    assert len(get('?district=Pune')) == 1
    assert len(get('?taluka=Beed')) == 1
    assert len(get(f"?organization_id={beed['id']}")) == 1


def test_services_by_organization(client, admin, citizen):
    a = create_org(client, admin)
    b = create_org(client, admin, organization_name='DEMO Other')
    create_service(client, admin, a['id'])
    create_service(client, admin, b['id'], service_name='Other service')
    response = client.get(f"/api/v1/organizations/{a['id']}/services", headers=citizen)
    assert response.status_code == 200
    assert [s['service_name'] for s in response.json()] == ['Admission support']


def test_update_service(client, admin):
    org = create_org(client, admin)
    service = create_service(client, admin, org['id'])
    response = client.put(f"/api/v1/organizations/{org['id']}/services/{service['id']}", headers=admin,
                          json={'service_name': 'Updated', 'is_active': False})
    assert response.status_code == 200
    assert response.json()['service_name'] == 'Updated'
    assert response.json()['is_active'] is False


def test_create_service_unknown_organization(client, admin):
    response = client.post(f'/api/v1/organizations/{uuid4()}/services', headers=admin,
                           json={'service_name': 'X', 'service_type': 'OTHER'})
    assert response.status_code == 404


def test_service_cannot_be_updated_through_wrong_organization(client, admin):
    a = create_org(client, admin)
    b = create_org(client, admin, organization_name='DEMO Other')
    service = create_service(client, admin, a['id'])
    response = client.put(f"/api/v1/organizations/{b['id']}/services/{service['id']}", headers=admin,
                          json={'service_name': 'Hijacked'})
    assert response.status_code == 404
    unchanged = client.get(f"/api/v1/organizations/{a['id']}/services", headers=admin).json()
    assert unchanged[0]['service_name'] == 'Admission support'


# ------------------------------------------------------------------ authorization

def test_citizen_can_read_but_not_manage(client, admin, citizen):
    org = create_org(client, admin)
    service = create_service(client, admin, org['id'])
    assert client.get('/api/v1/organizations', headers=citizen).status_code == 200
    assert client.get('/api/v1/services', headers=citizen).status_code == 200
    assert client.post('/api/v1/organizations', headers=citizen, json=org_payload()).status_code == 403
    assert client.put(f"/api/v1/organizations/{org['id']}", headers=citizen, json={'description': 'x'}).status_code == 403
    assert client.post(f"/api/v1/organizations/{org['id']}/services", headers=citizen,
                       json={'service_name': 'X', 'service_type': 'OTHER'}).status_code == 403
    assert client.put(f"/api/v1/organizations/{org['id']}/services/{service['id']}", headers=citizen,
                      json={'service_name': 'X'}).status_code == 403


@pytest.mark.parametrize('role', ['SCHOOL', 'HEALTHCARE', 'NGO_WORKER', 'GOVERNMENT'])
def test_other_roles_read_only(client, db_session, admin, role):
    headers = make_user(client, db_session, role)
    org = create_org(client, admin)
    assert client.get('/api/v1/organizations', headers=headers).status_code == 200
    assert client.get('/api/v1/services', headers=headers).status_code == 200
    assert client.post('/api/v1/organizations', headers=headers, json=org_payload()).status_code == 403
    assert client.put(f"/api/v1/organizations/{org['id']}", headers=headers, json={'description': 'x'}).status_code == 403


def test_unauthenticated_cannot_read(client):
    assert client.get('/api/v1/organizations').status_code in (401, 403)
    assert client.get('/api/v1/services').status_code in (401, 403)


# ----------------------------------------------------------------------- privacy

def test_responses_contain_no_private_fields(client, admin, citizen):
    org = create_org(client, admin)
    create_service(client, admin, org['id'])
    responses = [
        client.get('/api/v1/organizations', headers=citizen).json(),
        client.get('/api/v1/services', headers=citizen).json(),
        client.get(f"/api/v1/organizations/{org['id']}/services", headers=citizen).json(),
    ]
    for body in responses:
        assert not (set(all_keys(body)) & FORBIDDEN_KEYS)