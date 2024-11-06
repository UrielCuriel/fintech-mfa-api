from fastapi import FastAPI
import databases
import sqlalchemy

app = FastAPI()

DATABASE_URL = "postgresql://postgres:password@db:5432/postgres"

database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.get("/")
async def read_root():
    return {"Hello": "World"}

