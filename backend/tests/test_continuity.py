from datetime import date, timedelta
from uuid import UUID, uuid4

import pytest

from app.db.continuity_models import Family, FamilyAccess
from app.db.models import User
from app.core.security import create_access_token
from app.services.continuity import _service_status


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
    assert continuity.json()['overall_status'] == 'FOLLOW_UP_REQUIRED'
    followups = client.get(f"/api/v1/families/{family['id']}/followups", headers=headers)
    assert len(followups.json()) == 6


def test_migration_cannot_be_created_as_completed(client):
    headers, _ = register_user(client)
    family = create_family(client, headers)
    response = client.post(f"/api/v1/families/{family['id']}/migrations", headers=headers, json={
        'from_district': 'Pune', 'from_taluka': 'Haveli', 'from_location': 'Pune City',
        'to_district': 'Nashik', 'to_taluka': 'Nashik', 'to_location': 'Nashik City',
        'migration_date': '2026-10-10', 'status': 'COMPLETED',
    })
    assert response.status_code == 422
    assert client.get(f"/api/v1/families/{family['id']}/migrations", headers=headers).json() == []
    current_family = client.get(f"/api/v1/families/{family['id']}", headers=headers).json()
    assert current_family['current_district'] == 'Pune'


def test_migration_list_is_family_scoped(client):
    headers, _ = register_user(client)
    family = create_family(client, headers)
    response = client.get(f"/api/v1/families/{family['id']}/migrations", headers=headers)
    assert response.status_code == 200
    assert response.json() == []


def test_migration_lifecycle_syncs_location_and_refreshes_continuity(client):
    headers, _ = register_user(client)
    family = create_family(client, headers)
    child = create_child(client, headers, family['id'])
    migration = client.post(f"/api/v1/families/{family['id']}/migrations", headers=headers, json={
        'from_district': 'Pune', 'from_taluka': 'Haveli', 'from_location': 'Pune',
        'to_district': 'Nashik', 'to_taluka': 'Nashik', 'to_location': 'Nashik City',
        'migration_date': '2026-10-10', 'status': 'PLANNED',
    })
    assert migration.status_code == 201, migration.text
    migration_id = migration.json()['id']
    initial_family = client.get(f"/api/v1/families/{family['id']}", headers=headers).json()
    assert initial_family['current_district'] == 'Pune'
    summary = client.get(f"/api/v1/children/{child['id']}/continuity", headers=headers).json()
    assert {record['migration_id'] for record in summary['services']} == {migration_id}

    active = client.put(f"/api/v1/migrations/{migration_id}", headers=headers, json={'status': 'ACTIVE'})
    assert active.status_code == 200, active.text
    assert active.json()['status'] == 'ACTIVE'
    active_family = client.get(f"/api/v1/families/{family['id']}", headers=headers).json()
    assert active_family['current_district'] == 'Pune'

    completed = client.put(f"/api/v1/migrations/{migration_id}", headers=headers, json={'status': 'COMPLETED'})
    assert completed.status_code == 200, completed.text
    completed_family = client.get(f"/api/v1/families/{family['id']}", headers=headers).json()
    assert completed_family['current_district'] == 'Nashik'
    assert completed_family['current_taluka'] == 'Nashik'
    assert completed_family['current_village_or_city'] == 'Nashik City'
    refreshed = client.get(f"/api/v1/children/{child['id']}/continuity", headers=headers).json()
    assert {record['migration_id'] for record in refreshed['services']} == {migration_id}
    assert refreshed['overall_status'] == 'FOLLOW_UP_REQUIRED'


def test_current_continuity_ignores_newer_planned_migration(client):
    headers, _ = register_user(client)
    family = create_family(client, headers)
    child = create_child(client, headers, family['id'])
    active = client.post(f"/api/v1/families/{family['id']}/migrations", headers=headers, json={
        'from_district': 'Pune', 'from_taluka': 'Haveli', 'from_location': 'Pune',
        'to_district': 'Mumbai', 'to_taluka': 'Mumbai', 'to_location': 'Mumbai City',
        'migration_date': '2026-10-01', 'status': 'ACTIVE',
    }).json()
    planned = client.post(f"/api/v1/families/{family['id']}/migrations", headers=headers, json={
        'from_district': 'Mumbai', 'from_taluka': 'Mumbai', 'from_location': 'Mumbai City',
        'to_district': 'Delhi', 'to_taluka': 'New Delhi', 'to_location': 'Delhi City',
        'migration_date': '2026-12-01', 'status': 'PLANNED',
    })
    assert planned.status_code == 201, planned.text
    summary = client.get(f"/api/v1/children/{child['id']}/continuity", headers=headers).json()
    assert {record['migration_id'] for record in summary['services']} == {active['id']}


