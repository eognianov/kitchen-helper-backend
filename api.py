"""Kitchen Helper API"""
import fastapi
import features.health
import features.image_processing

app = fastapi.FastAPI()
app.include_router(features.health.router, prefix='/health')
app.include_router(features.image_processing.routerl, prefix='/images')
