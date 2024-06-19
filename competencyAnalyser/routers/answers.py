import uuid
from ..api import models, schemas
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, APIRouter, Response
from competencyAnalyser.db.database import get_db
from ..constants import ADMIN_ID
from json import *
#
# from openai import OpenAI
# client = OpenAI(api_key='sk-proj-izT2eRidNinyxa9FNHCnT3BlbkFJdapIfsWQY55DJLaP2pgF')

router = APIRouter()


@router.get('/', response_model=schemas.ListAnswerResponse)
def get_answers(db: Session = Depends(get_db)):
    answers = db.query(models.Answer).group_by(models.Answer.id).all()
    return {'status': 'success', 'results': len(answers), 'answers': answers}


@router.post('/', status_code=status.HTTP_201_CREATED, response_model=schemas.AnswerResponse)
def create_answer(id: str, answer: schemas.CreateAnswerSchema, db: Session = Depends(get_db)):
    content, grade, question_id, user_id = answer.dict().values()
    # print(content, grade, user_id, question_id)

    user_query = db.query(models.User).filter(models.User.id == user_id).first()
    if not user_query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='User not found')
    else:
        if user_query.answers:
            answers = loads(user_query.answers)
            answers[id] = content
            user_query.answers = dumps(answers)
        else:
            answers = {id: content}
            user_query.answers = dumps(answers)

    # AI grading

    # if grade <= BAD_GRADE:
        # recommendations forming
        # recommendations = {}
        # user_query.recommendations =

    new_answer = models.Answer(**answer.dict())
    new_answer.id = uuid.UUID(id)

    db.add(new_answer)
    db.commit()
    db.refresh(new_answer)
    return new_answer


@router.put('/{id}', response_model=schemas.AnswerResponse)
def update_answer(id: str, answer: schemas.UpdateAnswerSchema, db: Session = Depends(get_db)):
    answer_query = db.query(models.Answer).filter(models.Answer.id == id)
    updated_answer = answer_query.first()

    if not updated_answer:
        raise HTTPException(status_code=status.HTTP_200_OK,
                            detail=f'No post with this id: {id} found')
    if updated_answer.user_id != uuid.UUID(ADMIN_ID):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='You are not allowed to perform this action')
    answer.user_id = ADMIN_ID
    answer_query.update(answer.dict(exclude_unset=True), synchronize_session=False)
    db.commit()
    return updated_answer


@router.get('/{id}', response_model=schemas.AnswerResponse)
def get_answer(id: str, db: Session = Depends(get_db), ):
    answer = db.query(models.Answer).filter(models.Answer.id == id).first()
    if not answer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No answer with this id: {id} found")
    return answer


@router.delete('/{id}')
def delete_answer(id: str, db: Session = Depends(get_db)):
    answer_query = db.query(models.Answer).filter(models.Answer.id == id)
    answer = answer_query.first()

    if not answer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'No answer with this id: {id} found')

    if str(answer.user_id) != ADMIN_ID:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='You are not allowed to perform this action')

    answer_query.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