def test_migration_completion_does_not_transfer_origin_confirmation(client):
    headers, _ = register_user(client)
    family = create_family(client, headers)
    child = create_child(client, headers, family['id'])
    initial = client.get(f"/api/v1/children/{child['id']}/continuity", headers=headers).json()
    origin_record = next(item for item in initial['services'] if item['service_type'] == 'HEALTHCARE')
    confirmed = client.put(f"/api/v1/continuity/{origin_record['id']}", headers=headers, json={
        'status': 'CONNECTED',
        'confirmation_method': 'SERVICE_PROVIDER',
    })
    assert confirmed.status_code == 200, confirmed.text
    migration = client.post(f"/api/v1/families/{family['id']}/migrations", headers=headers, json={
        'from_district': 'Pune', 'from_taluka': 'Haveli', 'from_location': 'Pune',
        'to_district': 'Nashik', 'to_taluka': 'Nashik', 'to_location': 'Nashik City',
        'migration_date': '2026-10-10', 'status': 'PLANNED',
    }).json()
    destination = client.get(f"/api/v1/children/{child['id']}/continuity", headers=headers).json()
    destination_record = next(item for item in destination['services'] if item['service_type'] == 'HEALTHCARE')
    assert destination_record['migration_id'] == migration['id']
    assert destination_record['status'] == 'PENDING'
    assert destination_record['outcome_confirmed_at'] is None

    activated = client.put(f"/api/v1/migrations/{migration['id']}", headers=headers, json={'status': 'ACTIVE'})
    assert activated.status_code == 200
    active_summary = client.get(f"/api/v1/children/{child['id']}/continuity", headers=headers).json()
    active_healthcare = next(item for item in active_summary['services'] if item['service_type'] == 'HEALTHCARE')
    active_confirmation = client.put(f"/api/v1/continuity/{active_healthcare['id']}", headers=headers, json={
        'status': 'CONNECTED',
        'confirmation_method': 'SERVICE_PROVIDER',
    })
    assert active_confirmation.status_code == 200
    completed = client.put(f"/api/v1/migrations/{migration['id']}", headers=headers, json={'status': 'COMPLETED'})
    assert completed.status_code == 200
    after_completion = client.get(f"/api/v1/children/{child['id']}/continuity", headers=headers).json()
    destination_record = next(item for item in after_completion['services'] if item['service_type'] == 'HEALTHCARE')
    assert destination_record['status'] == 'PENDING'
    assert destination_record['outcome_confirmed_at'] is None


def test_unresolved_continuity_need_carries_into_next_migration(client):
    headers, _ = register_user(client)
    family = create_family(client, headers)
    child = create_child(client, headers, family['id'])
    origin = client.get(f"/api/v1/children/{child['id']}/continuity", headers=headers).json()
    education = next(item for item in origin['services'] if item['service_type'] == 'EDUCATION')
    marked = client.put(f"/api/v1/continuity/{education['id']}", headers=headers, json={
        'status': 'FOLLOW_UP_REQUIRED',
    })
    assert marked.status_code == 200
    migration = client.post(f"/api/v1/families/{family['id']}/migrations", headers=headers, json={
        'from_district': 'Pune', 'from_taluka': 'Haveli', 'from_location': 'Pune',
        'to_district': 'Nashik', 'to_taluka': 'Nashik', 'to_location': 'Nashik City',
        'migration_date': '2026-10-10', 'status': 'ACTIVE',
    }).json()
    destination = client.get(f"/api/v1/children/{child['id']}/continuity", headers=headers).json()
    education = next(item for item in destination['services'] if item['service_type'] == 'EDUCATION')
    assert education['migration_id'] == migration['id']
    assert education['status'] == 'FOLLOW_UP_REQUIRED'


