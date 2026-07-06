import os
from datetime import date
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor

app = FastAPI(title="Job Tracker API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "jobtracker")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")


def get_conn():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        cursor_factory=RealDictCursor,
    )


def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS applications (
            id SERIAL PRIMARY KEY,
            company VARCHAR(255) NOT NULL,
            role VARCHAR(255) NOT NULL,
            status VARCHAR(50) NOT NULL DEFAULT 'applied',
            applied_date DATE NOT NULL DEFAULT CURRENT_DATE
        );
        """
    )
    conn.commit()
    cur.close()
    conn.close()


@app.on_event("startup")
def on_startup():
    init_db()


class ApplicationIn(BaseModel):
    company: str
    role: str
    status: str = "applied"
    applied_date: Optional[date] = None


class ApplicationOut(ApplicationIn):
    id: int


@app.get("/health")
def health():
    try:
        conn = get_conn()
        conn.close()
        return {"status": "ok", "db": "connected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"db unreachable: {e}")


@app.get("/applications", response_model=list[ApplicationOut])
def list_applications():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM applications ORDER BY id DESC;")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


@app.post("/applications", response_model=ApplicationOut)
def create_application(app_in: ApplicationIn):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO applications (company, role, status, applied_date)
        VALUES (%s, %s, %s, COALESCE(%s, CURRENT_DATE))
        RETURNING *;
        """,
        (app_in.company, app_in.role, app_in.status, app_in.applied_date),
    )
    row = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return row


@app.put("/applications/{app_id}", response_model=ApplicationOut)
def update_application(app_id: int, app_in: ApplicationIn):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE applications
        SET company=%s, role=%s, status=%s, applied_date=COALESCE(%s, applied_date)
        WHERE id=%s
        RETURNING *;
        """,
        (app_in.company, app_in.role, app_in.status, app_in.applied_date, app_id),
    )
    row = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="not found")
    return row


@app.delete("/applications/{app_id}")
def delete_application(app_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM applications WHERE id=%s RETURNING id;", (app_id,))
    row = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="not found")
    return {"deleted": app_id}
