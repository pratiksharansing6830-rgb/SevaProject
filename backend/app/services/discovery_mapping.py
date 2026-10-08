"""Single mapping from a Part 3 continuity service type to a public discovery service type.

This module does NOT calculate continuity. Part 3 stays the source of truth for status and
action_required; this only decides which kind of public service to look for.
"""
from urllib.parse import urlencode

CONTINUITY_TO_DISCOVERY_SERVICE_TYPE: dict[str, str] = {
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

# Statuses that mean a discovery action is useful. CONNECTED is deliberately absent.
ACTION_STATUSES = frozenset({'PENDING', 'FOLLOW_UP_RECOMMENDED', 'REVIEW_REQUIRED', 'NOT_AVAILABLE'})


def discovery_service_type(continuity_service_type: str) -> str | None:
    return CONTINUITY_TO_DISCOVERY_SERVICE_TYPE.get((continuity_service_type or '').upper())


def needs_discovery_action(status: str, action_required: bool | None = None) -> bool:
    """True if Part 3's action_required flag is set, or the status is one that needs action."""
    return bool(action_required) or (status or '').upper() in ACTION_STATUSES


def discovery_target(continuity_service_type: str, status: str, action_required: bool | None = None) -> str | None:
    if not needs_discovery_action(status, action_required):
        return None
    return discovery_service_type(continuity_service_type)


def discovery_path(continuity_service_type: str, place: str | None = None) -> str:
    """Frontend URL for the map. Carries only a service type and an optional place name."""
    target = discovery_service_type(continuity_service_type)
    if target is None:
        return '/map'
    params = {'service_type': target}
    if place:
        params['place'] = place
    return f'/map?{urlencode(params)}'