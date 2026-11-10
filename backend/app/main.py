from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models import SourcingProject
from .schemas import SourcingProjectCreate, SourcingProjectRead

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ProcureFlow API",
    description="Strategic Sourcing API – Milestone 1",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000",
                   "http://localhost:3001",
                   "https://procureflow-s2p.vercel.app",
],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "ok", "application": "ProcureFlow API"}


@app.get("/api/sourcing-projects", response_model=list[SourcingProjectRead])
def list_projects(db: Session = Depends(get_db)):
    statement = select(SourcingProject).order_by(SourcingProject.id.desc())
    return db.scalars(statement).all()


@app.post(
    "/api/sourcing-projects",
    response_model=SourcingProjectRead,
    status_code=201,
)
def create_project(
    payload: SourcingProjectCreate,
    db: Session = Depends(get_db),
):
    project_code = f"SRC-{db.query(SourcingProject).count() + 1:04d}"

    existing = db.scalar(
        select(SourcingProject).where(
            SourcingProject.project_code == project_code
        )
    )
    if existing:
        raise HTTPException(status_code=409, detail="Project code already exists")

    project = SourcingProject(
        project_code=project_code,
        name=payload.name,
        category=payload.category,
        owner=payload.owner,
        estimated_budget=payload.estimated_budget,
        currency=payload.currency.upper(),
        description=payload.description,
        status="Draft",
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project
