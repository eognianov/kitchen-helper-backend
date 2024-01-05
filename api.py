"""Kitchen Helper API"""
import fastapi.staticfiles

import features.health
import features.images
import features.users
import features.recipes
import multiprocessing
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
import configuration
import khLogging
from features.users.tasks import app_seeder
from features.recipes.tasks import seed_recipe_categories

CPUS = multiprocessing.cpu_count()
config = configuration.Config()


logging = khLogging.Logger('api')
app = fastapi.FastAPI(docs_url='/api/docs', redoc_url='/api/redoc', openapi_url='/api/openai.json')
cors_config = configuration.CorsSettings()

app.add_middleware(
    CORSMiddleware,
    **cors_config.__dict__,
)


app.include_router(features.health.router, prefix='/api/health')
app.include_router(features.users.user_router, prefix='/api/users')
app.include_router(features.users.role_router, prefix='/api/roles')
app.include_router(features.recipes.category_router, prefix='/api/categories')
app.include_router(features.recipes.recipes_router, prefix='/api/recipes')
app.include_router(features.recipes.ingredient_router, prefix='/api/ingredients')
app.include_router(features.images.router, prefix='/api/images')
app.mount('/media', fastapi.staticfiles.StaticFiles(directory=configuration.MEDIA_PATH))


@app.on_event("startup")
def startup_event():
    app_seeder.apply_async(link=seed_recipe_categories.si())


if __name__ == '__main__':
    uvicorn.run(
        "api:app",
        reload=config.running_on_dev,
        workers=CPUS,
        log_config=khLogging.UVICORN_LOG_CONFIG,
        port=8000,
        host='0.0.0.0',
    )
