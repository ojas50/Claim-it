from typing import Literal

from pydantic import BaseModel, Field


class Clause(BaseModel):
    id: str = ""
    title: str = ""
    text: str = ""


class LineItem(BaseModel):
    id: str = ""
    description: str = ""
    amount: float = 0


class PolicyFields(BaseModel):
    policy_number: str = ""
    insurer: str = ""
    insured_name: str = ""
    sum_insured: float = 0
    policy_start_date: str = ""
    policy_end_date: str = ""
    clauses: list[Clause] = Field(default_factory=list)
    confidence: float = 0
    source_file: str = ""
    warnings: list[str] = Field(default_factory=list)


class BillFields(BaseModel):
    patient_name: str = ""
    hospital_name: str = ""
    admission_date: str = ""
    discharge_date: str = ""
    bill_number: str = ""
    line_items: list[LineItem] = Field(default_factory=list)
    total_amount: float = 0
    confidence: float = 0
    source_file: str = ""
    warnings: list[str] = Field(default_factory=list)


class ParseResponse(BaseModel):
    policy: PolicyFields
    bill: BillFields
    mode: Literal["mock", "live"]
    warnings: list[str] = Field(default_factory=list)


class TranscribeResponse(BaseModel):
    transcript: str
    language_code: str
    mode: Literal["mock", "live"]
    warning: str = ""


class AnalyzeRequest(BaseModel):
    narration: str
    language: str = "hi-IN"
    policy: PolicyFields
    bill: BillFields


class Facts(BaseModel):
    patient_name: str = ""
    hospital_name: str = ""
    incident_date: str = ""
    claim_type: str = ""
    summary: str = ""


class Verdict(BaseModel):
    line_id: str
    line_description: str
    amount: float
    verdict: Literal["covered", "partially_covered", "not_covered", "unclear"]
    covered_amount: float = 0
    confidence: float = 0
    clause_id: str = ""
    clause_text: str = ""
    reasoning: str = ""


class Gap(BaseModel):
    id: str = ""
    title: str
    detail: str
    severity: Literal["high", "medium", "low"] = "medium"
    action: str = ""


class Totals(BaseModel):
    billed: float = 0
    admissible: float = 0
    copay_percent: float = 0
    copay_amount: float = 0
    covered: float = 0
    patient_pay: float = 0


class AnalysisResponse(BaseModel):
    facts: Facts
    verdicts: list[Verdict]
    gaps: list[Gap]
    totals: Totals
    summary: str
    mode: Literal["mock", "live"]
    disclaimer: str


class ClaimForm(BaseModel):
    policy_number: str = ""
    insurer: str = ""
    patient_name: str = ""
    hospital_name: str = ""
    admission_date: str = ""
    discharge_date: str = ""
    claim_amount: float = 0
    phone: str = ""
    address: str = ""


class DraftRequest(BaseModel):
    language: str = "hi-IN"
    form: ClaimForm


class DraftResponse(BaseModel):
    letter: str
    language: str
    mode: Literal["mock", "live"]


class SpeakRequest(BaseModel):
    text: str
    language: str = "hi-IN"
