from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from competencyAnalyser.config import settings
from competencyAnalyser.database import init_db
from competencyAnalyser.routers import answers, questions

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


@app.on_event("startup")
def on_startup():
    init_db()


@app.get('/api/healthchecker')
def root():
    return {'message': 'Hello World'}
