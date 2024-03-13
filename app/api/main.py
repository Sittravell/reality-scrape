from fastapi import FastAPI, Depends
from dotenv import dotenv_values
import sys
import uvicorn
cfg=dotenv_values()
sys.path.append(cfg['ROOT']+'/app/api')
from app.database.engine import Session
from app.database.helpers import retrieve_news

app = FastAPI()

def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()

@app.get("/news")
async def news(db: Session = Depends(get_db)):
    return retrieve_news(db)

if __name__ == '__main__':
    config = uvicorn.Config("main:app", port=8000, log_level="info")
    server = uvicorn.Server(config)
    server.run()