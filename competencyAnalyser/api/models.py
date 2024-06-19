import uuid
from competencyAnalyser.db.database import Base
from sqlalchemy import TIMESTAMP, Column, ForeignKey, String, text, Text, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = 'users'
    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False,
                default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    answers = Column(Text, nullable=True)  # JSON {question_id: question.content}
    recommendations = Column(Text, nullable=True)  # JSON {question_id: recommendations.content}
    answer = relationship('Answer', backref='user', uselist=False)


class Competency(Base):
    __tablename__ = 'competencies'
    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False,)
    title = Column(String(255), unique=True, nullable=False)

    question = relationship('Question', backref='competency', uselist=False)


class Question(Base):
    __tablename__ = 'questions'
    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False,)
    competency_id = Column(UUID(as_uuid=True), ForeignKey('competencies.id'),)
    content = Column(Text, nullable=False)

    answer = relationship('Answer', backref='question', uselist=False)
    recommendation = relationship('Recommendation', backref='question', uselist=False)


class Answer(Base):
    __tablename__ = 'answers'
    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False,)
    question_id = Column(UUID(as_uuid=True), ForeignKey('questions.id'),)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'),)

    content = Column(Text, nullable=False)
    grade = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text("now()"))
    updated_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text("now()"))


class Recommendation(Base):
    __tablename__ = 'recommendations'
    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False,)
    question_id = Column(UUID(as_uuid=True), ForeignKey('questions.id'),)
    content = Column(Text, nullable=False)


class Vacancy(Base):
    __tablename__ = 'vacancies'
    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False,)
    title = Column(String(255), unique=True, nullable=False)
    competencies = Column(Text, nullable=True)
