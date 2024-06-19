from datetime import datetime
from typing import List
import uuid
from pydantic import BaseModel, EmailStr, constr


class UserBaseSchema(BaseModel):
    username: str
    email: EmailStr
    password: str

    class Config:
        orm_mode = True


class CreateUserSchema(UserBaseSchema):
    password: constr(min_length=8)
    passwordConfirm: str
    role: str = 'user'
    verified: bool = False


class LoginUserSchema(BaseModel):
    email: EmailStr
    password: constr(min_length=8)


class UserResponse(UserBaseSchema):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class FilteredUserResponse(UserBaseSchema):
    id: uuid.UUID


class CompetencyBaseSchema(BaseModel):
    title: str

    class Config:
        orm_mode = True


class CompetencyResponse(CompetencyBaseSchema):
    id: int


class CompetencyCreateSchema(CompetencyBaseSchema):
    pass


class RecommendationBaseSchema(BaseModel):
    question_id: uuid.UUID
    content: str

    class Config:
        orm_mode = True


class QuestionBaseSchema(BaseModel):
    question: str
    competency_id: uuid.UUID
    accurate_answers: List[str]

    class Config:
        orm_mode = True


class QuestionResponse(QuestionBaseSchema):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class CreateQuestionSchema(QuestionBaseSchema):
    pass


class UpdateQuestionSchema(QuestionBaseSchema):
    question: str
    competency_id: uuid.UUID
    accurate_answers: List[str]


class ListQuestionResponse(QuestionBaseSchema):
    status: str
    results: int
    questions: List[QuestionResponse]


class AnswerBaseSchema(BaseModel):
    content: str
    grade: int
    question_id: uuid.UUID | None = None
    user_id: uuid.UUID | None = None

    class Config:
        orm_mode = True


class AnswerResponse(AnswerBaseSchema):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class CreateAnswerSchema(AnswerBaseSchema):
    pass


class UpdateAnswerSchema(BaseModel):
    question_id: uuid.UUID
    content: str
    user_id: uuid.UUID | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        orm_mode = True


class ListAnswerResponse(BaseModel):
    status: str
    results: int
    answers: List[AnswerResponse]
