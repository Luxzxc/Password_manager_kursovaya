from app.database import Base, engine, get_db
from fastapi import Depends, FastAPI
import uvicorn
from app.models import User, PasswordRecord

app = FastAPI(
    title="Защищённый Менеджер Паролей",
    description="Курсовая работа по дисциплине Основы программирования",
    version="0.0.1"
)

Base.metadata.create_all(bind=engine)

@app.get("/")
async def root():
    return {"message": "Hello World! Сервер работает :)"}

@app.get("/test-db")
def test_db(db=Depends(get_db)):
    users_count = db.query(User).count()
    return {"status": "БД работает", "users_in_db": users_count}



if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)