from fastapi import FastAPI
import uvicorn

app = FastAPI()

import auth
import roles
import articles

if __name__ == "__main__":
    uvicorn.run("main:app", port = 8000, host = "localhost", reload = True, ssl_keyfile="./cert/key.pem", ssl_certfile="./cert/cert.pem")