def test_migration_status_cannot_move_backwards(client):
    headers, _ = register_user(client)
    family = create_family(client, headers)
    migration = client.post(f"/api/v1/families/{family['id']}/migrations", headers=headers, json={
        'from_district': 'Pune', 'from_taluka': 'Haveli', 'from_location': 'Pune',
        'to_district': 'Nashik', 'to_taluka': 'Nashik', 'to_location': 'Nashik City',
        'migration_date': '2026-10-10', 'status': 'PLANNED',
    }).json()
    assert client.put(f"/api/v1/migrations/{migration['id']}", headers=headers, json={'status': 'ACTIVE'}).status_code == 200
    completed = client.put(f"/api/v1/migrations/{migration['id']}", headers=headers, json={'status': 'COMPLETED'})
    assert completed.status_code == 200
    backwards = client.put(f"/api/v1/migrations/{migration['id']}", headers=headers, json={'status': 'ACTIVE'})
    assert backwards.status_code == 409


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
    assert education['status'] == 'FOLLOW_UP_REQUIRED'


def test_finding_a_school_does_not_confirm_enrollment(client):
    headers, _ = register_user(client)
    family = create_family(client, headers)
    child = create_child(client, headers, family['id'])
    client.post(f"/api/v1/children/{child['id']}/education", headers=headers, json={
        'current_school_name': 'Local School',
        'enrollment_status': 'UNKNOWN',
    })
    summary = client.get(f"/api/v1/children/{child['id']}/continuity", headers=headers).json()
    education = next(record for record in summary['services'] if record['service_type'] == 'EDUCATION')
    assert education['status'] == 'FOLLOW_UP_REQUIRED'


def test_contacting_a_provider_does_not_confirm_acceptance(client):
    headers, _ = register_user(client)
    family = create_family(client, headers)
    child = create_child(client, headers, family['id'])
    client.post(f"/api/v1/children/{child['id']}/healthcare", headers=headers, json={
        'healthcare_provider_name': 'Community Clinic',
        'continuity_status': 'FOLLOW_UP_RECOMMENDED',
    })
    summary = client.get(f"/api/v1/children/{child['id']}/continuity", headers=headers).json()
    healthcare = next(record for record in summary['services'] if record['service_type'] == 'HEALTHCARE')
    assert healthcare['status'] == 'FOLLOW_UP_REQUIRED'


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
    blocked = client.put(f"/api/v1/continuity/{protection['id']}", headers=headers, json={
        'status': 'SUPPORT_NOT_REQUIRED',
        'confirmation_method': 'FAMILY_REPORT',
    })
    assert blocked.status_code == 409


def test_all_connected_services_return_connected_summary(client):
    headers, user = register_user(client)
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
    assert summary['overall_status'] == 'FOLLOW_UP_REQUIRED'
    assert {record['status'] for record in summary['services']} == {'PENDING'}

    for record in summary['services']:
        outcome = 'SUPPORT_NOT_REQUIRED' if record['service_type'] == 'INCLUSION' else 'CONNECTED'
        confirmed = client.put(f"/api/v1/continuity/{record['id']}", headers=headers, json={
            'status': outcome,
            'confirmation_method': 'DOCUMENT_REVIEW',
            'supporting_reference': 'CASE-REF-7',
        })
        assert confirmed.status_code == 200, confirmed.text
        assert confirmed.json()['status'] == outcome
        assert confirmed.json()['outcome_confirmed_at']
        assert confirmed.json()['outcome_confirmed_by_user_id'] == user['id']
        assert confirmed.json()['confirmation_method'] == 'DOCUMENT_REVIEW'
        assert confirmed.json()['supporting_reference'] == 'CASE-REF-7'

    summary = client.get(f"/api/v1/children/{child['id']}/continuity", headers=headers).json()
    assert summary['overall_status'] == 'CONNECTED'
    assert summary['follow_up_count'] == 0
    assert {record['status'] for record in summary['services']} == {'CONNECTED', 'SUPPORT_NOT_REQUIRED'}


def test_confirmed_outcome_requires_confirmation_method(client):
    headers, _ = register_user(client)
    family = create_family(client, headers)
    child = create_child(client, headers, family['id'])
    records = client.post(f"/api/v1/children/{child['id']}/continuity/check", headers=headers).json()
    response = client.put(f"/api/v1/continuity/{records[0]['id']}", headers=headers, json={
        'status': 'CONNECTED',
    })
    assert response.status_code == 422


