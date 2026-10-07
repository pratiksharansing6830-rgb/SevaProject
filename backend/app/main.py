from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.auth import router as auth_router
from app.api.routes.children import router as children_router
from app.api.routes.continuity import router as continuity_router
from app.api.routes.families import router as families_router
from app.api.routes.followups import router as followups_router
from app.api.routes.health import router as health_router
from app.api.routes.migrations import router as migrations_router
from app.api.routes.service_records import router as service_records_router
from app.api.routes.users import router as users_router
from app.core.config import settings

app = FastAPI(
    title='Sahaayak API',
    version='0.2.0',
    description='Backend foundation for the Sahaayak child continuity platform.',
)

origins = [origin.strip() for origin in settings.FRONTEND_URL.split(',') if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(health_router, prefix='/api/v1')
app.include_router(auth_router, prefix='/api/v1')
app.include_router(users_router, prefix='/api/v1')
app.include_router(families_router, prefix='/api/v1')
app.include_router(children_router, prefix='/api/v1')
app.include_router(migrations_router, prefix='/api/v1')
app.include_router(service_records_router, prefix='/api/v1')
app.include_router(continuity_router, prefix='/api/v1')
app.include_router(followups_router, prefix='/api/v1')


@app.get('/')
def read_root() -> dict[str, str]:
    return {'service': 'sahaayak-api', 'status': 'ok'}
