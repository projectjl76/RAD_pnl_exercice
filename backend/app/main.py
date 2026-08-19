from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import positions, pnl, risk

app = FastAPI(
    title="Risk & P&L Tool",
    description="Exercice for Interview",
    version="0.1.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(positions.router, prefix="/api/positions", tags=["positions"])
app.include_router(pnl.router, prefix="/api/pnl", tags=["pnl"])
app.include_router(risk.router, prefix="/api/risk", tags=["risk"])


@app.get("/api/health")
def health():
    return {"status": "ok"}
