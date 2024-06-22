import uuid
from ..api import models, schemas
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, APIRouter, Response
from competencyAnalyser.db.database import get_db
from ..api.models import Competency, Question
from ..constants import ADMIN_ID
from json import loads, dumps

router = APIRouter()


@router.get('/', response_model=schemas.AnswerListResponse)
def get_answers(db: Session = Depends(get_db)):
    answers = db.query(models.Answer).group_by(models.Answer.id).all()
    return {'status': 'success', 'results': len(answers), 'answers': answers}


@router.post('/', status_code=status.HTTP_201_CREATED, response_model=schemas.AnswerResponse)
def create_answer(answer: schemas.AnswerCreate, db: Session = Depends(get_db)):
    content = answer.content
    grade = answer.grade
    question_id = answer.question_id
    user_id = answer.user_id

    user_query = db.query(models.User).filter(models.User.id == user_id).first()
    if not user_query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='User not found')

    if user_query.answers:
        answers = loads(user_query.answers)
        answers[str(uuid.uuid4())] = content
        user_query.answers = dumps(answers)
    else:
        answers = {str(uuid.uuid4()): content}
        user_query.answers = dumps(answers)

    new_answer = models.Answer(
        id=uuid.uuid4(),
        content=content,
        grade=grade,
        question_id=question_id,
        user_id=user_id
    )

    db.add(new_answer)
    db.commit()
    db.refresh(new_answer)
    return {'status': 'success', 'answer': new_answer}


@router.put('/{id}', response_model=schemas.AnswerResponse)
def update_answer(id: str, answer: schemas.AnswerUpdate, db: Session = Depends(get_db)):
    answer_query = db.query(models.Answer).filter(models.Answer.id == id)
    existing_answer = answer_query.first()

    if not existing_answer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'No answer with this id: {id} found')

    if existing_answer.user_id != uuid.UUID(ADMIN_ID):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='You are not allowed to perform this action')

    answer_query.update(answer.dict(exclude_unset=True), synchronize_session=False)
    db.commit()
    db.refresh(existing_answer)
    return {'status': 'success', 'answer': existing_answer}


@router.get('/{id}', response_model=schemas.AnswerResponse)
def get_answer(id: str, db: Session = Depends(get_db)):
    answer = db.query(models.Answer).filter(models.Answer.id == id).first()
    if not answer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No answer with this id: {id} found")
    return {'status': 'success', 'answer': answer}


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