def test_new_unresolved_source_status_revokes_prior_confirmation(client):
    headers, _ = register_user(client)
    family = create_family(client, headers)
    child = create_child(client, headers, family['id'])
    healthcare = client.post(f"/api/v1/children/{child['id']}/healthcare", headers=headers, json={
        'continuity_status': 'CONNECTED',
    }).json()
    summary = client.get(f"/api/v1/children/{child['id']}/continuity", headers=headers).json()
    record = next(item for item in summary['services'] if item['service_type'] == 'HEALTHCARE')
    assert record['status'] == 'PENDING'
    confirmed = client.put(f"/api/v1/continuity/{record['id']}", headers=headers, json={
        'status': 'CONNECTED',
        'confirmation_method': 'SERVICE_PROVIDER',
    })
    assert confirmed.status_code == 200
    changed = client.put(f"/api/v1/healthcare/{healthcare['id']}", headers=headers, json={
        'continuity_status': 'FOLLOW_UP_RECOMMENDED',
    })
    assert changed.status_code == 200
    refreshed = client.get(f"/api/v1/children/{child['id']}/continuity", headers=headers).json()
    record = next(item for item in refreshed['services'] if item['service_type'] == 'HEALTHCARE')
    assert record['status'] == 'FOLLOW_UP_REQUIRED'
    assert record['outcome_confirmed_at'] is None


def test_completed_followup_does_not_resolve_service_need(client):
    headers, _ = register_user(client)
    family = create_family(client, headers)
    child = create_child(client, headers, family['id'])
    initial = client.get(f"/api/v1/children/{child['id']}/continuity", headers=headers).json()
    education = next(item for item in initial['services'] if item['service_type'] == 'EDUCATION')
    followups = client.get(f"/api/v1/families/{family['id']}/followups", headers=headers).json()
    education_followup = next(item for item in followups if item['service_continuity_id'] == education['id'])
    completed = client.put(f"/api/v1/followups/{education_followup['id']}", headers=headers, json={'status': 'COMPLETED'})
    assert completed.status_code == 200
    refreshed = client.get(f"/api/v1/children/{child['id']}/continuity", headers=headers).json()
    education = next(item for item in refreshed['services'] if item['service_type'] == 'EDUCATION')
    assert education['status'] == 'PENDING'
    assert education['action_required'] is True


def test_unrecognized_protection_state_requires_review():
    from app.db.continuity_models import Child, ChildProtectionRecord

    child = Child(protection=ChildProtectionRecord(
        protection_status='UNRECOGNIZED',
        followup_required=False,
    ))
    assert _service_status(child, 'PROTECTION') == 'REVIEW_REQUIRED'


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


def test_contact_referral_followup_is_linked_to_child_service_and_remains_unresolved(client):
    headers, _ = register_user(client)
    family = create_family(client, headers)
    child = create_child(client, headers, family['id'])
    summary = client.get(f"/api/v1/children/{child['id']}/continuity", headers=headers).json()
    healthcare = next(item for item in summary['services'] if item['service_type'] == 'HEALTHCARE')
    existing_followups = client.get(f"/api/v1/families/{family['id']}/followups", headers=headers).json()
    response = client.post(f"/api/v1/families/{family['id']}/followups", headers=headers, json={
        'child_id': child['id'],
        'service_continuity_id': healthcare['id'],
        'title': 'Healthcare contact / referral',
        'description': 'Contact attempt / referral: Called clinic\nProvider response: Asked to call back',
        'status': 'IN_PROGRESS',
        'due_date': '2026-10-12',
    })
    assert response.status_code == 201, response.text
    followup = response.json()
    assert followup['child_id'] == child['id']
    assert followup['service_continuity_id'] == healthcare['id']
    assert followup['due_date'] == '2026-10-12'

    updated = client.put(f"/api/v1/followups/{followup['id']}", headers=headers, json={
        'description': 'Contact attempt / referral: Called clinic\nProvider response: Appointment offered',
        'status': 'COMPLETED',
    })
    assert updated.status_code == 200, updated.text
    assert 'Appointment offered' in updated.json()['description']
    refreshed = client.get(f"/api/v1/children/{child['id']}/continuity", headers=headers).json()
    healthcare = next(item for item in refreshed['services'] if item['service_type'] == 'HEALTHCARE')
    assert healthcare['status'] == 'PENDING'


