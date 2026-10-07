from datetime import date
from uuid import UUID, uuid4

import pytest

from app.db.continuity_models import FamilyAccess
from app.db.models import User
from app.core.security import create_access_token


def register_user(client, role='CITIZEN'):
    suffix = f'{uuid4().int % 10_000_000_000:010d}'
    payload = {
        'full_name': f'Test {role.title()}',
        'email': f'{role.lower()}-{suffix}@example.com',
        'mobile_number': f'+919{suffix[:9]}',
        'password': 'securepass123',
        'confirm_password': 'securepass123',
        'role': role,
    }
    registered = client.post('/api/v1/auth/register', json=payload)
    assert registered.status_code == 201, registered.text
    login = client.post('/api/v1/auth/login', json={'identifier': payload['email'], 'password': payload['password']})
    assert login.status_code == 200, login.text
    return {'Authorization': f"Bearer {login.json()['access_token']}"}, registered.json()


def create_family(client, headers, family_name='Sample Family'):
    response = client.post('/api/v1/families', headers=headers, json={
        'family_name': family_name,
        'contact_mobile': '+919876543210',
        'current_district': 'Pune',
        'current_taluka': 'Haveli',
        'current_village_or_city': 'Pune City',
        'preferred_language': 'Marathi',
    })
    assert response.status_code == 201, response.text
    return response.json()


def create_child(client, headers, family_id):
    response = client.post(f'/api/v1/families/{family_id}/children', headers=headers, json={
        'first_name': 'Aarav',
        'last_name': 'Patil',
        'date_of_birth': '2014-03-12',
        'gender': 'UNDISCLOSED',
        'current_class': '7',
        'education_status': 'PENDING',
    })
    assert response.status_code == 201, response.text
    return response.json()


def test_family_create_and_get_own(client):
    headers, _ = register_user(client)
    family = create_family(client, headers)
    response = client.get(f"/api/v1/families/{family['id']}", headers=headers)
    assert response.status_code == 200
    assert response.json()['family_reference_id'].startswith('SAH-')


def test_citizen_cannot_view_another_family(client):
    owner_headers, _ = register_user(client)
    other_headers, _ = register_user(client)
    family = create_family(client, owner_headers)
    response = client.get(f"/api/v1/families/{family['id']}", headers=other_headers)
    assert response.status_code == 403


def test_family_requires_authentication(client):
    response = client.get('/api/v1/families')
    assert response.status_code == 401


def test_family_validation_rejects_short_mobile(client):
    headers, _ = register_user(client)
    response = client.post('/api/v1/families', headers=headers, json={
        'family_name': 'Family', 'contact_mobile': '123', 'current_district': 'Pune',
        'current_taluka': 'Haveli', 'current_village_or_city': 'Pune',
    })
    assert response.status_code == 422


def test_child_create_and_get(client):
    headers, _ = register_user(client)
    family = create_family(client, headers)
    child = create_child(client, headers, family['id'])
    response = client.get(f"/api/v1/children/{child['id']}", headers=headers)
    assert response.status_code == 200
    assert response.json()['first_name'] == 'Aarav'


def test_citizen_cannot_view_another_familys_child(client):
    owner_headers, _ = register_user(client)
    other_headers, _ = register_user(client)
    family = create_family(client, owner_headers)
    child = create_child(client, owner_headers, family['id'])
    response = client.get(f"/api/v1/children/{child['id']}", headers=other_headers)
    assert response.status_code == 403


def test_migration_creation_generates_continuity_and_followups(client):
    headers, _ = register_user(client)
    family = create_family(client, headers)
    child = create_child(client, headers, family['id'])
    response = client.post(f"/api/v1/families/{family['id']}/migrations", headers=headers, json={
        'from_district': 'Nashik', 'from_taluka': 'Nashik', 'from_location': 'Nashik City',
        'to_district': 'Pune', 'to_taluka': 'Haveli', 'to_location': 'Pune City',
        'migration_date': '2026-10-07', 'status': 'ACTIVE',
    })
    assert response.status_code == 201, response.text
    continuity = client.get(f"/api/v1/children/{child['id']}/continuity", headers=headers)
    assert continuity.status_code == 200
    assert len(continuity.json()['services']) == 6
    assert continuity.json()['overall_status'] == 'FOLLOW_UP_RECOMMENDED'
    followups = client.get(f"/api/v1/families/{family['id']}/followups", headers=headers)
    assert len(followups.json()) == 6


