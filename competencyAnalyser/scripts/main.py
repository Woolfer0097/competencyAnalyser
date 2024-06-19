from fastapi import FastAPI, APIRouter, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from competencyAnalyser.config import settings
from competencyAnalyser.db.database import init_db
from competencyAnalyser.routers import answers
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")

app = FastAPI()

origins = [
    settings.CLIENT_ORIGIN,
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app.include_router(questions.router, tags=["Questions"], prefix="/api/questions")
app.include_router(answers.router, tags=['Answers'], prefix='/api/answers')

general_pages_router = APIRouter()


@general_pages_router.get("/")
async def home(request: Request):
    return templates.TemplateResponse(
        "general_pages/index.html",
        {
            "request": request
        })


@app.on_event("startup")
def on_startup():
    init_db()


@app.get('/api/healthchecker')
def root():
    return {'message': 'Hello World'}


@app.get("/quiz")
async def quiz(answers: list = Form()):
    questions: list[str] = generate_questions()
    return templates.TemplateResponse("general_pages/quiz.html", {
        "questions": questions
    })


def generate_questions():
    pass
