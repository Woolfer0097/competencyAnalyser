from pydantic import BaseModel, EmailStr, Field, condecimal
from typing import Optional, List
from uuid import UUID
from datetime import datetime


# Base schemas

class BusinessTypeBase(BaseModel):
    title: str = Field(..., max_length=255)


class VacancyBase(BaseModel):
    title: str


# Response schemas

class BusinessTypeOut(BusinessTypeBase):
    id: UUID
    vacancies: List['VacancyOut'] = []

    class Config:
        orm_mode = True


class VacancyOut(VacancyBase):
    id: UUID
    business_types: List[BusinessTypeOut] = []

    class Config:
        orm_mode = True


# Request schemas

class BusinessTypeCreate(BusinessTypeBase):
    pass


class BusinessTypeUpdate(BusinessTypeBase):
    title: Optional[str] = Field(None, max_length=255)


class VacancyCreate(VacancyBase):
    business_type_ids: List[UUID]


class VacancyUpdate(BaseModel):
    title: Optional[str] = None
    business_type_ids: Optional[List[UUID]] = None


# Other schemas (Answer, User, Question, Competency)

# Answer schemas
class AnswerBase(BaseModel):
    content: str
    grade: int


class AnswerOut(AnswerBase):
    id: UUID
    question_id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class AnswerCreate(AnswerBase):
    question_id: UUID
    user_id: UUID


class AnswerResponse(BaseModel):
    id: UUID
    question_id: UUID
    user_id: UUID
    content: str
    grade: condecimal(gt=-1, le=5)
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class AnswerListResponse(BaseModel):
    status: str
    results: int
    answers: List[AnswerResponse]


class AnswerUpdate(BaseModel):
    content: Optional[str] = None
    grade: Optional[int] = None


# User schemas
class UserBase(BaseModel):
    email: EmailStr


class UserOut(UserBase):
    id: UUID
    answers: Optional[str] = None
    recommendations: Optional[str] = None

    class Config:
        orm_mode = True


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    answers: Optional[str] = None
    recommendations: Optional[str] = None


# Question schemas
class QuestionBase(BaseModel):
    content: str


class QuestionOut(QuestionBase):
    id: UUID
    competency_id: UUID

    class Config:
        orm_mode = True


class QuestionCreate(QuestionBase):
    competency_id: UUID


class QuestionUpdate(BaseModel):
    content: Optional[str] = None
    competency_id: Optional[UUID] = None


# Competency schemas
class CompetencyBase(BaseModel):
    title: str


class CompetencyOut(CompetencyBase):
    id: UUID

    class Config:
        orm_mode = True


class CompetencyCreate(CompetencyBase):
    pass


class CompetencyUpdate(BaseModel):
    title: Optional[str] = None
