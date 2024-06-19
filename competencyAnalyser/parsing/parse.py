from competencyAnalyser.db.database import init_db
from fastapi import APIRouter

router = APIRouter()





if __name__ == '__main__':
    init_db()
    main()