def test_migration_list_is_family_scoped(client):
    headers, _ = register_user(client)
    family = create_family(client, headers)
    response = client.get(f"/api/v1/families/{family['id']}/migrations", headers=headers)
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.parametrize(('service', 'payload', 'expected_status'), [
    ('education', {'enrollment_status': 'ENROLLED', 'transfer_status': 'COMPLETED', 'current_class': '7'}, 201),
    ('healthcare', {'continuity_status': 'CONNECTED'}, 201),
    ('nutrition', {'service_status': 'CONNECTED'}, 201),
    ('wellbeing', {'support_status': 'CONNECTED'}, 201),
    ('protection', {'protection_status': 'SUPPORT_CONNECTED', 'support_contact_available': True}, 201),
    ('inclusion', {'requirement_present': True, 'support_type': 'LEARNING_SUPPORT', 'support_status': 'CONNECTED'}, 201),
])
def test_service_record_create_and_read(client, service, payload, expected_status):
    headers, _ = register_user(client)
    family = create_family(client, headers)
    child = create_child(client, headers, family['id'])
    created = client.post(f"/api/v1/children/{child['id']}/{service}", headers=headers, json=payload)
    assert created.status_code == expected_status, created.text
    fetched = client.get(f"/api/v1/children/{child['id']}/{service}", headers=headers)
    assert fetched.status_code == 200
    assert fetched.json()['child_id'] == child['id']


def test_missing_services_are_pending(client):
    headers, _ = register_user(client)
    family = create_family(client, headers)
    child = create_child(client, headers, family['id'])
    checked = client.post(f"/api/v1/children/{child['id']}/continuity/check", headers=headers)
    assert checked.status_code == 200
    assert {record['status'] for record in checked.json()} == {'PENDING'}


def test_pending_education_recommends_followup(client):
    headers, _ = register_user(client)
    family = create_family(client, headers)
    child = create_child(client, headers, family['id'])
    client.post(f"/api/v1/children/{child['id']}/education", headers=headers, json={
        'enrollment_status': 'ENROLLED', 'transfer_status': 'PENDING',
    })
    summary = client.get(f"/api/v1/children/{child['id']}/continuity", headers=headers).json()
    education = next(record for record in summary['services'] if record['service_type'] == 'EDUCATION')
    assert education['status'] == 'FOLLOW_UP_RECOMMENDED'


def test_protection_followup_is_human_review_required(client):
    headers, _ = register_user(client)
    family = create_family(client, headers)
    child = create_child(client, headers, family['id'])
    client.post(f"/api/v1/children/{child['id']}/protection", headers=headers, json={
        'protection_status': 'REVIEW_REQUIRED', 'followup_required': True,
    })
    summary = client.get(f"/api/v1/children/{child['id']}/continuity", headers=headers).json()
    protection = next(record for record in summary['services'] if record['service_type'] == 'PROTECTION')
    assert protection['status'] == 'REVIEW_REQUIRED'
    assert summary['overall_status'] == 'REVIEW_REQUIRED'


def test_all_connected_services_return_connected_summary(client):
    headers, _ = register_user(client)
    family = create_family(client, headers)
    child = create_child(client, headers, family['id'])
    records = {
        'education': {'enrollment_status': 'ENROLLED', 'transfer_status': 'COMPLETED'},
        'healthcare': {'continuity_status': 'CONNECTED'},
        'nutrition': {'service_status': 'CONNECTED'},
        'wellbeing': {'support_status': 'CONNECTED'},
        'protection': {'protection_status': 'SUPPORT_CONNECTED'},
        'inclusion': {'requirement_present': False},
    }
    for service, payload in records.items():
        response = client.post(f"/api/v1/children/{child['id']}/{service}", headers=headers, json=payload)
        assert response.status_code == 201, response.text
    summary = client.get(f"/api/v1/children/{child['id']}/continuity", headers=headers).json()
    assert summary['overall_status'] == 'CONNECTED'
    assert summary['follow_up_count'] == 0


