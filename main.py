from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Load environment variables from .env file
load_dotenv()

from auth import router as auth_router
from models import init_db
from student_routes import router as student_router
from teacher_routes import router as teacher_router

app = FastAPI(title="Adaptive Learning System POC")

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@app.on_event("startup")
def _startup():
    init_db()

app.include_router(auth_router)
app.include_router(teacher_router)
app.include_router(student_router)


@app.get("/")
def root(request: Request):
    accept = request.headers.get("accept") or ""
    if "text/html" in accept:
        return templates.TemplateResponse(
            "home.html",
            {
                "request": request,
                "page_title": "Adaptive Learning POC",
                "subtitle": "Login to continue as teacher or student.",
                "role": None,
                "user_email": None,
            },
        )
    return {"status": "Adaptive Learning POC running"}
