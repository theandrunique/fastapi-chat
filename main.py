from fastapi import FastAPI
import uvicorn

from api.auth import router as auth_router
from api.messenger import router as messenger_router


app = FastAPI()
app.include_router(auth_router)
app.include_router(messenger_router)


if __name__ == "__main__":
    uvicorn.run("main:app")

