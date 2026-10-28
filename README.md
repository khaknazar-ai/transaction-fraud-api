# Transaction Fraud API

An inference-only FastAPI demo that scores PaySim-style transaction records. It is not validated for real financial decisions.

## Run

The API requires Python 3.9 and an authorized `models/production_model.pkl` artifact, which is not included. Without it, the service can start but predictions are unavailable.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-api.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Alternatively, place the authorized model in `models/` and run `docker compose up --build`. The API docs are at <http://127.0.0.1:8000/docs>; `/health`, `/model-info`, `/predict`, and `/predict-batch` are the service endpoints.

## Results and limitations

Evaluation output is omitted from this runtime bundle; the full checkout stores it in `reports/metrics.json`. The test split comes from a 300,000-row development sample that preserves fraud cases and samples normal transactions; its fraud share is about 2.74%, compared with about 0.129% in the original PaySim data. Reported metrics use a 0.50 threshold, while the API risk bands use 0.30 and 0.70. These figures do not establish real-world performance.

The service has no authentication, rate limiting, or log retention policy. It appends submitted transaction features to `logs/predictions.csv`; do not send personal or production data. Load only a trusted model artifact.

## Dependencies and publication

Pinned dependencies are listed in [`requirements-api.txt`](requirements-api.txt): [FastAPI](https://fastapi.tiangolo.com/), [Uvicorn](https://github.com/encode/uvicorn), [pandas](https://pandas.pydata.org/docs/), [NumPy](https://numpy.org/doc/), [scikit-learn](https://scikit-learn.org/stable/), [joblib](https://joblib.readthedocs.io/en/stable/), [PyYAML](https://pyyaml.org/wiki/PyYAMLDocumentation), and [Pydantic](https://docs.pydantic.dev/latest/).

The source checkout has no project license, and the model and dataset redistribution terms and attribution are unverified. Confirm rights and add the appropriate license and notices before publishing.