def test_contact_followup_rejects_oversized_description_without_creating_record(client):
    headers, _ = register_user(client)
    family = create_family(client, headers)
    child = create_child(client, headers, family['id'])
    summary = client.get(f"/api/v1/children/{child['id']}/continuity", headers=headers).json()
    healthcare = next(item for item in summary['services'] if item['service_type'] == 'HEALTHCARE')
    existing_followups = client.get(f"/api/v1/families/{family['id']}/followups", headers=headers).json()
    response = client.post(f"/api/v1/families/{family['id']}/followups", headers=headers, json={
        'child_id': child['id'],
        'service_continuity_id': healthcare['id'],
        'title': 'Healthcare contact / referral',
        'description': 'Contact attempt / referral: ' + ('x' * 2000),
    })
    assert response.status_code == 422
    after_rejection = client.get(f"/api/v1/families/{family['id']}/followups", headers=headers).json()
    assert after_rejection == existing_followups


def test_contact_followup_preserves_valid_description(client):
    headers, _ = register_user(client)
    family = create_family(client, headers)
    child = create_child(client, headers, family['id'])
    summary = client.get(f"/api/v1/children/{child['id']}/continuity", headers=headers).json()
    healthcare = next(item for item in summary['services'] if item['service_type'] == 'HEALTHCARE')
    label = 'Contact attempt / referral: '
    description = label + ('x' * (2000 - len(label)))
    response = client.post(f"/api/v1/families/{family['id']}/followups", headers=headers, json={
        'child_id': child['id'],
        'service_continuity_id': healthcare['id'],
        'title': 'Healthcare contact / referral',
        'description': description,
    })
    assert response.status_code == 201, response.text
    assert response.json()['description'] == description


def test_followup_cannot_link_another_childs_continuity_record(client):
    headers, _ = register_user(client)
    family = create_family(client, headers)
    first_child = create_child(client, headers, family['id'])
    second_child = create_child(client, headers, family['id'])
    first_summary = client.get(f"/api/v1/children/{first_child['id']}/continuity", headers=headers).json()
    first_record = first_summary['services'][0]
    response = client.post(f"/api/v1/families/{family['id']}/followups", headers=headers, json={
        'child_id': second_child['id'],
        'service_continuity_id': first_record['id'],
        'title': 'Mismatched follow-up',
    })
    assert response.status_code == 400


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

    dashboard = client.get('/api/v1/government/dashboard', headers={'Authorization': f'Bearer {token}'})
    assert dashboard.status_code == 200
    dashboard_payload = dashboard.json()
    assert dashboard_payload['profile_counts'] == {'family_count': 1, 'child_count': 1}
    assert dashboard_payload['privacy']['aggregate_only'] is True
    assert dashboard_payload['destination_service_gaps'] == []
    assert dashboard_payload['migration_trend'] == []
    assert 'child_id' not in str(dashboard_payload)
    assert 'family_id' not in str(dashboard_payload)
    assert 'Aarav' not in str(dashboard_payload)

    admin = User(
        full_name='Aggregate Administrator',
        email='aggregate-admin@example.com',
        mobile_number='+919000000002',
        password_hash='not-used-for-token-test',
        role='ADMIN',
    )
    db_session.add(admin)
    db_session.commit()
    admin_token = create_access_token(str(admin.id), 'ADMIN')
    assert client.get(
        '/api/v1/government/dashboard',
        headers={'Authorization': f'Bearer {admin_token}'},
    ).status_code == 200


