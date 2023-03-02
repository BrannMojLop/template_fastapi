from fastapi import APIRouter

Index = APIRouter()

@Index.get('/')
def index():
    return {"message": "Hello World, API created by Brandon M."}
