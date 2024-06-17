import uuid
from .. import schemas, models
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, APIRouter, Response
from ..database import get_db
from ..constants import ADMIN_ID

router = APIRouter()


@router.get('/', response_model=schemas.ListQuestionResponse)
def get_questions(db: Session = Depends(get_db)):
    questions = db.query(models.Question).group_by(models.Question.id).all()
    return {'status': 'success', 'results': len(questions), 'questions': questions}


@router.post('/', status_code=status.HTTP_201_CREATED, response_model=schemas.QuestionResponse)
def create_question(id: str, question: schemas.CreateQuestionSchema, db: Session = Depends(get_db)):
    new_question = models.Question(**question.dict())
    new_question.id = uuid.UUID(id)

    db.add(new_question)
    db.commit()
    db.refresh(new_question)
    return new_question


@router.put('/{id}', response_model=schemas.QuestionResponse)
def update_question(id: str, question: schemas.UpdateQuestionSchema, db: Session = Depends(get_db)):
    question_query = db.query(models.Question).filter(models.Question.id == id)
    updated_question = question_query.first()

    if not updated_question:
        raise HTTPException(status_code=status.HTTP_200_OK,
                            detail=f'No post with this id: {id} found')
    if updated_question.user_id != uuid.UUID(ADMIN_ID):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='You are not allowed to perform this action')
    question.user_id = ADMIN_ID
    question_query.update(question.dict(exclude_unset=True), synchronize_session=False)
    db.commit()
    return updated_question


@router.get('/{id}', response_model=schemas.QuestionResponse)
def get_question(id: str, db: Session = Depends(get_db), ):
    question = db.query(models.Question).filter(models.Question.id == id).first()
    if not question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No question with this id: {id} found")
    return question


@router.delete('/{id}')
def delete_question(id: str, db: Session = Depends(get_db)):
    question_query = db.query(models.Question).filter(models.Question.id == id)
    question = question_query.first()
    if not question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'No question with this id: {id} found')

    if str(question.user_id) != ADMIN_ID:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='You are not allowed to perform this action')
    question_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
