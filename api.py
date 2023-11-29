"""Kitchen Helper API"""
import fastapi

import features.health
import features.users
import features.recipes

import uvicorn

from fastapi.middleware.cors import CORSMiddleware

import configuration

cors_config = configuration.CorsSettings()



app = fastapi.FastAPI()

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_config.allow_origins,
    allow_methods=cors_config.allow_methods,
    allow_headers=cors_config.allow_headers,
)


app.include_router(features.health.router, prefix='/health')
app.include_router(features.users.router, prefix='/users')
app.include_router(features.recipes.category_router, prefix='/categories')
app.include_router(features.recipes.recipes_router, prefix='/recipes')

if __name__ == '__main__':
    uvicorn.run(app)
