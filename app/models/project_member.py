from sqlalchemy import Table, Column, ForeignKey
from app.database import Base

project_members = Table(
    "project_members",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("project_id", ForeignKey("projects.id"), primary_key=True)
)
