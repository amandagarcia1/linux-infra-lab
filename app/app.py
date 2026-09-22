import os
import socket

import psycopg
from psycopg.rows import dict_row
from fastapi import FastAPI, HTTPException


app = FastAPI(title="Linux Infra Lab")


def get_db_connection():
    return psycopg.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )


@app.get("/")
def root():
    return {
        "app": "linux-infra-lab",
        "hostname": socket.gethostname(),
        "status": "ok",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "hostname": socket.gethostname(),
    }


@app.get("/health/db")
def health_db():
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                cur.fetchone()

        return {
            "status": "healthy",
            "database": "connected",
            "hostname": socket.gethostname(),
        }

    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Database unavailable",
        )


@app.get("/records")
def get_records():
    try:
        with get_db_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute("""
                    SELECT id, origem, mensagem, criado_em
                    FROM lab_test
                    ORDER BY id
                """)

                records = cur.fetchall()

        return records

    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Database unavailable",
        )
    