"""Kitchen Helper API"""
import fastapi
import features.health
import features.users

from fastapi.middleware.cors import CORSMiddleware

app = fastapi.FastAPI()

# TODO: Configure CORS middleware
# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", ],
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(features.health.router, prefix='/health')
app.include_router(features.users.router, prefix='/users')
