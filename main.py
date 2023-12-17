from fastapi import FastAPI
import uvicorn

from api.auth import router as auth_router
from api.group_chats import router as group_chats_router
from api.group_chats_settings import router as chats_settings_router


app = FastAPI()
app.include_router(auth_router)
app.include_router(group_chats_router)
app.include_router(chats_settings_router)


if __name__ == "__main__":
    uvicorn.run("main:app")

