# main.py
# Run: uvicorn main:app --reload
# Docs: http://localhost:8000/docs

from fastapi import FastAPI, Depends, HTTPException, Query, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from database import get_db, create_tables
from models import User, Entry
from auth import (
    hash_password, verify_password,
    create_access_token, verify_token, require_admin
)

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(title="SurveyPulse API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables on startup
create_tables()

# Serve frontend assets (HTML, CSS, JS) from the frontend directory.
# Static files (style.css, shared.js, etc.) are exposed under /static.
app.mount("/static", StaticFiles(directory="frontend"), name="static")


# ── Pydantic schemas ──────────────────────────────────────────────────────────
class SignupSchema(BaseModel):
    username: str
    email:    str
    password: str

class EntrySchema(BaseModel):
    name:       str
    age:        int
    city:       str
    profession: Optional[str] = None
    salary:     Optional[int] = None

class EntryUpdateSchema(BaseModel):
    name:       Optional[str] = None
    age:        Optional[int] = None
    city:       Optional[str] = None
    profession: Optional[str] = None
    salary:     Optional[int] = None


# ══════════════════════════════════════════════════════
#   AUTH ROUTES
# ══════════════════════════════════════════════════════

# ------------------ SIGNUP ------------------
@app.post("/signup", tags=["Auth"])
def signup(data: SignupSchema, db: Session = Depends(get_db)):
    # Check if username or email already exists
    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        username = data.username,
        email    = data.email,
        password = hash_password(data.password),
        role     = "user",  # default; DB owner can manually change to "admin"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "Account created successfully", "username": new_user.username}


# ------------------ LOGIN ------------------
@app.post("/login", tags=["Auth"])
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    admin: bool = Form(False),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == form_data.username).first()

    if not user:
        raise HTTPException(status_code=400, detail="Invalid username")
    if not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=400, detail="Invalid password")

    # block admin accounts on the normal page and vice versa
    if user.role == "admin" and not admin:
        raise HTTPException(status_code=400, detail="Admin accounts must sign in via the admin login page")
    if user.role != "admin" and admin:
        raise HTTPException(status_code=400, detail="Not an admin account")

    token = create_access_token({"sub": user.username, "role": user.role})
    return {"access_token": token, "token_type": "bearer", "role": user.role}


# ══════════════════════════════════════════════════════
#   ENTRY ROUTES
# ══════════════════════════════════════════════════════

# ------------------ CREATE (admin only) ------------------
@app.post("/entries", tags=["Entries"])
def create_entry(
    entry: EntrySchema,
    db:   Session = Depends(get_db),
    user: dict    = Depends(require_admin)
):
    new_entry = Entry(
        name       = entry.name,
        age        = entry.age,
        city       = entry.city,
        profession = entry.profession,
        salary     = entry.salary,
    )
    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)
    return new_entry


# ------------------ READ ALL (any logged-in user) ------------------
@app.get("/entries", tags=["Entries"])
def get_entries(
    search:     Optional[str] = Query(None),
    city:       Optional[str] = Query(None),
    profession: Optional[str] = Query(None),
    skip:       int           = Query(0,  ge=0),
    limit:      int           = Query(10, ge=1, le=100),
    db:   Session = Depends(get_db),
    user: dict    = Depends(verify_token)
):
    query = db.query(Entry)

    if search:
        like = f"%{search}%"
        query = query.filter(
            Entry.name.ilike(like)       |
            Entry.city.ilike(like)       |
            Entry.profession.ilike(like)
        )
    if city:
        query = query.filter(Entry.city == city)
    if profession:
        query = query.filter(Entry.profession == profession)

    total   = query.count()
    entries = query.order_by(Entry.created_at.desc()).offset(skip).limit(limit).all()

    return {"total": total, "skip": skip, "limit": limit, "entries": entries}


# ------------------ READ ONE (any logged-in user) ------------------
@app.get("/entries/{entry_id}", tags=["Entries"])
def get_entry(
    entry_id: int,
    db:   Session = Depends(get_db),
    user: dict    = Depends(verify_token)
):
    entry = db.query(Entry).filter(Entry.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    return entry


# ------------------ UPDATE (admin only) ------------------
@app.put("/entries/{entry_id}", tags=["Entries"])
def update_entry(
    entry_id:     int,
    updated_data: EntryUpdateSchema,
    db:   Session = Depends(get_db),
    user: dict    = Depends(require_admin)
):
    entry = db.query(Entry).filter(Entry.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")

    # Only update fields that were actually sent
    for field, value in updated_data.dict(exclude_unset=True).items():
        if value is not None:
            setattr(entry, field, value)

    db.commit()
    return {"message": "Entry updated successfully"}


# ------------------ DELETE (admin only) ------------------
@app.delete("/entries/{entry_id}", tags=["Entries"])
def delete_entry(
    entry_id: int,
    db:   Session = Depends(get_db),
    user: dict    = Depends(require_admin)
):
    entry = db.query(Entry).filter(Entry.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")

    db.delete(entry)
    db.commit()
    return {"message": "Entry deleted successfully"}


# ------------------ STATS (any logged-in user) ------------------
@app.get("/stats", tags=["Stats"])
def get_stats(db: Session = Depends(get_db), user: dict = Depends(verify_token)):
    from sqlalchemy import func, cast, Date
    from datetime import date

    total  = db.query(Entry).count()
    cities = db.query(Entry.city).distinct().count()
    today  = db.query(Entry).filter(
        cast(Entry.created_at, Date) == date.today()
    ).count()
    avg_age_row = db.query(func.avg(Entry.age)).scalar()
    avg_age = round(avg_age_row) if avg_age_row else 0

    return {"total": total, "cities": cities, "today": today, "avg_age": avg_age}


# ------------------ STATIC/HTML ROUTES (after all API endpoints) ------------------
@app.get("/", include_in_schema=False)
def root():
    return FileResponse("frontend/login.html")

@app.get("/{page_name}", include_in_schema=False)
def serve_page(page_name: str):
    # List of valid HTML pages (all under frontend/)
    valid_pages = ["index.html", "login.html", "admin-login.html", "add.html", "update.html", 
                   "delete.html", "view.html"]
    if page_name in valid_pages:
        return FileResponse(f"frontend/{page_name}")
    elif "." not in page_name:  # Handle URLs without extension
        html_file = f"{page_name}.html"
        if html_file in valid_pages:
            return FileResponse(f"frontend/{html_file}")
    # fallback to login
    return FileResponse("frontend/login.html")