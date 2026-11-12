from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models import SourcingProject, Supplier, Quotation, Award
from .schemas import (
    SourcingProjectCreate,
    SourcingProjectRead,
    SourcingProjectUpdate,
    SupplierCreate,
    SupplierRead,
    QuotationCreate,
    QuotationRead,
    AwardCreate,
    AwardRead,
    BidComparisonRead,
)

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



@app.get("/api/suppliers", response_model=list[SupplierRead])
def list_suppliers(db: Session = Depends(get_db)):
    statement = select(Supplier).order_by(Supplier.id.desc())
    return db.scalars(statement).all()


@app.post("/api/suppliers", response_model=SupplierRead, status_code=201)
def create_supplier(payload: SupplierCreate, db: Session = Depends(get_db)):
    existing = db.query(Supplier).filter(
        Supplier.supplier_code == payload.supplier_code
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Supplier code already exists",
        )

    supplier = Supplier(**payload.model_dump())
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    return supplier


@app.put("/api/suppliers/{supplier_id}", response_model=SupplierRead)
def update_supplier(
    supplier_id: int,
    payload: SupplierCreate,
    db: Session = Depends(get_db),
):
    supplier = db.get(Supplier, supplier_id)

    if supplier is None:
        raise HTTPException(status_code=404, detail="Supplier not found")

    if payload.supplier_code != supplier.supplier_code:
        existing = db.query(Supplier).filter(
            Supplier.supplier_code == payload.supplier_code
        ).first()

        if existing:
            raise HTTPException(
                status_code=400,
                detail="Supplier code already exists",
            )

    for field, value in payload.model_dump().items():
        setattr(supplier, field, value)

    db.commit()
    db.refresh(supplier)
    return supplier


@app.delete("/api/suppliers/{supplier_id}")
def delete_supplier(supplier_id: int, db: Session = Depends(get_db)):
    supplier = db.get(Supplier, supplier_id)

    if supplier is None:
        raise HTTPException(status_code=404, detail="Supplier not found")

    quotation = db.query(Quotation).filter(
        Quotation.supplier_id == supplier_id
    ).first()

    if quotation:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete supplier because quotations are linked to it",
        )

    db.delete(supplier)
    db.commit()
    return {"message": "Supplier deleted successfully"}



@app.get("/api/quotations", response_model=list[QuotationRead])
def list_quotations(
    project_id: int | None = None,
    db: Session = Depends(get_db),
):
    statement = select(Quotation).order_by(Quotation.id.desc())

    if project_id is not None:
        statement = statement.where(Quotation.project_id == project_id)

    return db.scalars(statement).all()


@app.post("/api/quotations", response_model=QuotationRead, status_code=201)
def create_quotation(
    payload: QuotationCreate,
    db: Session = Depends(get_db),
):
    project = db.get(SourcingProject, payload.project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Sourcing project not found")

    supplier = db.get(Supplier, payload.supplier_id)
    if supplier is None:
        raise HTTPException(status_code=404, detail="Supplier not found")

    quotation = Quotation(
        **payload.model_dump(exclude={"currency"}),
        currency=payload.currency.upper(),
    )

    db.add(quotation)
    db.commit()
    db.refresh(quotation)
    return quotation


@app.put("/api/quotations/{quotation_id}", response_model=QuotationRead)
def update_quotation(
    quotation_id: int,
    payload: QuotationCreate,
    db: Session = Depends(get_db),
):
    quotation = db.get(Quotation, quotation_id)

    if quotation is None:
        raise HTTPException(status_code=404, detail="Quotation not found")

    if db.get(SourcingProject, payload.project_id) is None:
        raise HTTPException(status_code=404, detail="Sourcing project not found")

    if db.get(Supplier, payload.supplier_id) is None:
        raise HTTPException(status_code=404, detail="Supplier not found")

    for field, value in payload.model_dump().items():
        setattr(quotation, field, value.upper() if field == "currency" else value)

    db.commit()
    db.refresh(quotation)
    return quotation


@app.delete("/api/quotations/{quotation_id}")
def delete_quotation(
    quotation_id: int,
    db: Session = Depends(get_db),
):
    quotation = db.get(Quotation, quotation_id)

    if quotation is None:
        raise HTTPException(status_code=404, detail="Quotation not found")

    award = db.query(Award).filter(
        Award.quotation_id == quotation_id
    ).first()

    if award:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete a quotation that has an award",
        )

    db.delete(quotation)
    db.commit()
    return {"message": "Quotation deleted successfully"}


@app.get(
    "/api/sourcing-projects/{project_id}/bid-comparison",
    response_model=list[BidComparisonRead],
)
def compare_bids(project_id: int, db: Session = Depends(get_db)):
    project = db.get(SourcingProject, project_id)

    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    statement = (
        select(Quotation, Supplier)
        .join(Supplier, Quotation.supplier_id == Supplier.id)
        .where(Quotation.project_id == project_id)
    )

    results = db.execute(statement).all()

    bids = []
    for quotation, supplier in results:
        bids.append({
            "quotation_id": quotation.id,
            "supplier_id": supplier.id,
            "supplier_name": supplier.name,
            "unit_price": quotation.unit_price,
            "currency": quotation.currency,
            "moq": quotation.moq,
            "lead_time_days": quotation.lead_time_days,
            "payment_terms": quotation.payment_terms,
            "validity_days": quotation.validity_days,
        })

    bids.sort(key=lambda bid: (bid["unit_price"], bid["moq"], bid["lead_time_days"]))

    for index, bid in enumerate(bids):
        bid["price_rank"] = 1 + sum(
            other["unit_price"] < bid["unit_price"] for other in bids
        )
        bid["moq_rank"] = 1 + sum(
            other["moq"] < bid["moq"] for other in bids
        )
        bid["lead_time_rank"] = 1 + sum(
            other["lead_time_days"] < bid["lead_time_days"] for other in bids
        )
        bid["overall_rank"] = index + 1

    return bids


@app.get("/api/awards/{project_id}", response_model=AwardRead)
def get_project_award(project_id: int, db: Session = Depends(get_db)):
    award = db.query(Award).filter(
        Award.project_id == project_id
    ).first()

    if award is None:
        raise HTTPException(status_code=404, detail="Award not found")

    return award


@app.post("/api/awards", response_model=AwardRead, status_code=201)
def create_award(payload: AwardCreate, db: Session = Depends(get_db)):
    project = db.get(SourcingProject, payload.project_id)

    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    quotation = db.get(Quotation, payload.quotation_id)

    if quotation is None or quotation.project_id != payload.project_id:
        raise HTTPException(
            status_code=400,
            detail="Quotation does not belong to this sourcing project",
        )

    existing_award = db.query(Award).filter(
        Award.project_id == payload.project_id
    ).first()

    if existing_award:
        raise HTTPException(
            status_code=400,
            detail="An award already exists for this project",
        )

    awarded_quotation = db.query(Award).filter(
        Award.quotation_id == payload.quotation_id
    ).first()

    if awarded_quotation:
        raise HTTPException(
            status_code=400,
            detail="This quotation has already been awarded",
        )

    award = Award(
        project_id=payload.project_id,
        quotation_id=payload.quotation_id,
        awarded_price=payload.awarded_price,
        currency=payload.currency.upper(),
        justification=payload.justification,
    )

    db.add(award)
    db.commit()
    db.refresh(award)

    return award
