import json
from typing import List
from urllib.parse import urlencode
from random import choice

import fastapi
from authlib.integrations.base_client import OAuthError
from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter, Request, FastAPI, Depends, Body
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from openai import BaseModel
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import JSONResponse, Response

from competencyAnalyser.additional_scripts.main import get_random_questions
from competencyAnalyser.routers.ai import *
from competencyAnalyser.api import models
from competencyAnalyser.config import CLIENT_ID, CLIENT_SECRET
from competencyAnalyser.db.database import get_db

templates = Jinja2Templates(directory="templates")
# app.add_middleware(SessionMiddleware, secret_key ="secret_key_mega_string_brbrbrbr")
# app.mount("/templates", StaticFiles(directory="templates"), name="templates")

oauth = OAuth()
oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    client_kwargs={
        'scope': 'email openid profile',
        'redirect_url': 'http://localhost:8000/auth'
    }
)

router = APIRouter()


@router.get("/")
async def home(request: Request, db: Session = Depends(get_db)):
    vacancies = [[str(vacancy.id), vacancy.title] for vacancy in db.query(models.Vacancy).all()]
    # print(vacancies)
    return templates.TemplateResponse(
        "general_pages/index.html",
        {
            "request": request, "vacancies": vacancies,
        })


@router.get("/quiz")
async def quiz(request: Request, db: Session = Depends(get_db)):
    buttons = request.query_params
    # print(buttons.values())
    vacancies = [vacancy for vacancy in buttons.values()]
    # print(vacancies)
    competencies_list = await competencies_generate(vacancies_list=vacancies)
    competencies_id_list = db.query(models.Competency).filter(models.Competency.title.in_(list(competencies_list.strip('[]')))).options(load_only("id")).all()

    questions = await db.query(models.Question).filter(models.Question.competency_id.in_(competencies_id_list)).get("content")
    print(questions)

    # return templates.TemplateResponse(
    #     "general_pages/quiz.html", {
    #         "request": request,
    #         "questions": questions,
    #     })


@router.post("/quiz/redirect")
async def handle_button_states(data=Body()):
    query_params = {}
    for i in data["selected_buttons"]:
        query_params[i['id']] = i['text']

    return fastapi.responses.RedirectResponse(
        '/quiz?' + urlencode(query_params),
        status_code=status.HTTP_302_FOUND)


@router.get("/quiz/redirect")
async def hui(request: Request):
    return fastapi.responses.RedirectResponse(
        '/quiz',
        status_code=status.HTTP_302_FOUND)


@router.get("/hr_auth_page")
async def auth(request: Request):
    user = request.session.get('user')
    if user:
        return RedirectResponse('welcome')

    return templates.TemplateResponse(
        "general_pages/hr_auth_page.html", {
            "request": request
        })


@router.get('/welcome')
def welcome(request: Request):
    user = request.session.get('user')
    if not user:
        return RedirectResponse('/')
    return templates.TemplateResponse(
        name='welcome.html',
        context={'request': request, 'user': user}
    )


@router.get("/login")
async def login(request: Request):
    url = request.url_for('auth')
    return await oauth.google.authorize_redirect(request, url)


@router.get('/auth')
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


@router.get('/logout')
def logout(request: Request):
    request.session.pop('user')
    request.session.clear()
    return RedirectResponse('/')
