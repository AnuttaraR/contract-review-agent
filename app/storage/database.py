import json
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime, Enum as SAEnum
from sqlalchemy.orm import declarative_base, sessionmaker
import enum
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./contracts.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class ContractStatus(str, enum.Enum):
    PENDING = "PENDING"
    AUTO_APPROVED = "AUTO_APPROVED"
    NEEDS_REVIEW = "NEEDS_REVIEW"
    HUMAN_APPROVED = "HUMAN_APPROVED"
    HUMAN_REJECTED = "HUMAN_REJECTED"
    REJECTED = "REJECTED"


class Contract(Base):
    __tablename__ = "contracts"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(50), default="upload")
    file_name = Column(String(255))
    file_type = Column(String(20))
    raw_text = Column(Text)
    extracted_data = Column(Text)
    rag_enrichment = Column(Text)
    confidence_score = Column(Float)
    status = Column(SAEnum(ContractStatus), default=ContractStatus.PENDING)
    risk_assessment = Column(String(20))
    reviewer_notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    reviewed_at = Column(DateTime, nullable=True)

    vendor_name = Column(String(255))
    contract_value = Column(Float, nullable=True)
    contract_currency = Column(String(10), nullable=True)
    start_date = Column(String(20), nullable=True)
    end_date = Column(String(20), nullable=True)
    contract_type = Column(String(100), nullable=True)

    def get_extracted(self) -> dict:
        return json.loads(self.extracted_data) if self.extracted_data else {}

    def get_enrichment(self) -> dict:
        return json.loads(self.rag_enrichment) if self.rag_enrichment else {}


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def save_contract(db, contract_data: dict) -> Contract:
    extracted = contract_data.get("extracted", {})
    enrichment = contract_data.get("enrichment", {})

    contract = Contract(
        source=contract_data.get("source", "upload"),
        file_name=contract_data.get("file_name", "unknown"),
        file_type=contract_data.get("file_type", "unknown"),
        raw_text=contract_data.get("raw_text", ""),
        extracted_data=json.dumps(extracted),
        rag_enrichment=json.dumps(enrichment),
        confidence_score=contract_data.get("confidence_score", 0.0),
        status=contract_data.get("status", ContractStatus.PENDING),
        risk_assessment=enrichment.get("risk_assessment", "UNKNOWN"),
        vendor_name=extracted.get("vendor_name"),
        contract_value=extracted.get("contract_value_total"),
        contract_currency=extracted.get("contract_value_currency"),
        start_date=extracted.get("start_date"),
        end_date=extracted.get("end_date"),
        contract_type=extracted.get("contract_type"),
    )
    db.add(contract)
    db.commit()
    db.refresh(contract)
    return contract


def update_contract_status(db, contract_id: int, status: ContractStatus, notes: str = None):
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if contract:
        contract.status = status
        contract.reviewer_notes = notes
        contract.reviewed_at = datetime.utcnow()
        db.commit()
        db.refresh(contract)
    return contract
