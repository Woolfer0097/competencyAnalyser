from competencyAnalyser.database import init_db
import uuid
from .. import schemas, models
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, APIRouter, Response
from ..database import get_db

router = APIRouter()





if __name__ == '__main__':
    init_db()
    main()
