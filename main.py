from fastapi import FastAPI
import uvicorn

app = FastAPI()

import settings
import session
import user
import article
import comment
import search

if __name__ == "__main__":
    uvicorn.run("main:app", port = settings.web_server["port"], host = settings.web_server["host"], reload = True, ssl_keyfile="./cert/key.pem", ssl_certfile="./cert/cert.pem")

