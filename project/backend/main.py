from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from model import calculate_risk

app = FastAPI(title="Smart Patrol Dashboard")

# Fix CORS so the frontend can retrieve data without errors
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/heatmap")
def heatmap():
    return calculate_risk()
