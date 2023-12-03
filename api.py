"""Kitchen Helper API"""
import fastapi
import fastapi.staticfiles

import features.health
import features.images
import features.users
import features.recipes

import uvicorn

from fastapi.middleware.cors import CORSMiddleware

import configuration
import khLogging

config = configuration.Config()

logging = khLogging.Logger('api')

app = fastapi.FastAPI()

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.cors.allow_origins,
    allow_methods=config.cors.allow_methods,
    allow_headers=config.cors.allow_headers,
)


app.include_router(features.health.router, prefix='/health')
app.include_router(features.users.user_router, prefix='/users')
app.include_router(features.users.role_router, prefix='/roles')
app.include_router(features.recipes.category_router, prefix='/categories')
app.include_router(features.recipes.recipes_router, prefix='/recipes')
app.include_router(features.images.router, prefix='/images')
# app.mount('/media', fastapi.staticfiles.StaticFiles(directory='media'))

if __name__ == '__main__':
    uvicorn.run(app, log_config=khLogging.UVICORN_LOG_CONFIG)
