from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, Field


TransactionType = Literal[
    "CASH_IN",
    "CASH_OUT",
    "DEBIT",
    "PAYMENT",
    "TRANSFER",
]


class TransactionRequest(BaseModel):
    step: int = Field(..., ge=1, description="Simulation time step from the PaySim dataset.")
    type: TransactionType = Field(..., description="Transaction type.")
    amount: float = Field(..., ge=0, description="Transaction amount.")
    oldbalanceOrg: float = Field(..., ge=0, description="Sender balance before transaction.")
    newbalanceOrig: float = Field(..., ge=0, description="Sender balance after transaction.")
    oldbalanceDest: float = Field(..., ge=0, description="Receiver balance before transaction.")
    newbalanceDest: float = Field(..., ge=0, description="Receiver balance after transaction.")


class PredictionResponse(BaseModel):
    fraud_probability: float
    risk_level: Literal["low", "medium", "high"]
    decision: Literal["approve", "manual_review", "block"]
    model_version: str


class BatchPredictionRequest(BaseModel):
    transactions: List[TransactionRequest] = Field(..., min_length=1)


class BatchPredictionResponse(BaseModel):
    count: int
    predictions: List[PredictionResponse]


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool


class ModelInfoResponse(BaseModel):
    model_name: str
    model_version: str
    metrics_available: bool
    test_pr_auc: Optional[float] = None
    test_roc_auc: Optional[float] = None
    test_precision: Optional[float] = None
    test_recall: Optional[float] = None
    test_f1: Optional[float] = None
