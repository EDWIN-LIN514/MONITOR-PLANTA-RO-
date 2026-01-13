from __future__ import annotations

from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .config import AppConfig, load_config, save_config
from .models import ConfigPayload, ConsumptionPayload, OperationalEntry
from .storage import JSONStorage

app = FastAPI(title="PTAP Monitor API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_storage() -> tuple[AppConfig, JSONStorage]:
    config = load_config()
    storage = JSONStorage(config)
    return config, storage


def ensure_seed_data(storage: JSONStorage) -> None:
    storage.read(
        "chemicals.json",
        [
            {"nombre": "Antiescalante", "stock_inicial": 200.0, "stock": 180.0, "unidad": "L"},
            {"nombre": "Hipoclorito", "stock_inicial": 150.0, "stock": 120.0, "unidad": "L"},
            {"nombre": "Cloruro férrico", "stock_inicial": 100.0, "stock": 90.0, "unidad": "L"},
        ],
    )
    storage.read("operational.json", [])
    storage.read("consumption.json", [])


@app.on_event("startup")
async def startup_event() -> None:
    _, storage = get_storage()
    ensure_seed_data(storage)


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/config")
async def get_config() -> dict[str, str | float]:
    config, _ = get_storage()
    return {"data_dir": str(config.data_dir), "dp_threshold": config.dp_threshold}


@app.post("/api/config")
async def update_config(payload: ConfigPayload) -> dict[str, str]:
    data_dir = Path(payload.data_dir).expanduser()
    config = AppConfig(data_dir=data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)
    save_config(config)
    return {"status": "ok"}


@app.get("/api/operational")
async def list_operational() -> list[dict]:
    _, storage = get_storage()
    ensure_seed_data(storage)
    return storage.read("operational.json", [])


@app.post("/api/operational")
async def add_operational(entry: OperationalEntry) -> dict[str, str]:
    _, storage = get_storage()
    ensure_seed_data(storage)
    storage.append_operational(entry.model_dump())
    return {"status": "saved"}


@app.get("/api/chemicals")
async def list_chemicals() -> list[dict]:
    _, storage = get_storage()
    ensure_seed_data(storage)
    return storage.read("chemicals.json", [])


@app.post("/api/chemicals/consume")
async def consume_chemicals(payload: ConsumptionPayload) -> dict[str, str]:
    _, storage = get_storage()
    ensure_seed_data(storage)
    chemicals = storage.read("chemicals.json", [])
    chem_index = {item["nombre"].lower(): item for item in chemicals}

    updates = []
    for item in payload.items:
        key = item.nombre.lower()
        if key not in chem_index:
            raise HTTPException(status_code=404, detail=f"Químico no encontrado: {item.nombre}")
        chemical = chem_index[key]
        chemical["stock"] = max(0.0, float(chemical["stock"]) - item.consumo_diario)
        updates.append(
            {
                "fecha": payload.fecha.isoformat(),
                "nombre": chemical["nombre"],
                "consumo": item.consumo_diario,
                "stock_restante": chemical["stock"],
            }
        )

    storage.update_chemicals(list(chem_index.values()))
    storage.append_consumption(updates)
    return {"status": "updated"}


@app.get("/api/chemicals/consumption")
async def list_consumption() -> list[dict]:
    _, storage = get_storage()
    ensure_seed_data(storage)
    return storage.read("consumption.json", [])


@app.get("/api/alerts")
async def get_alerts() -> dict[str, list[dict]]:
    config, storage = get_storage()
    ensure_seed_data(storage)
    chemicals = storage.read("chemicals.json", [])
    operational = storage.read("operational.json", [])

    stock_alerts = []
    for item in chemicals:
        initial = float(item.get("stock_inicial", 0))
        if initial <= 0:
            continue
        remaining = float(item.get("stock", 0))
        percent = (remaining / initial) * 100
        if percent < 20:
            stock_alerts.append(
                {
                    "nombre": item.get("nombre"),
                    "percent": round(percent, 2),
                    "stock": remaining,
                }
            )

    dp_alerts = []
    if operational:
        last = operational[-1]
        dp = float(last["presiones"]["entrada"]) - float(last["presiones"]["salida"])
        if dp >= config.dp_threshold:
            dp_alerts.append(
                {
                    "mensaje": "ΔP alto: posible ensuciamiento de membranas",
                    "delta_p": round(dp, 2),
                }
            )

    return {"stock": stock_alerts, "delta_p": dp_alerts}
