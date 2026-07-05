# main.py
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import Column, String, Integer, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel
from database import Base, engine, get_db
import bcrypt
import jwt
from datetime import datetime, timedelta
from typing import List

# Initialize FastAPI app
app = FastAPI()

# Initialize security scheme
security = HTTPBearer()

# Define token settings
SECRET_KEY = "your_secret_key_here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Define database models
class Candidate(Base):
    __tablename__ = "candidates"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String, unique=True)
    phone = Column(String)
    resume = Column(String)

class JobPosting(Base):
    __tablename__ = "job_postings"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    description = Column(String)
    requirements = Column(String)

class InterviewSchedule(Base):
    __tablename__ = "interview_schedules"
    id = Column(Integer, primary_key=True)
    candidate_id = Column(Integer)
    job_posting_id = Column(Integer)
    interview_time = Column(DateTime)

# Define Pydantic models
class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str

class CandidateRequest(BaseModel):
    name: str
    email: str
    phone: str
    resume: str

class JobPostingRequest(BaseModel):
    title: str
    description: str
    requirements: str

class InterviewScheduleRequest(BaseModel):
    candidate_id: int
    job_posting_id: int
    interview_time: datetime

# Define authentication and authorization functions
def get_current_user(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload["sub"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def authenticate_user(db: Session, email: str, password: str):
    user = db.query(Candidate).filter(Candidate.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not bcrypt.checkpw(password.encode("utf-8"), user.password.encode("utf-8")):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return user

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Define API endpoints
@app.post("/api/v1/auth/login")
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, request.email, request.password)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/api/v1/auth/register")
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    hashed_password = bcrypt.hashpw(request.password.encode("utf-8"), bcrypt.gensalt())
    db_user = Candidate(name=request.name, email=request.email, password=hashed_password.decode("utf-8"))
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"message": "User created successfully"}

@app.get("/api/v1/candidates")
async def get_candidates(db: Session = Depends(get_db), token: HTTPAuthorizationCredentials = Depends(security)):
    current_user = get_current_user(token.credentials)
    candidates = db.query(Candidate).all()
    return [{"id": candidate.id, "name": candidate.name, "email": candidate.email} for candidate in candidates]

@app.post("/api/v1/candidates")
async def create_candidate(request: CandidateRequest, db: Session = Depends(get_db), token: HTTPAuthorizationCredentials = Depends(security)):
    current_user = get_current_user(token.credentials)
    db_candidate = Candidate(name=request.name, email=request.email, phone=request.phone, resume=request.resume)
    db.add(db_candidate)
    db.commit()
    db.refresh(db_candidate)
    return {"id": db_candidate.id, "name": db_candidate.name, "email": db_candidate.email}

@app.get("/api/v1/job-postings")
async def get_job_postings(db: Session = Depends(get_db), token: HTTPAuthorizationCredentials = Depends(security)):
    current_user = get_current_user(token.credentials)
    job_postings = db.query(JobPosting).all()
    return [{"id": job_posting.id, "title": job_posting.title, "description": job_posting.description} for job_posting in job_postings]

@app.post("/api/v1/job-postings")
async def create_job_posting(request: JobPostingRequest, db: Session = Depends(get_db), token: HTTPAuthorizationCredentials = Depends(security)):
    current_user = get_current_user(token.credentials)
    db_job_posting = JobPosting(title=request.title, description=request.description, requirements=request.requirements)
    db.add(db_job_posting)
    db.commit()
    db.refresh(db_job_posting)
    return {"id": db_job_posting.id, "title": db_job_posting.title, "description": db_job_posting.description}

@app.get("/api/v1/interview-schedules")
async def get_interview_schedules(db: Session = Depends(get_db), token: HTTPAuthorizationCredentials = Depends(security)):
    current_user = get_current_user(token.credentials)
    interview_schedules = db.query(InterviewSchedule).all()
    return [{"id": interview_schedule.id, "candidate_id": interview_schedule.candidate_id, "job_posting_id": interview_schedule.job_posting_id, "interview_time": interview_schedule.interview_time} for interview_schedule in interview_schedules]

@app.post("/api/v1/interview-schedules")
async def create_interview_schedule(request: InterviewScheduleRequest, db: Session = Depends(get_db), token: HTTPAuthorizationCredentials = Depends(security)):
    current_user = get_current_user(token.credentials)
    db_interview_schedule = InterviewSchedule(candidate_id=request.candidate_id, job_posting_id=request.job_posting_id, interview_time=request.interview_time)
    db.add(db_interview_schedule)
    db.commit()
    db.refresh(db_interview_schedule)
    return {"id": db_interview_schedule.id, "candidate_id": db_interview_schedule.candidate_id, "job_posting_id": db_interview_schedule.job_posting_id, "interview_time": db_interview_schedule.interview_time}