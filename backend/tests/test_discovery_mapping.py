import pytest

from app.db.directory_models import ServiceType
from app.services.discovery_mapping import (
    ACTION_STATUSES,
    CONTINUITY_TO_DISCOVERY_SERVICE_TYPE,
    discovery_path,
    discovery_target,
    needs_discovery_action,
)

SPEC_MAPPING = {
    'EDUCATION': 'EDUCATION',
    'HEALTHCARE': 'HEALTHCARE',
    'NUTRITION': 'NUTRITION',
    'PROTECTION': 'CHILD_SUPPORT',
    'WELLBEING': 'WELLBEING',
    'INCLUSION': 'INCLUSION',
    'GOVERNMENT_SCHEME': 'GOVERNMENT_SCHEME',
    'SOCIAL_SUPPORT': 'SOCIAL_SUPPORT',
    'DOCUMENTATION': 'DOCUMENTATION',
    'HOUSING_SUPPORT': 'HOUSING_SUPPORT',
}


def test_mapping_matches_spec_exactly():
    assert CONTINUITY_TO_DISCOVERY_SERVICE_TYPE == SPEC_MAPPING


def test_every_discovery_target_is_accepted_by_the_nearby_api():
    valid = {item.value for item in ServiceType}
    assert set(SPEC_MAPPING.values()) <= valid


@pytest.mark.parametrize(
    'continuity_type,expected',
    [
        ('EDUCATION', 'EDUCATION'),
        ('HEALTHCARE', 'HEALTHCARE'),
        ('NUTRITION', 'NUTRITION'),
        ('PROTECTION', 'CHILD_SUPPORT'),
        ('WELLBEING', 'WELLBEING'),
        ('INCLUSION', 'INCLUSION'),
    ],
)
def test_action_required_service_maps_to_discovery_type(continuity_type, expected):
    assert discovery_target(continuity_type, 'FOLLOW_UP_RECOMMENDED', True) == expected


def test_connected_service_needs_no_discovery_action():
    assert discovery_target('EDUCATION', 'CONNECTED', False) is None
    assert needs_discovery_action('CONNECTED', False) is False
    assert needs_discovery_action('CONNECTED', None) is False


@pytest.mark.parametrize('status', sorted(ACTION_STATUSES))
def test_action_statuses_trigger_discovery(status):
    assert needs_discovery_action(status, False) is True
    assert needs_discovery_action(status, None) is True


def test_action_required_flag_alone_triggers_discovery():
    assert needs_discovery_action('CONNECTED', True) is True


def test_unknown_service_type_has_no_target():
    assert discovery_target('SOMETHING_ELSE', 'PENDING', True) is None


def test_discovery_path_carries_only_type_and_place():
    assert discovery_path('PROTECTION') == '/map?service_type=CHILD_SUPPORT'
    assert discovery_path('EDUCATION', 'Pune') == '/map?service_type=EDUCATION&place=Pune'
    assert discovery_path('UNKNOWN') == '/map'
    assert 'child' not in discovery_path('EDUCATION', 'Pune').lower()
    assert 'family' not in discovery_path('EDUCATION', 'Pune').lower()