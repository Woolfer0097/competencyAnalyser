from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..api import models, schemas
from competencyAnalyser.db.database import get_db

from random import sample

from ..routers.questions import get_questions


router = APIRouter()


def unpack(question):
    return question[0]


@router.get('/random_questions', response_model=List[schemas.QuestionOut])
def get_random_questions(vacancies: List[str], db: Session = Depends(get_db)):
    questions = [unpack(question) for question in db.query(models.Question).filter(models.Question.vacancy.in_(vacancies)).all()]
    return sample(questions, 5)


def parse():
    with open("parsing/texts/to_parse.txt", 'r', encoding="utf-8") as file:
        examples = file.read()
        chunk = examples.split('&')
        for i in chunk:
            print(i.split("=")[0], end=";")
