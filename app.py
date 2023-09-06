import warnings
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from config.Database import engine, BaseModel
from config.IniitialSystem import initial_system
from services.ErrorsService import ErrorsService
from utils.settings import Settings

# Environment Configuration
settings = Settings()
BASE_URL = settings.url

# Auth
from routes.AuthenticationRouter import AuthenticationRouter

# Permissions
from routes.UserGroupRouter import UserGroupRouter
from routes.PermissionRouter import PermissionRouter
from routes.FunctionsRouter import FunctionsRouter

# Administration
from routes.UserRouter import UserRouter


app = FastAPI(title="API - Created for Brandon Mojica", version="1.0.0")


@app.get("/", status_code=status.HTTP_200_OK, include_in_schema=False)
async def index():
    try:
        return JSONResponse(
            content={
                "endpoint": "/",
                "version": "1.0.0",
                "description": "Api Server",
            },
            status_code=status.HTTP_200_OK,
        )
    except Exception as e:
        error_msg = str(e)
        ErrorsService().internal_error(error_msg)


admin_app = FastAPI(title="API - Administration", version="1.0.0")


@admin_app.get("/", status_code=status.HTTP_200_OK, include_in_schema=False)
async def index():
    try:
        return JSONResponse(
            content={
                "endpoint": "/admin",
                "version": "1.0.0",
                "description": "Api Server for app administration",
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

# Auth
admin_app.include_router(AuthenticationRouter)

# Permissions / Groups
admin_app.include_router(UserGroupRouter)
admin_app.include_router(PermissionRouter)
admin_app.include_router(FunctionsRouter)

# Administration
admin_app.include_router(UserRouter)

# Initial System Config
app.mount("/admin", admin_app)

initial_system()

warnings.simplefilter(action="ignore", category=FutureWarning)
