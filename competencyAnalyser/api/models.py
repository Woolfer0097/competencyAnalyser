import uuid
from competencyAnalyser.db.database import Base
from sqlalchemy import TIMESTAMP, Column, ForeignKey, String, text, Text, Integer, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

# Association Table for many-to-many relationship between Vacancy and BusinessType
vacancy_business_type = Table(
    'vacancy_business_type',
    Base.metadata,
    Column('vacancy_id', UUID(as_uuid=True), ForeignKey('vacancies.id'), primary_key=True),
    Column('business_type_id', UUID(as_uuid=True), ForeignKey('business_types.id'), primary_key=True)
)


class User(Base):
    __tablename__ = 'users'
    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    answers = Column(Text, nullable=True)  # JSON {question_id: question.content}
    recommendations = Column(Text, nullable=True)  # JSON {question_id: recommendations.content}
    answer = relationship('Answer', backref='user', uselist=False)


class Competency(Base):
    __tablename__ = 'competencies'
    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
    title = Column(String(255), unique=True, nullable=False)
    question = relationship('Question', backref='competency', uselist=False)


class Question(Base):
    __tablename__ = 'questions'
    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
    competency_id = Column(UUID(as_uuid=True), ForeignKey('competencies.id'))
    content = Column(Text, nullable=False)
    answer = relationship('Answer', backref='question', uselist=False)


class Answer(Base):
    __tablename__ = 'answers'
    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
    question_id = Column(UUID(as_uuid=True), ForeignKey('questions.id'))
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    content = Column(Text, nullable=False)
    grade = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))


class BusinessType(Base):
    __tablename__ = 'business_types'
    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
    title = Column(String(255), unique=True, nullable=False)


class Vacancy(Base):
    __tablename__ = 'vacancies'
    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
    title = Column(String(255), unique=True, nullable=False)

    business_types = relationship('BusinessType', secondary=vacancy_business_type, backref='vacancy')
