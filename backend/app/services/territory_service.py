from typing import Optional, List
from sqlalchemy.orm import Session

from ..models import Territory
from ..schemas import TerritoryCreate, TerritoryUpdate


def get_territory(db: Session, territory_id: int) -> Optional[Territory]:
    return db.query(Territory).filter(Territory.id == territory_id).first()


def get_territories(db: Session, skip: int = 0, limit: int = 100) -> List[Territory]:
    return db.query(Territory).offset(skip).limit(limit).all()


def create_territory(db: Session, data: TerritoryCreate) -> Territory:
    territory = Territory(**data.model_dump())
    db.add(territory)
    db.commit()
    db.refresh(territory)
    return territory


def update_territory(db: Session, territory_id: int, data: TerritoryUpdate) -> Optional[Territory]:
    territory = get_territory(db, territory_id)
    if not territory:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(territory, field, value)
    db.commit()
    db.refresh(territory)
    return territory


def delete_territory(db: Session, territory_id: int) -> bool:
    territory = get_territory(db, territory_id)
    if not territory:
        return False
    db.delete(territory)
    db.commit()
    return True
