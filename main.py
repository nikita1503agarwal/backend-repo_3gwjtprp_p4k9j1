import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import BlogPost, Tournament, ClassVideo, Trainer, Booking

app = FastAPI(title="Tennis Connect API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Tennis Connect Backend Running"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = getattr(db, 'name', None) or "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response


# Helper to convert ObjectId strings

def to_object_id(id_str: str) -> ObjectId:
    try:
        return ObjectId(id_str)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID format")


# Blog Endpoints

@app.post("/api/blogs", response_model=dict)
def create_blog(post: BlogPost):
    inserted_id = create_document("blogpost", post)
    return {"id": inserted_id}


@app.get("/api/blogs", response_model=List[dict])
def list_blogs(tag: Optional[str] = None, limit: int = 50):
    filter_dict = {"published": True}
    if tag:
        filter_dict["tags"] = tag
    docs = get_documents("blogpost", filter_dict, limit)
    # Convert ObjectId to string
    for d in docs:
        d["_id"] = str(d.get("_id"))
    return docs


# Tournaments

@app.post("/api/tournaments", response_model=dict)
def create_tournament(t: Tournament):
    inserted_id = create_document("tournament", t)
    return {"id": inserted_id}


@app.get("/api/tournaments", response_model=List[dict])
def list_tournaments(country: Optional[str] = None, upcoming_only: bool = False, limit: int = 100):
    from datetime import date
    filter_dict = {}
    if country:
        filter_dict["country"] = country
    if upcoming_only:
        filter_dict["start_date"] = {"$gte": date.today()}
    docs = get_documents("tournament", filter_dict, limit)
    for d in docs:
        d["_id"] = str(d.get("_id"))
    return docs


# Instruction Videos

@app.post("/api/classes", response_model=dict)
def create_class_video(v: ClassVideo):
    inserted_id = create_document("classvideo", v)
    return {"id": inserted_id}


@app.get("/api/classes", response_model=List[dict])
def list_class_videos(premium: Optional[bool] = None, limit: int = 100):
    filter_dict = {}
    if premium is not None:
        filter_dict["is_premium"] = premium
    docs = get_documents("classvideo", filter_dict, limit)
    for d in docs:
        d["_id"] = str(d.get("_id"))
    return docs


# Trainers and Bookings

@app.post("/api/trainers", response_model=dict)
def create_trainer(t: Trainer):
    inserted_id = create_document("trainer", t)
    return {"id": inserted_id}


@app.get("/api/trainers", response_model=List[dict])
def list_trainers(country: Optional[str] = None, city: Optional[str] = None, limit: int = 100):
    filter_dict = {}
    if country:
        filter_dict["country"] = country
    if city:
        filter_dict["city"] = city
    docs = get_documents("trainer", filter_dict, limit)
    for d in docs:
        d["_id"] = str(d.get("_id"))
    return docs


class BookingIn(Booking):
    pass


@app.post("/api/bookings", response_model=dict)
def create_booking(b: BookingIn):
    # validate trainer exists
    trainer = db["trainer"].find_one({"_id": to_object_id(b.trainer_id)})
    if not trainer:
        raise HTTPException(status_code=404, detail="Trainer not found")
    if b.tournament_id:
        tournament = db["tournament"].find_one({"_id": to_object_id(b.tournament_id)})
        if not tournament:
            raise HTTPException(status_code=404, detail="Tournament not found")
    inserted_id = create_document("booking", b)
    return {"id": inserted_id}


@app.get("/api/bookings", response_model=List[dict])
def list_bookings(trainer_id: Optional[str] = None, user_email: Optional[str] = None, limit: int = 100):
    filter_dict = {}
    if trainer_id:
        filter_dict["trainer_id"] = trainer_id
    if user_email:
        filter_dict["user_email"] = user_email
    docs = get_documents("booking", filter_dict, limit)
    for d in docs:
        d["_id"] = str(d.get("_id"))
    return docs


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
