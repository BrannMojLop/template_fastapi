import sys
from fastapi.logger import logger
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from utils.settings import Settings
from config.values_dafault import user_root, functions_default

# Index
from routes.index import Index

# Users
from routes.user.users import users_records

# Permissions
from routes.user_groups.user_groups import user_groups
from routes.permissions.permissions import permissions
from routes.permissions_functions.permissions_functions import permissions_functions
from routes.users_permissions_groups.users_permissions_groups import users_permissions_groups
from routes.functions.functions import functions

settings = Settings()

BASE_URL = settings.url
USE_NGROK = settings.ngrok


def init_webhooks(base_url):
    print(f'Public URL: {public_url}')
    # Update inbound traffic via APIs to use the public-facing ngrok URL
    pass


app = FastAPI()

if USE_NGROK:
    # pyngrok should only ever be installed or initialized in a dev environment when this flag is set
    from pyngrok import ngrok

    # Get the dev server port (defaults to 8000 for Uvicorn, can be overridden with `--port`
    # when starting the server
    port = sys.argv[sys.argv.index(
        "--port") + 1] if "--port" in sys.argv else 8000

    # Open a ngrok tunnel to the dev server
    public_url = ngrok.connect(port, bind_tls=True).public_url
    logger.info(
        "ngrok tunnel -host-header=rewrite \"{}\" -> \"http://127.0.0.1:{}\"".format(public_url, port))

    # Update any base URLs or webhooks to use the public ngrok URL
    BASE_URL = public_url
    init_webhooks(public_url)

origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(Index)

# Users
app.include_router(users_records)

# Permissions / Groups
app.include_router(user_groups)
app.include_router(permissions)
app.include_router(functions)
app.include_router(users_permissions_groups)
app.include_router(permissions_functions)

# Values default
user_root();
functions_default();

load_dotenv()
