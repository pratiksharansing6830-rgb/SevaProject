from app.db.models import UserRole


def test_health_endpoint(client):
    response = client.get('/api/v1/health')
    assert response.status_code == 200
    assert response.json()['status'] == 'ok'
    assert response.json()['service'] == 'sahaayak-api'


def test_successful_registration(client):
    payload = {
        'full_name': 'Aisha Patel',
        'email': 'aisha@example.com',
        'mobile_number': '+91 9876543210',
        'password': 'securepass123',
        'confirm_password': 'securepass123',
        'role': 'CITIZEN',
        'preferred_language': 'English',
    }

    response = client.post('/api/v1/auth/register', json=payload)
    assert response.status_code == 201
    assert response.json()['email'] == 'aisha@example.com'
    assert 'password' not in response.json()


def test_duplicate_registration(client):
    payload = {
        'full_name': 'Duplicate User',
        'email': 'duplicate@example.com',
        'mobile_number': '+91 9000000000',
        'password': 'securepass123',
        'confirm_password': 'securepass123',
        'role': 'CITIZEN',
        'preferred_language': 'English',
    }
    first = client.post('/api/v1/auth/register', json=payload)
    assert first.status_code == 201

    second = client.post('/api/v1/auth/register', json=payload)
    assert second.status_code == 409


def test_successful_login(client):
    register_payload = {
        'full_name': 'Login User',
        'email': 'login@example.com',
        'mobile_number': '+91 9111111111',
        'password': 'securepass123',
        'confirm_password': 'securepass123',
        'role': 'CITIZEN',
        'preferred_language': 'English',
    }
    client.post('/api/v1/auth/register', json=register_payload)

    response = client.post('/api/v1/auth/login', json={'identifier': 'login@example.com', 'password': 'securepass123'})
    assert response.status_code == 200
    assert 'access_token' in response.json()
    assert response.json()['user']['email'] == 'login@example.com'


def test_invalid_login(client):
    response = client.post('/api/v1/auth/login', json={'identifier': 'no-one@example.com', 'password': 'wrongpass'})
    assert response.status_code == 401


def test_authenticated_me(client):
    register_payload = {
        'full_name': 'Me User',
        'email': 'me@example.com',
        'mobile_number': '+91 9123456789',
        'password': 'securepass123',
        'confirm_password': 'securepass123',
        'role': 'CITIZEN',
        'preferred_language': 'Marathi',
    }
    client.post('/api/v1/auth/register', json=register_payload)

    login_response = client.post('/api/v1/auth/login', json={'identifier': 'me@example.com', 'password': 'securepass123'})
    token = login_response.json()['access_token']

    me_response = client.get('/api/v1/auth/me', headers={'Authorization': f'Bearer {token}'})
    assert me_response.status_code == 200
    assert me_response.json()['email'] == 'me@example.com'
    assert 'password_hash' not in me_response.json()


def test_unauthenticated_me(client):
    response = client.get('/api/v1/auth/me')
    assert response.status_code == 401


def test_role_validation(client):
    payload = {
        'full_name': 'Government User',
        'email': 'gov@example.com',
        'mobile_number': '+91 9555555555',
        'password': 'securepass123',
        'confirm_password': 'securepass123',
        'role': 'GOVERNMENT',
        'preferred_language': 'Hindi',
    }

    response = client.post('/api/v1/auth/register', json=payload)
    assert response.status_code == 400
    assert 'Government and administrator accounts' in response.json()['detail']
