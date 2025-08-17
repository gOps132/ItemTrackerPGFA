from sqlalchemy import Boolean, Column, Integer, String
# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Item(Base):
    """
    SQLAlchemy model for the 'items' table.
    represents the database schema.
    """
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, index=True) 
    is_done = Column(Boolean, default=False)

    def __repr__(self):
        return f"<Item(id={self.id}, text='{self.text}', is_done={self.is_done})>"
