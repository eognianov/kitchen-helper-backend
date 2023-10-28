"""Kitchen Helper API"""
import fastapi
import features.health

app = fastapi.FastAPI()
app.include_router(features.health.router, prefix='/health')
