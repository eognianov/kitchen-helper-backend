"""Kitchen Helper API"""
import fastapi
import features.health
import features.recipes

app = fastapi.FastAPI()
app.include_router(features.health.router, prefix='/health')
app.include_router(features.recipes.category_router, prefix='/categoires')