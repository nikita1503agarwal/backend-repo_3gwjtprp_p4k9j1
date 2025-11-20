"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogpost" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime

# Core domain schemas for the Tennis Connect app

class BlogPost(BaseModel):
    title: str = Field(..., description="Post title")
    content: str = Field(..., description="Markdown or rich text content")
    author_name: str = Field(..., description="Author display name")
    tags: List[str] = Field(default_factory=list, description="List of tags")
    published: bool = Field(default=True, description="Whether post is published")


class Tournament(BaseModel):
    name: str = Field(..., description="Tournament name")
    country: str = Field(..., description="Country where the tournament takes place")
    city: Optional[str] = Field(None, description="City where the tournament takes place")
    start_date: date = Field(..., description="Start date (YYYY-MM-DD)")
    end_date: date = Field(..., description="End date (YYYY-MM-DD)")
    surface: Optional[str] = Field(None, description="Surface type: clay, grass, hard")
    level: Optional[str] = Field(None, description="Level: Grand Slam, ATP, WTA, Challenger, ITF")


class ClassVideo(BaseModel):
    title: str = Field(..., description="Class title")
    description: Optional[str] = Field(None, description="Class description")
    level: Optional[str] = Field(None, description="Beginner, Intermediate, Advanced")
    video_url: Optional[str] = Field(None, description="Streaming or embed URL")
    is_premium: bool = Field(default=False, description="If true, requires payment")
    price: Optional[float] = Field(None, ge=0, description="Price in USD if premium")


class Trainer(BaseModel):
    name: str = Field(..., description="Trainer full name")
    country: str = Field(..., description="Country of operation")
    city: Optional[str] = Field(None, description="City of operation")
    languages: List[str] = Field(default_factory=list, description="Languages spoken")
    hourly_rate: float = Field(..., ge=0, description="Hourly rate in USD")
    bio: Optional[str] = Field(None, description="Short biography")
    rating: Optional[float] = Field(None, ge=0, le=5, description="Average rating 0-5")


class Booking(BaseModel):
    trainer_id: str = Field(..., description="ID of the trainer")
    user_name: str = Field(..., description="Name of the person booking")
    user_email: str = Field(..., description="Contact email")
    tournament_id: Optional[str] = Field(None, description="ID of the tournament if booking around an event")
    session_date: datetime = Field(..., description="Session date/time in ISO format")
    duration_hours: float = Field(..., gt=0, description="Duration in hours")
    notes: Optional[str] = Field(None, description="Optional notes for the trainer")
    status: str = Field(default="pending", description="pending, confirmed, canceled")


# Optional: keep previous example schemas for reference of the viewer tooling
class User(BaseModel):
    name: str
    email: str
    address: str
    age: Optional[int] = None
    is_active: bool = True

class Product(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    category: str
    in_stock: bool = True
