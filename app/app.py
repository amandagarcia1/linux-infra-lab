import socket

from fastapi import FastAPI

app = FastAPI(title="Linux Infra Lab")


@app.get("/")
def root():
    return {
        "app": "linux-infra-lab",
        "hostname": socket.gethostname(),
        "status": "ok"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }