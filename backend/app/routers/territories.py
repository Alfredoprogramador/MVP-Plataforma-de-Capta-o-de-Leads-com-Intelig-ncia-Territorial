from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas import TerritoryCreate, TerritoryUpdate, TerritoryOut, LeadOut
from ..services import territory_service
from ..models import Lead

router = APIRouter(prefix="/api/territories", tags=["territories"])


@router.get("/", response_model=List[TerritoryOut])
def list_territories(db: Session = Depends(get_db)):
    territories = territory_service.get_territories(db)
    result = []
    for t in territories:
        count = db.query(Lead).filter(Lead.territory_id == t.id).count()
        out = TerritoryOut.model_validate(t)
        out.lead_count = count
        result.append(out)
    return result


@router.post("/", response_model=TerritoryOut, status_code=201)
def create_territory(data: TerritoryCreate, db: Session = Depends(get_db)):
    return territory_service.create_territory(db, data)


@router.get("/{territory_id}", response_model=TerritoryOut)
def get_territory(territory_id: int, db: Session = Depends(get_db)):
    t = territory_service.get_territory(db, territory_id)
    if not t:
        raise HTTPException(status_code=404, detail="Território não encontrado")
    out = TerritoryOut.model_validate(t)
    out.lead_count = db.query(Lead).filter(Lead.territory_id == territory_id).count()
    return out


@router.put("/{territory_id}", response_model=TerritoryOut)
def update_territory(territory_id: int, data: TerritoryUpdate, db: Session = Depends(get_db)):
    t = territory_service.update_territory(db, territory_id, data)
    if not t:
        raise HTTPException(status_code=404, detail="Território não encontrado")
    return t


@router.delete("/{territory_id}", status_code=204)
def delete_territory(territory_id: int, db: Session = Depends(get_db)):
    if not territory_service.delete_territory(db, territory_id):
        raise HTTPException(status_code=404, detail="Território não encontrado")


@router.get("/{territory_id}/leads", response_model=List[LeadOut])
def territory_leads(territory_id: int, db: Session = Depends(get_db)):
    t = territory_service.get_territory(db, territory_id)
    if not t:
        raise HTTPException(status_code=404, detail="Território não encontrado")
    return db.query(Lead).filter(Lead.territory_id == territory_id).all()