def test_government_dashboard_counts_and_small_group_suppression(client, db_session):
    citizen_headers, _ = register_user(client)
    assert client.get('/api/v1/government/dashboard').status_code == 401
    assert client.get('/api/v1/government/dashboard', headers=citizen_headers).status_code == 403

    today = date.today()
    families = []
    for _ in range(5):
        family = create_family(client, citizen_headers)
        families.append(family)
        child = create_child(client, citizen_headers, family['id'])
        migration = client.post(f"/api/v1/families/{family['id']}/migrations", headers=citizen_headers, json={
            'from_district': 'Nashik', 'from_taluka': 'Nashik', 'from_location': 'Origin',
            'to_district': 'Shared District', 'to_taluka': 'Shared Taluka', 'to_location': 'Shared Town',
            'migration_date': today.isoformat(), 'status': 'ACTIVE',
        })
        assert migration.status_code == 201, migration.text
        if len(families) == 1:
            late_followup = client.post(f"/api/v1/families/{family['id']}/followups", headers=citizen_headers, json={
                'child_id': child['id'], 'title': 'Overdue planning follow-up',
                'due_date': (today - timedelta(days=1)).isoformat(),
            })
            due_followup = client.post(f"/api/v1/families/{family['id']}/followups", headers=citizen_headers, json={
                'child_id': child['id'], 'title': 'Due planning follow-up',
                'due_date': today.isoformat(),
            })
            assert late_followup.status_code == 201
            assert due_followup.status_code == 201

    demo_family = create_family(client, citizen_headers, family_name='DEMO DATA - Excluded')
    demo_child = create_child(client, citizen_headers, demo_family['id'])
    demo_migration = client.post(f"/api/v1/families/{demo_family['id']}/migrations", headers=citizen_headers, json={
        'from_district': 'Nashik', 'from_taluka': 'Nashik', 'from_location': 'Origin',
        'to_district': 'Shared District', 'to_taluka': 'Shared Taluka', 'to_location': 'Shared Town',
        'migration_date': today.isoformat(), 'status': 'ACTIVE',
    })
    assert demo_migration.status_code == 201
    demo_family_record = db_session.get(Family, UUID(demo_family['id']))
    demo_family_record.family_reference_id = f"DEMO-{demo_family['id'][:8]}"
    db_session.commit()

    government = User(
        full_name='Aggregate Reviewer',
        email='aggregate-threshold@example.com',
        mobile_number='+919000000003',
        password_hash='not-used-for-token-test',
        role='GOVERNMENT',
    )
    db_session.add(government)
    db_session.commit()
    token = create_access_token(str(government.id), 'GOVERNMENT')
    response = client.get('/api/v1/government/dashboard', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200, response.text
    payload = response.json()

    assert payload['profile_counts'] == {'family_count': 5, 'child_count': 5}
    assert payload['migration_counts'] == {'PLANNED': 0, 'ACTIVE': 5, 'COMPLETED': 0}
    assert payload['followups']['overdue'] == 1
    assert payload['followups']['due_today'] == 1
    assert payload['destination_service_gaps']
    assert all(item['affected_child_count'] >= 5 for item in payload['destination_service_gaps'])
    assert all(item['district'] == 'Shared District' for item in payload['destination_service_gaps'])
    assert payload['migration_trend'] == [{
        'month': today.strftime('%Y-%m'),
        'migration_count': 5,
        'family_count': 5,
    }]
    education = next(item for item in payload['unresolved_needs_by_service'] if item['service_type'] == 'EDUCATION')
    assert education['total'] == 5
    assert 'Aarav' not in str(payload)
    assert demo_child['id'] not in str(payload)


def test_dashboard_suppression_counts_distinct_families_not_children(client, db_session):
    citizen_headers, _ = register_user(client)
    family = create_family(client, citizen_headers)
    children = [create_child(client, citizen_headers, family['id']) for _ in range(5)]
    migration = client.post(f"/api/v1/families/{family['id']}/migrations", headers=citizen_headers, json={
        'from_district': 'Nashik', 'from_taluka': 'Nashik', 'from_location': 'Origin',
        'to_district': 'Single Family District', 'to_taluka': 'Haveli', 'to_location': 'Destination',
        'migration_date': date.today().isoformat(), 'status': 'ACTIVE',
    })
    assert migration.status_code == 201, migration.text

    government = User(
        full_name='Aggregate Reviewer',
        email='aggregate-single-family@example.com',
        mobile_number='+919000000004',
        password_hash='not-used-for-token-test',
        role='GOVERNMENT',
    )
    db_session.add(government)
    db_session.commit()
    token = create_access_token(str(government.id), 'GOVERNMENT')
    response = client.get('/api/v1/government/dashboard', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload['destination_service_gaps'] == []
    assert all(child['id'] not in str(payload) for child in children)
    assert 'family_id' not in str(payload)