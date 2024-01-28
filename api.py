"""Kitchen Helper API"""
from contextlib import asynccontextmanager

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
import threading
from features.users.grpc_server import serve as users_grpc
from features.images.grpc_server import serve as images_grpc
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.sdk.trace.export import BatchSpanProcessor


resource = Resource(attributes={SERVICE_NAME: "kitchen-helper"})
trace_provider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(OTLPSpanExporter(endpoint="http://jaeger:4318/v1/traces"))
trace_provider.add_span_processor(processor)
trace.set_tracer_provider(trace_provider)

CPUS = multiprocessing.cpu_count()
config = configuration.Config()

logging = khLogging.Logger('api')


@asynccontextmanager
async def startup_shutdown_lifespan(app: fastapi.FastAPI):
    """
    Startup and shutdown lifespan for the app
    :param app:
    :return:
    """
    try:
        # app_seeder.apply_async(link=seed_recipe_categories.si()) # disabled until burning category ids is fixed
        users_grpc_thread = threading.Thread(target=users_grpc)
        users_grpc_thread.daemon = True
        users_grpc_thread.start()
        images_grpc_thread = threading.Thread(target=images_grpc)
        images_grpc_thread.daemon = True
        images_grpc_thread.start()
    except Exception:
        error_message = "Seed task is not able to run!"
        if config.running_on_dev:
            logging.warning(error_message)
        else:
            logging.exception(error_message)
    yield


app = fastapi.FastAPI(
    docs_url='/api/docs', redoc_url='/api/redoc', openapi_url='/api/openai.json', lifespan=startup_shutdown_lifespan
)
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
app.mount('/api/media', fastapi.staticfiles.StaticFiles(directory=configuration.MEDIA_PATH))

FastAPIInstrumentor.instrument_app(app)

if __name__ == '__main__':
    uvicorn.run(
        "api:app",
        reload=config.running_on_dev,
        workers=CPUS,
        log_config=khLogging.UVICORN_LOG_CONFIG,
        port=8000,
        host='0.0.0.0',
    )
