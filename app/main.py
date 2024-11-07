from contextlib import asynccontextmanager
from fastapi import FastAPI
import databases
import sqlalchemy



DATABASE_URL = "postgresql://postgres:password@db:5432/postgres"

database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect()
    yield
    await database.disconnect()

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def read_root():
    return {"Hello": "World"}

