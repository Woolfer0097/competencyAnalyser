from fastapi import FastAPI, APIRouter, Request
from fastapi.middleware.cors import CORSMiddleware
from competencyAnalyser.config import settings
from competencyAnalyser.db.database import init_db
from competencyAnalyser.routers import answers
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from competencyAnalyser.config import CLIENT_ID, CLIENT_SECRET
from authlib.integrations.starlette_client import OAuth, OAuthError
from fastapi.staticfiles import StaticFiles

templates = Jinja2Templates(directory="templates")

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key ="secret_key_mega_string_brbrbrbr")
app.mount("/static", StaticFiles(directory="static"), name="static")

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