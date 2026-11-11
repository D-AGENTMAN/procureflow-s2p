from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models import SourcingProject
from .schemas import SourcingProjectCreate, SourcingProjectRead, SourcingProjectUpdate

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ProcureFlow API",
    description="Strategic Sourcing API – Milestone 1",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://procureflow-s2p.vercel.app"],
    allow_origin_regex=r"^http://localhost:[0-9]+$",
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
    existing_codes = db.query(SourcingProject.project_code).all()

    existing_numbers = []

    for (code,) in existing_codes:
        if code and code.startswith("SRC-"):
            number = code.replace("SRC-", "", 1)
            if number.isdigit():
                existing_numbers.append(int(number))

    next_number = max(existing_numbers, default=0) + 1
    project_code = f"SRC-{next_number:04d}"

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



@app.put(
    "/api/sourcing-projects/{project_id}",
    response_model=SourcingProjectRead,
)
def update_project(
    project_id: int,
    payload: SourcingProjectUpdate,
    db: Session = Depends(get_db),
):
    project = db.get(SourcingProject, project_id)

    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    project.name = payload.name
    project.category = payload.category
    project.owner = payload.owner
    project.estimated_budget = payload.estimated_budget
    project.currency = payload.currency.upper()
    project.description = payload.description
    project.status = payload.status

    db.commit()
    db.refresh(project)

    return project


@app.delete("/api/sourcing-projects/{project_id}")
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
):
    project = db.get(SourcingProject, project_id)

    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    db.delete(project)
    db.commit()

    return {"message": "Project deleted successfully"}

