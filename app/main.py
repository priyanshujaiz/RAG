from fastapi import FastAPI
from app.api.auth.router import router as auth_router
from app.api.users.router import router as users_router
from app.api.workspaces.router import router as workspaces_router
from app.api.documents.router import router as documents_router
from app.api.projects.router import router as projects_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(workspaces_router)
app.include_router(documents_router)
app.include_router(projects_router)