"""Distance helpers for nearby service discovery.

PostGIS is optional. If the PostGIS extension is installed in the connected
PostgreSQL database it is used for the distance calculation; otherwise the
pure-Python Haversine formula is used. Both return kilometres, so the API
response has the same shape either way.
"""
import math
from collections.abc import Iterable
from uuid import UUID

from sqlalchemy import bindparam, text
from sqlalchemy.orm import Session

from app.db.directory_models import Organization

EARTH_RADIUS_KM = 6371.0088
# One degree of latitude is never shorter than ~110.5 km, so 110 is a safe divisor
# for building a bounding window that cannot wrongly exclude a match.
KM_PER_DEGREE_LATITUDE = 110.0


def validate_coordinates(latitude: float, longitude: float) -> None:
    if not (math.isfinite(latitude) and -90 <= latitude <= 90):
        raise ValueError('latitude must be between -90 and 90')
    if not (math.isfinite(longitude) and -180 <= longitude <= 180):
        raise ValueError('longitude must be between -180 and 180')


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance in kilometres between two decimal-degree points."""
    validate_coordinates(lat1, lon1)
    validate_coordinates(lat2, lon2)
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)
    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    return 2 * EARTH_RADIUS_KM * math.asin(min(1.0, math.sqrt(a)))


def latitude_window(latitude: float, radius_km: float) -> tuple[float, float]:
    """Cheap SQL pre-filter: only organizations inside this latitude band can match."""
    delta = radius_km / KM_PER_DEGREE_LATITUDE
    return max(-90.0, latitude - delta), min(90.0, latitude + delta)


def postgis_available(db: Session) -> bool:
    """True only on PostgreSQL with the PostGIS extension installed."""
    try:
        if db.get_bind().dialect.name != 'postgresql':
            return False
        row = db.execute(text("SELECT 1 FROM pg_extension WHERE extname = 'postgis'")).first()
        return row is not None
    except Exception:
        db.rollback()
        return False


_POSTGIS_SQL = text(
    """
    SELECT id,
           ST_DistanceSphere(
               ST_SetSRID(ST_MakePoint(longitude, latitude), 4326),
               ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)
           ) / 1000.0 AS distance_km
    FROM organizations
    WHERE id IN :ids
    """
).bindparams(bindparam('ids', expanding=True))


def _postgis_distances_km(db: Session, latitude: float, longitude: float, ids: list[UUID]) -> dict[UUID, float]:
    rows = db.execute(_POSTGIS_SQL, {'lat': latitude, 'lon': longitude, 'ids': ids})
    return {row.id: float(row.distance_km) for row in rows}


def distances_km(
    db: Session,
    latitude: float,
    longitude: float,
    organizations: Iterable[Organization],
) -> dict[UUID, float]:
    """Distance in km from the search point to each organization, keyed by organization id.

    PostGIS-capable database -> PostGIS. Otherwise (or if PostGIS fails) -> Haversine.
    """
    orgs = list(organizations)
    if orgs and postgis_available(db):
        try:
            return _postgis_distances_km(db, latitude, longitude, [org.id for org in orgs])
        except Exception:
            db.rollback()
    return {org.id: haversine_km(latitude, longitude, org.latitude, org.longitude) for org in orgs}