# PTAP Monitor (Ósmosis Inversa)

Aplicación web industrial para el monitoreo de una Planta de Tratamiento de Agua Potable (PTAP) con ósmosis inversa. Incluye backend en FastAPI, frontend en React y almacenamiento local configurable mediante archivos JSON.

## Estructura del proyecto

```
.
├── backend
│   ├── app
│   │   ├── config.py
│   │   ├── main.py
│   │   ├── models.py
│   │   └── storage.py
│   ├── config.json
│   └── requirements.txt
├── data
│   ├── chemicals.json
│   ├── consumption.json
│   └── operational.json
├── frontend
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── src
│       ├── App.jsx
│       ├── main.jsx
│       └── styles.css
└── README.md
```

## Requisitos

- Python 3.10+
- Node.js 18+

## Instalación rápida

### Backend (FastAPI)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Frontend (React)

```bash
cd frontend
npm install
npm run dev
```

La interfaz estará disponible en `http://localhost:5173` y el backend en `http://localhost:8000`.

## Configuración de almacenamiento local

- Por defecto los datos se guardan en la carpeta `data/`.
- Para cambiarla desde la UI, usa la sección **Configuración de almacenamiento** (solo Supervisor).
- También puedes definir la variable de entorno `DATA_DIR` antes de iniciar el backend.

## Archivos de ejemplo

En la carpeta `data/` se incluyen archivos JSON con datos de ejemplo para:

- Presiones y caudales: `operational.json`
- Inventario y stock de químicos: `chemicals.json`
- Consumos diarios: `consumption.json`

## Funcionalidades principales

- Registro de presiones (entrada, salida, rechazo)
- Registro de caudales en GPM (permeado, rechazo, recirculación)
- Monitoreo de químicos (stock inicial, consumo diario y stock restante)
- Alertas visuales:
  - Stock < 20% se muestra en rojo
  - ΔP alto = posible ensuciamiento de membranas
- Gráficos de tendencias para presiones, caudales y químicos
- Roles: Operador y Supervisor
