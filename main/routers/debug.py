from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.get("/fail")
def fail() -> None:
    raise HTTPException(status_code=400, detail="Something went wrong?")


@router.get("/sentry-debug")
def trigger_error() -> float:
    return 1 / 0
