# models.py
from sqlalchemy import Column, Integer, String, BigInteger, DateTime, func
from database import Base


# ── Users table (for login/signup) ───────────────────────────────────────────
class User(Base):
    __tablename__ = "users"

    id       = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email    = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)          # stored as bcrypt hash
    role     = Column(String, default="user")          # "admin" or "user"; set by DB owner
    created_at = Column(DateTime, default=func.now())


# ── Survey entries table ──────────────────────────────────────────────────────
class Entry(Base):
    __tablename__ = "entries"

    id         = Column(Integer, primary_key=True, index=True)
    name       = Column(String,  nullable=False)
    age        = Column(Integer, nullable=False)
    city       = Column(String,  nullable=False)
    profession = Column(String)
    salary     = Column(BigInteger)
    created_at = Column(DateTime, default=func.now())


# NOTE
# The previous design stored admin usernames in a separate ``admins`` table.
# That approach has been deprecated: each ``User`` row now carries a ``role``
# attribute (default "user").  The database owner can promote a user to
# administrator by updating that column.  The old ``admins`` table is no longer
# defined here and should be dropped manually if it exists.
