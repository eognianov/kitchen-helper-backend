"""Kitchen Helper API"""
import fastapi
import features.health
import features.users

from fastapi.middleware.cors import CORSMiddleware

import configuration

config = configuration.Config()

app = fastapi.FastAPI()

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.cors.allow_origins,
    allow_methods=config.cors.allow_methods,
    allow_headers=config.cors.allow_headers,
)


app.include_router(features.health.router, prefix='/health')
app.include_router(features.users.router, prefix='/users')
