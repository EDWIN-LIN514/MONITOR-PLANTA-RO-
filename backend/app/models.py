from __future__ import annotations

from datetime import date
from pydantic import BaseModel, Field


class PressureData(BaseModel):
    entrada: float = Field(..., ge=0)
    salida: float = Field(..., ge=0)
    rechazo: float = Field(..., ge=0)


class FlowData(BaseModel):
    permeado: float = Field(..., ge=0)
    rechazo: float = Field(..., ge=0)
    recirculacion: float = Field(..., ge=0)


class OperationalEntry(BaseModel):
    fecha: date
    presiones: PressureData
    caudales_gpm: FlowData


class ChemicalItem(BaseModel):
    nombre: str
    stock_inicial: float = Field(..., ge=0)
    stock: float = Field(..., ge=0)
    unidad: str = "L"


class ConsumptionItem(BaseModel):
    nombre: str
    consumo_diario: float = Field(..., ge=0)


class ConsumptionPayload(BaseModel):
    fecha: date
    items: list[ConsumptionItem]


class ConfigPayload(BaseModel):
    data_dir: str