def test_continuity_reasons_are_present_and_migration_updates_family_location(client):
    headers, _ = register_user(client)
    family = create_family(client, headers)
    child = create_child(client, headers, family['id'])
    client.post(f"/api/v1/children/{child['id']}/education", headers=headers, json={
        'enrollment_status': 'PENDING', 'transfer_status': 'PENDING',
    })
    summary = client.get(f"/api/v1/children/{child['id']}/continuity", headers=headers).json()
    education = next(record for record in summary['services'] if record['service_type'] == 'EDUCATION')
    assert education['reason']
    assert education['action_required'] is True

    migration = client.post(f"/api/v1/families/{family['id']}/migrations", headers=headers, json={
        'from_district': 'Nashik', 'from_taluka': 'Nashik', 'from_location': 'Nashik City',
        'to_district': 'Pune', 'to_taluka': 'Haveli', 'to_location': 'Pune City',
        'migration_date': '2026-10-07', 'status': 'ACTIVE',
    }).json()
    completed = client.put(f"/api/v1/migrations/{migration['id']}", headers=headers, json={'status': 'COMPLETED'})
    assert completed.status_code == 200, completed.text
    family_details = client.get(f"/api/v1/families/{family['id']}", headers=headers).json()
    assert family_details['current_district'] == 'Pune'
    assert family_details['current_taluka'] == 'Haveli'
    assert family_details['current_village_or_city'] == 'Pune City'


def test_followup_can_be_created_and_updated(client):
    headers, _ = register_user(client)
    family = create_family(client, headers)
    response = client.post(f"/api/v1/families/{family['id']}/followups", headers=headers, json={
        'title': 'Call school office', 'priority': 'LOW', 'status': 'OPEN',
    })
    assert response.status_code == 201, response.text
    updated = client.put(f"/api/v1/followups/{response.json()['id']}", headers=headers, json={'status': 'COMPLETED'})
    assert updated.status_code == 200
    assert updated.json()['status'] == 'COMPLETED'


def test_school_assignment_does_not_expose_healthcare(client, db_session):
    citizen_headers, _ = register_user(client)
    family = create_family(client, citizen_headers)
    child = create_child(client, citizen_headers, family['id'])
    school_headers, school_data = register_user(client, 'SCHOOL')
    staff = db_session.get(User, UUID(school_data['id']))
    guardian = db_session.get(User, UUID(family['primary_guardian_user_id']))
    db_session.add(FamilyAccess(
        family_id=UUID(family['id']),
        user_id=staff.id,
        access_role='SCHOOL',
        granted_by_user_id=guardian.id,
    ))
    db_session.commit()
    education = client.get(f"/api/v1/children/{child['id']}/education", headers=school_headers)
    healthcare = client.get(f"/api/v1/children/{child['id']}/healthcare", headers=school_headers)
    assert education.status_code == 200
    assert healthcare.status_code == 403


def test_foreign_child_id_cannot_be_attached_to_family_followup(client):
    first_headers, _ = register_user(client)
    second_headers, _ = register_user(client)
    first_family = create_family(client, first_headers)
    second_family = create_family(client, second_headers)
    child = create_child(client, first_headers, first_family['id'])
    response = client.post(f"/api/v1/families/{second_family['id']}/followups", headers=second_headers, json={
        'child_id': child['id'], 'title': 'Invalid association',
    })
    assert response.status_code == 404


def test_government_summary_is_aggregated_and_role_restricted(client, db_session):
    citizen_headers, _ = register_user(client)
    family = create_family(client, citizen_headers)
    child = create_child(client, citizen_headers, family['id'])
    client.post(f"/api/v1/children/{child['id']}/continuity/check", headers=citizen_headers)

    citizen_denied = client.get('/api/v1/continuity/summary', headers=citizen_headers)
    assert citizen_denied.status_code == 403

    government = User(
        full_name='Aggregate Reviewer',
        email='aggregate-reviewer@example.com',
        mobile_number='+919000000001',
        password_hash='not-used-for-token-test',
        role='GOVERNMENT',
    )
    db_session.add(government)
    db_session.commit()
    token = create_access_token(str(government.id), 'GOVERNMENT')
    response = client.get('/api/v1/continuity/summary', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200
    payload = response.json()
    assert payload['child_count'] == 1
    assert len(payload['service_status_counts']) == 6
    assert 'child_id' not in payload
    assert 'family_id' not in payload