# Ticket Triage — Support Ticket Classification System

Classifies incoming customer support tickets by **category** and **priority**
using NLP + scikit-learn, exposed through a FastAPI backend and a clean
static dashboard frontend.

## Folder architecture

```
ticket-classifier/
├── backend/
│   ├── app/
│   │   ├── main.py               # FastAPI entrypoint
│   │   ├── api/
│   │   │   └── routes.py         # /classify, /health endpoints
│   │   ├── models/
│   │   │   └── schemas.py        # Pydantic request/response models
│   │   ├── services/
│   │   │   ├── classifier.py     # loads models, runs inference
│   │   │   └── priority.py       # hybrid ML + rule-based priority logic
│   │   └── utils/
│   │       └── text_cleaning.py  # shared spaCy cleaning/tokenizing
│   ├── data/
│   │   ├── generate_dataset.py   # builds a synthetic labeled dataset
│   │   └── tickets.csv           # generated dataset (created by script)
│   ├── notebooks/
│   │   ├── train_model.ipynb     # Jupyter notebook version of training
│   │   └── train.py              # script version of the same pipeline
│   ├── saved_models/             # trained .joblib pipelines (created by training)
│   └── requirements.txt
├── frontend/
│   ├── index.html                # dashboard UI
│   ├── css/style.css
│   └── js/{config.js, app.js}
└── README.md
```

## How it works

1. **Text preprocessing** (`utils/text_cleaning.py`) — lowercases, strips
   URLs/emails/punctuation/digits, then uses spaCy to tokenize, remove
   stopwords, and lemmatize. The exact same function runs at training time
   and at inference time so the model never sees a mismatch.
2. **Category classification** — a TF-IDF + calibrated LinearSVC pipeline
   predicts one of `Billing / Technical / Account / Product / General`.
3. **Priority logic** — a second TF-IDF + LinearSVC pipeline predicts
   `High / Medium / Low`, then `services/priority.py` blends that
   prediction with rule-based signals (urgency keywords, shouting/caps,
   exclamation marks, category weighting) so the final label reflects both
   what the model learned and obvious surface cues it might miss.
4. **API** — FastAPI exposes `POST /api/classify` and `GET /api/health`.
5. **Frontend** — a static dashboard posts ticket text to the API and
   renders category, priority, confidence, and the reasoning behind the
   priority decision.

## Running it — phase by phase

### Phase 1 — Environment setup
```bash
cd ticket-classifier/backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
python -m nltk.downloader punkt stopwords
```

### Phase 2 — Data & training
```bash
# still inside backend/
python data/generate_dataset.py      # creates data/tickets.csv
python notebooks/train.py            # trains + saves both models to saved_models/
# or open notebooks/train_model.ipynb in Jupyter to run it interactively
```
Swap in your own labeled export any time by replacing `data/tickets.csv`
with columns: `text, category, priority`.

### Phase 3 — Backend API
```bash
# still inside backend/
uvicorn app.main:app --reload --port 8000
```
Visit `http://localhost:8000/docs` for interactive API docs.

### Phase 4 — Frontend
Open `frontend/index.html` directly in a browser, or serve it:
```bash
cd ticket-classifier/frontend
python -m http.server 5500
```
Then visit `http://localhost:5500`. The dashboard calls the API at
`http://localhost:8000/api` (edit `frontend/js/config.js` if your backend
runs elsewhere).

## Extending this system

- Swap `LinearSVC` for `RandomForestClassifier` or a transformer embedding
  (e.g. `sentence-transformers`) if you have a larger labeled dataset.
- Add a `/feedback` endpoint so agents can correct mispredictions, then
  periodically retrain on the corrected labels.
- Add authentication and a ticket history database (Postgres) once this
  moves beyond a single-ticket classification tool into a full queue.
