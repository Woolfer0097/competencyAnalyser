#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import uuid

from fastapi import FastAPI, APIRouter, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from competencyAnalyser.api.models import Competency, Question, Vacancy, BusinessType
from competencyAnalyser.config import settings
from competencyAnalyser.db.database import init_db, get_db
from competencyAnalyser.routers import answers, questions, users, vacancies, business_types, competencies
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from competencyAnalyser.config import CLIENT_ID, CLIENT_SECRET
from authlib.integrations.starlette_client import OAuth, OAuthError
from fastapi.staticfiles import StaticFiles

templates = Jinja2Templates(directory="templates")

app = FastAPI()

# app.add_middleware(SessionMiddleware, secret_key ="secret_key_mega_string_brbrbrbr")
# app.mount("/templates", StaticFiles(directory="templates"), name="templates")

oauth = OAuth()
oauth.register(
    name = 'google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_id = CLIENT_ID,
    client_secret = CLIENT_SECRET,
    client_kwargs={
        'scope':'email openid profile',
        'redirect_url' : 'http://localhost:8000/auth'
    }
)


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

app.include_router(answers.router, prefix="/answers", tags=["Answers"])
app.include_router(questions.router, prefix="/questions", tags=["Questions"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(vacancies.router, prefix="/vacancies", tags=["Vacancies"])
app.include_router(business_types.router, prefix="/business-types", tags=["Business Types"])
app.include_router(competencies.router, prefix="/competencies", tags=["Competencies"])

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
async def quiz(request: Request):
    return templates.TemplateResponse("general_pages/quiz.html", {
        "request": request
    })
@app.get("/hr_auth_page")
async def auth(request: Request):

    user = request.session.get('user')
    if user:
        return RedirectResponse('welcome')

    return templates.TemplateResponse("general_pages/hr_auth_page.html", {
        "request": request
    })

@app.get('/welcome')
def welcome(request: Request):
    user = request.session.get('user')
    if not user:
        return RedirectResponse('/')
    return templates.TemplateResponse(
        name='welcome.html',
        context={'request': request, 'user': user}
    )


@app.get("/login")
async def login(request: Request):
    url = request.url_for('auth')
    return await oauth.google.authorize_redirect(request, url)


@app.get('/auth')
async def auth(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)
    except OAuthError as e:
        return templates.TemplateResponse(
            name='error.html',
            context={'request': request, 'error': e.error}
        )
    user = token.get('userinfo')
    if user:
        request.session['user'] = dict(user)
    return RedirectResponse('welcome')


@app.get('/logout')
def logout(request: Request):
    request.session.pop('user')
    request.session.clear()
    return RedirectResponse('/')


FILE_PATH = r'competencyAnalyser/parsing/texts/to_parse.txt'
FILE_PATH_2 = r'competencyAnalyser/parsing/texts/to_parse_bv.txt'


@app.get("/parse_qc")
def parse_questions_with_competencies(db: Session = Depends(get_db)):
    with open(FILE_PATH, 'r', encoding="utf-8") as f:
        data = f.read()

    chunks = data.split("&")

    for chunk in chunks:
        competency, questions = chunk.split("=")
        questions_list = questions.split(";")

        existing_competency = db.query(Competency).filter(Competency.title == competency).first()
        if existing_competency:
            competency_id = existing_competency.id
        else:
            competency_id = uuid.uuid4()
            new_competency = Competency(id=competency_id, title=competency)
            db.add(new_competency)
            db.commit()
            db.refresh(new_competency)

        for question in questions_list:
            new_question = Question(content=question, competency_id=competency_id)
            db.add(new_question)
            db.commit()
            db.refresh(new_question)

    return {"status": "success", "message": "Parsing and database update completed"}


@app.get("/parse_bv")
def parse_business_with_vacancies(db: Session = Depends(get_db)):
    with open(FILE_PATH_2, 'r', encoding="utf-8") as f:
        data = f.read()

    chunks = data.split(";")

    for chunk in chunks:
        if not chunk.strip():  # Skip empty lines
            continue

        parts = chunk.split(":")
        vacancy_title = parts[0].strip()
        business_types_list = [b.strip() for b in parts[1:] if b.strip()]

        # Check if the vacancy already exists in the database
        existing_vacancy = db.query(Vacancy).filter_by(title=vacancy_title).first()

        if not existing_vacancy:
            new_vacancy = Vacancy(title=vacancy_title)
            db.add(new_vacancy)
            db.commit()
            db.refresh(new_vacancy)
        else:
            new_vacancy = existing_vacancy

        # Associate business types with the vacancy
        for business_type_title in business_types_list:
            existing_business_type = db.query(BusinessType).filter_by(title=business_type_title).first()

            if not existing_business_type:
                new_business_type = BusinessType(title=business_type_title)
                db.add(new_business_type)
                db.commit()
                db.refresh(new_business_type)
            else:
                new_business_type = existing_business_type

            # Check if the association already exists
            if new_business_type not in new_vacancy.business_types:
                new_vacancy.business_types.append(new_business_type)

            db.commit()

    return {"status": "success", "message": "Parsing and database update completed"}


# def main():
#     import uvicorn
#     uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
#
#
# if __name__ == '__main__':
#     init_db()
#     main()
