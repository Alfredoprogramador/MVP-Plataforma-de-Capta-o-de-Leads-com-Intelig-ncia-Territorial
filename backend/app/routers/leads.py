import csv
import io
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas import LeadCreate, LeadUpdate, LeadOut, QualifyResult, BulkAction, BulkResult, NoteCreate, NoteOut
from ..services import lead_service
from ..services import ai_service
from ..models import LeadStatus, Lead, LeadNote

router = APIRouter(prefix="/api/leads", tags=["leads"])


@router.get("/stats/summary")
def lead_stats(db: Session = Depends(get_db)):
    from datetime import datetime, date
    total = db.query(Lead).count()
    today = db.query(Lead).filter(
        Lead.created_at >= datetime.combine(date.today(), datetime.min.time())
    ).count()
    qualified = db.query(Lead).filter(Lead.status == LeadStatus.qualified).count()
    converted = db.query(Lead).filter(Lead.status == LeadStatus.converted).count()
    return {"total": total, "new_today": today, "qualified": qualified, "converted": converted}


@router.get("/export/csv")
def export_leads_csv(
    status: Optional[str] = None,
    territory_id: Optional[int] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Download all leads as a CSV file."""
    leads = lead_service.get_leads(db, skip=0, limit=10000, status=status,
                                    territory_id=territory_id, search=search)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "ID", "Nome", "E-mail", "Telefone", "Endereço", "Cidade", "Estado",
        "CEP", "Status", "Origem", "Score IA", "Território", "Latitude", "Longitude",
        "Observações", "Criado em",
    ])
    for l in leads:
        writer.writerow([
            l.id, l.name, l.email or "", l.phone or "", l.address or "",
            l.city or "", l.state or "", l.zip_code or "",
            l.status.value if l.status else "",
            l.source.value if l.source else "",
            l.ai_score if l.ai_score is not None else "",
            l.territory.name if l.territory else "",
            l.latitude or "", l.longitude or "",
            l.notes or "",
            l.created_at.strftime("%Y-%m-%d %H:%M") if l.created_at else "",
        ])
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=leads.csv"},
    )


@router.post("/import/csv", status_code=201)
async def import_leads_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Import leads from a CSV file. Expected columns: nome, email, telefone, cidade, estado, endereco, observacoes."""
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Apenas arquivos .csv são aceitos")
    contents = await file.read()
    try:
        text = contents.decode("utf-8-sig")  # handle BOM
    except UnicodeDecodeError:
        text = contents.decode("latin-1")
    reader = csv.DictReader(io.StringIO(text))
    created = 0
    errors = []
    for i, row in enumerate(reader, start=2):
        # Normalize header keys: strip, lower, remove accents
        row = {k.strip().lower(): v.strip() for k, v in row.items() if k}
        name = row.get("nome") or row.get("name") or row.get("nome completo") or ""
        if not name:
            errors.append(f"Linha {i}: campo 'nome' obrigatório")
            continue
        try:
            lead_data = LeadCreate(
                name=name,
                email=row.get("email") or row.get("e-mail") or None,
                phone=row.get("telefone") or row.get("phone") or row.get("whatsapp") or None,
                address=row.get("endereco") or row.get("endereço") or row.get("address") or None,
                city=row.get("cidade") or row.get("city") or None,
                state=row.get("estado") or row.get("state") or None,
                zip_code=row.get("cep") or row.get("zip") or None,
                notes=row.get("observacoes") or row.get("observações") or row.get("notes") or None,
                source="manual",
            )
            lead_service.create_lead(db, lead_data)
            created += 1
        except Exception as e:
            errors.append(f"Linha {i}: {str(e)}")
    return {"created": created, "errors": errors}


@router.post("/bulk", response_model=BulkResult)
def bulk_action(payload: BulkAction, db: Session = Depends(get_db)):
    """Perform bulk actions: delete, qualify (AI), set_status."""
    processed = 0
    failed = 0
    errors = []
    for lead_id in payload.ids:
        try:
            lead = lead_service.get_lead(db, lead_id)
            if not lead:
                failed += 1
                errors.append(f"Lead {lead_id} não encontrado")
                continue
            if payload.action == "delete":
                lead_service.delete_lead(db, lead_id)
            elif payload.action == "set_status":
                if not payload.status:
                    raise ValueError("Status obrigatório para set_status")
                lead_service.update_lead(db, lead_id, LeadUpdate(status=payload.status))
            elif payload.action == "qualify":
                lead_data = {
                    "name": lead.name, "email": lead.email, "phone": lead.phone,
                    "city": lead.city, "state": lead.state,
                    "source": lead.source.value if lead.source else None,
                }
                result = ai_service.qualify_lead(lead_data)
                lead_service.update_lead(db, lead_id, LeadUpdate(
                    ai_score=result["score"],
                    ai_notes=result["notes"],
                    status=LeadStatus.qualified if result["score"] >= 60 else None,
                ))
            else:
                raise ValueError(f"Ação desconhecida: {payload.action}")
            processed += 1
        except Exception as e:
            failed += 1
            errors.append(f"Lead {lead_id}: {str(e)}")
    return BulkResult(processed=processed, failed=failed, errors=errors)


@router.get("/", response_model=List[LeadOut])
def list_leads(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status: Optional[str] = None,
    territory_id: Optional[int] = None,
    source: Optional[str] = None,
    search: Optional[str] = Query(None, description="Busca por nome, email, telefone ou cidade"),
    db: Session = Depends(get_db),
):
    leads = lead_service.get_leads(db, skip=skip, limit=limit, status=status,
                                    territory_id=territory_id, source=source, search=search)
    return leads


@router.post("/", response_model=LeadOut, status_code=201)
def create_lead(data: LeadCreate, db: Session = Depends(get_db)):
    return lead_service.create_lead(db, data)


@router.get("/{lead_id}", response_model=LeadOut)
def get_lead(lead_id: int, db: Session = Depends(get_db)):
    lead = lead_service.get_lead(db, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead não encontrado")
    return lead


@router.put("/{lead_id}", response_model=LeadOut)
def update_lead(lead_id: int, data: LeadUpdate, db: Session = Depends(get_db)):
    lead = lead_service.update_lead(db, lead_id, data)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead não encontrado")
    return lead


@router.delete("/{lead_id}", status_code=204)
def delete_lead(lead_id: int, db: Session = Depends(get_db)):
    if not lead_service.delete_lead(db, lead_id):
        raise HTTPException(status_code=404, detail="Lead não encontrado")


@router.post("/{lead_id}/qualify", response_model=QualifyResult)
def qualify_lead(lead_id: int, db: Session = Depends(get_db)):
    lead = lead_service.get_lead(db, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead não encontrado")

    lead_data = {
        "name": lead.name, "email": lead.email, "phone": lead.phone,
        "city": lead.city, "state": lead.state,
        "source": lead.source.value if lead.source else None,
        "notes": lead.notes,
    }
    result = ai_service.qualify_lead(lead_data)

    lead_service.update_lead(db, lead_id, LeadUpdate(
        ai_score=result["score"],
        ai_notes=result["notes"],
        status=LeadStatus.qualified if result["score"] >= 60 else None,
    ))
    return QualifyResult(lead_id=lead_id, score=result["score"], notes=result["notes"])


@router.get("/{lead_id}/notes", response_model=List[NoteOut])
def get_notes(lead_id: int, db: Session = Depends(get_db)):
    lead = lead_service.get_lead(db, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead não encontrado")
    return db.query(LeadNote).filter(LeadNote.lead_id == lead_id).order_by(LeadNote.created_at.asc()).all()


@router.post("/{lead_id}/notes", response_model=NoteOut, status_code=201)
def add_note(lead_id: int, payload: NoteCreate, db: Session = Depends(get_db)):
    lead = lead_service.get_lead(db, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead não encontrado")
    note = LeadNote(lead_id=lead_id, content=payload.content, author=payload.author or "admin")
    db.add(note)
    db.commit()
    db.refresh(note)
    return note

