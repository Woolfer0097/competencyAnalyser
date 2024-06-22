import uuid

from competencyAnalyser.api.models import Competency, Question
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, APIRouter, Response
from competencyAnalyser.db.database import get_db, init_db

router = APIRouter()
FILE_PATH = r'C:\Users\Woolfer0097\PycharmProjects\CompetencyAnalyser\competencyAnalyser\parsing\texts\to_parse.txt'

@app.get("/")
def parse(db: Session = Depends(get_db)):
    with open(FILE_PATH, 'r', encoding="utf-8") as f:
        data = f.read()

    chunks = data.split("&")

    for chunk in chunks:
        competency, questions = chunk.split("=")
        print(competency, questions.split(";"))

        competencies = db.query(Competency).filter(Competency.title == competency).all()
        print(competencies)

        competency_id = uuid.uuid4()
        new_competency = Competency(id=competency_id, title=competency)

        db.add(new_competency)

        for question in questions:
            new_question = Question(content=question, competency_id=competency_id)
            db.add(new_question)
    db.commit()
    db.refresh(new_question)


if __name__ == '__main__':
    init_db()
    main()
