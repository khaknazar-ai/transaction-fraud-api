from __future__ import annotations

from typing import Dict, Tuple

import pandas as pd
from fastapi import FastAPI

from app.model_loader import (
    get_config,
    get_model_version,
    load_metrics,
    load_production_model,
)
from app.prediction_logger import log_prediction
from app.schemas import (
    BatchPredictionRequest,
    BatchPredictionResponse,
    HealthResponse,
    ModelInfoResponse,
    PredictionResponse,
    TransactionRequest,
)


app = FastAPI(
    title="Transaction Fraud API",
    description="API for scoring PaySim transaction records with a trained scikit-learn pipeline.",
    version="0.1.0",
)


@app.get("/")
def root() -> Dict[str, str]:
    return {
        "service": "Transaction Fraud API",
        "status": "running",
        "docs": "/docs",
        "health": "/health",
        "model_info": "/model-info",
        "predict": "/predict",
        "predict_batch": "/predict-batch",
    }


def make_decision(fraud_probability: float) -> Tuple[str, str]:
    config = get_config()

    approve_threshold = config["risk_policy"]["approve_threshold"]
    review_threshold = config["risk_policy"]["review_threshold"]

    if fraud_probability < approve_threshold:
        return "low", "approve"

    if fraud_probability < review_threshold:
        return "medium", "manual_review"

    return "high", "block"


def predict_single_transaction(transaction: TransactionRequest) -> PredictionResponse:
    model = load_production_model()
    transaction_dict = transaction.model_dump()

    input_df = pd.DataFrame([transaction_dict])
    fraud_probability = float(model.predict_proba(input_df)[:, 1][0])

    risk_level, decision = make_decision(fraud_probability)
    model_version = get_model_version()

    log_prediction(
        transaction=transaction_dict,
        fraud_probability=fraud_probability,
        risk_level=risk_level,
        decision=decision,
        model_version=model_version,
    )

    return PredictionResponse(
        fraud_probability=fraud_probability,
        risk_level=risk_level,
        decision=decision,
        model_version=model_version,
    )


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    try:
        load_production_model()
        model_loaded = True
    except FileNotFoundError:
        model_loaded = False

    return HealthResponse(status="ok", model_loaded=model_loaded)


@app.get("/model-info", response_model=ModelInfoResponse)
def model_info() -> ModelInfoResponse:
    metrics = load_metrics()
    model_version = get_model_version()

    if metrics is None:
        return ModelInfoResponse(
            model_name="unknown",
            model_version=model_version,
            metrics_available=False,
        )

    test_metrics = metrics["test_metrics"]

    return ModelInfoResponse(
        model_name=metrics["model_name"],
        model_version=model_version,
        metrics_available=True,
        test_pr_auc=test_metrics["pr_auc"],
        test_roc_auc=test_metrics["roc_auc"],
        test_precision=test_metrics["precision"],
        test_recall=test_metrics["recall"],
        test_f1=test_metrics["f1"],
    )


@app.post("/predict", response_model=PredictionResponse)
def predict(transaction: TransactionRequest) -> PredictionResponse:
    return predict_single_transaction(transaction)


@app.post("/predict-batch", response_model=BatchPredictionResponse)
def predict_batch(request: BatchPredictionRequest) -> BatchPredictionResponse:
    predictions = [
        predict_single_transaction(transaction)
        for transaction in request.transactions
    ]

    return BatchPredictionResponse(
        count=len(predictions),
        predictions=predictions,
    )
