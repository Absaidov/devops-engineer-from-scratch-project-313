from fastapi import FastAPI, HTTPException

app = FastAPI()


@app.get("/ping")
def ping():
    return "pong"


@app.get("/fail")
def fail():
    raise HTTPException(status_code=400, detail="Что-то пошло не так")