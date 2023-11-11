"""Kitchen Helper API"""
import fastapi
import features.health
import features.recipes
import uvicorn

app = fastapi.FastAPI()
app.include_router(features.health.router, prefix='/health')
app.include_router(features.recipes.category_router, prefix='/categoires')
app.include_router(features.recipes.recipes_router, prefix='/recipes')
app.include_router(features.recipes.instructions_router, prefix='/instructions')

if __name__ == '__main__':
    uvicorn.run(app)
