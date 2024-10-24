import warnings
from jobs.jobs import scheduler
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from config.Database import BaseModel, engine
from config.IniitialSystem import initial_system
from services.auth.ErrorsService import ErrorsService
from utils.settings import Settings

# Environment Configuration
settings = Settings()
BASE_URL = settings.url

# Users
from routes.auth.UserRouter import UserRouter
from routes.auth.AuthenticationRouter import AuthenticationRouter

# Platform
from routes.auth.AppRouter import AppRouter
from routes.auth.ViewRouter import ViewRouter

# Permissions
from routes.auth.UserGroupRouter import UserGroupRouter
from routes.auth.PermissionRouter import PermissionRouter
from routes.auth.FunctionsRouter import FunctionsRouter

app = FastAPI(title="Project API", version="1.0.0")


@app.get("/api", status_code=status.HTTP_200_OK, include_in_schema=False)
async def index():
    try:
        return JSONResponse(
            content={
                "endpoint": "/",
                "version": "1.0.0",
                "description": "Project Api Server",
            },
            status_code=status.HTTP_200_OK,
        )
    except Exception as e:
        error_msg = str(e)
        ErrorsService().internal_error(error_msg)


admin_app = FastAPI(title="API - Businext Manager", version="1.0.0")


@admin_app.get("/", status_code=status.HTTP_200_OK, include_in_schema=False)
async def index():
    try:
        return JSONResponse(
            content={
                "endpoint": "/admin",
                "version": "1.0.0",
                "description": "Project Manager",
                "documentation": f"{BASE_URL}/admin/docs",
            },
            status_code=status.HTTP_200_OK,
        )
    except Exception as e:
        error_msg = str(e)
        ErrorsService().internal_error(error_msg)


BaseModel.metadata.create_all(bind=engine)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Users
admin_app.include_router(UserRouter)

# Platform
admin_app.include_router(AppRouter)
admin_app.include_router(ViewRouter)

# Auth
app.include_router(AuthenticationRouter)

# Permissions / Groups
admin_app.include_router(UserGroupRouter)
admin_app.include_router(PermissionRouter)
admin_app.include_router(FunctionsRouter)

app.mount("/api/admin", admin_app)

# Initial user root system
initial_system()

# Cron Jobs
scheduler.start()

warnings.simplefilter(action="ignore", category=FutureWarning)
