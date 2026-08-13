import os
from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI, File, UploadFile, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.intake.parser import parse_document
from app.agent.extractor import process_document
from app.agent.router import route_contract
from app.storage.database import get_db, save_contract, init_db, ContractStatus

app = FastAPI(title="Contract Review Webhook", version="1.0.0")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    init_db()


def verify_secret(x_webhook_secret: str = Header(default="")):
    if WEBHOOK_SECRET and x_webhook_secret != WEBHOOK_SECRET:
        raise HTTPException(status_code=401, detail="Invalid webhook secret")


@app.post("/webhook/contract", dependencies=[Depends(verify_secret)])
async def receive_contract(
    file: UploadFile = File(...),
    source: str = "webhook",
    db: Session = Depends(get_db),
):
    file_bytes = await file.read()
    filename = file.filename or "attachment"
    content_type = file.content_type or ""

    try:
        parsed = parse_document(file_bytes, filename, content_type)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    try:
        result = process_document(parsed)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI extraction failed: {e}")

    status, reason = route_contract(result["confidence_score"], result["enrichment"])

    contract = save_contract(
        db,
        {
            **result,
            "source": source,
            "file_name": filename,
            "status": status,
        },
    )

    return {
        "contract_id": contract.id,
        "vendor_name": contract.vendor_name,
        "confidence_score": contract.confidence_score,
        "status": status.value,
        "routing_reason": reason,
        "risk_assessment": result["enrichment"].get("risk_assessment"),
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/contracts")
def list_contracts(limit: int = 20, db: Session = Depends(get_db)):
    from app.storage.database import Contract
    contracts = db.query(Contract).order_by(Contract.created_at.desc()).limit(limit).all()
    return [
        {
            "id": c.id,
            "vendor_name": c.vendor_name,
            "status": c.status.value if c.status else None,
            "confidence_score": c.confidence_score,
            "created_at": c.created_at.isoformat() if c.created_at else None,
        }
        for c in contracts
    ]
