"""Kitchen Helper API"""
import fastapi
import fastapi.staticfiles

import features.health
import features.images
import features.users
import features.recipes

import multiprocessing
cpus = multiprocessing.cpu_count()

import uvicorn

from fastapi.middleware.cors import CORSMiddleware

import configuration
import khLogging


logging = khLogging.Logger('api')

app = fastapi.FastAPI()

cors_config = configuration.CorsSettings()

app.add_middleware(
    CORSMiddleware,
    **cors_config.__dict__,
)


app.include_router(features.health.router, prefix='/health')
app.include_router(features.users.user_router, prefix='/users')
app.include_router(features.users.role_router, prefix='/roles')
app.include_router(features.recipes.category_router, prefix='/categories')
app.include_router(features.recipes.recipes_router, prefix='/recipes')
app.include_router(features.images.router, prefix='/images')
# app.mount('/media', fastapi.staticfiles.StaticFiles(directory='media'))

if __name__ == '__main__':
    uvicorn.run("api:app", workers=cpus, log_config=khLogging.UVICORN_LOG_CONFIG, port=8000, host='0.0.0.0')
