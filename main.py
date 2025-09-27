from fastapi import FastAPI
from app.routers import auth, users, posts
from app.core.exceptions import ExceptionHandlerMiddleware
from app.core.config import settings
from app.core.middleware import LoggingMiddleware
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:55000", "https://your-frontend.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.add_middleware(LoggingMiddleware)

app.add_middleware(LoggingMiddleware)

print("🔑 SECRET_KEY:", settings.SECRET_KEY)

app.add_middleware(ExceptionHandlerMiddleware)


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(posts.router)


