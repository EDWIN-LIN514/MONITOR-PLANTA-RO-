import { useEffect, useMemo, useState } from "react";
import {
  LineChart,
  Line,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Legend
} from "recharts";

const initialOperational = {
  fecha: new Date().toISOString().slice(0, 10),
  presiones: { entrada: 0, salida: 0, rechazo: 0 },
  caudales_gpm: { permeado: 0, rechazo: 0, recirculacion: 0 }
};

const roles = ["Operador", "Supervisor"];

const apiFetch = async (url, options = {}) => {
  const response = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options
  });
  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || "Error de comunicación con la API");
  }
  return response.json();
};

const formatDate = (value) => value?.slice(5) ?? "";

const AlertBadge = ({ label, tone = "danger" }) => (
  <div className={`alert alert-${tone}`}>{label}</div>
);

export default function App() {
  const [role, setRole] = useState(() => localStorage.getItem("role") || "Operador");
  const [operational, setOperational] = useState([]);
  const [chemicals, setChemicals] = useState([]);
  const [consumption, setConsumption] = useState([]);
  const [alerts, setAlerts] = useState({ stock: [], delta_p: [] });
  const [config, setConfig] = useState({ data_dir: "", dp_threshold: 15 });
  const [opForm, setOpForm] = useState(initialOperational);
  const [consumptionForm, setConsumptionForm] = useState({
    fecha: new Date().toISOString().slice(0, 10),
    items: []
  });
  const [statusMessage, setStatusMessage] = useState("");
  const [errorMessage, setErrorMessage] = useState("");

  const refreshAll = async () => {
    const [opData, chemData, consData, alertData, configData] = await Promise.all([
      apiFetch("/api/operational"),
      apiFetch("/api/chemicals"),
      apiFetch("/api/chemicals/consumption"),
      apiFetch("/api/alerts"),
      apiFetch("/api/config")
    ]);
    setOperational(opData);
    setChemicals(chemData);
    setConsumption(consData);
    setAlerts(alertData);
    setConfig(configData);

    setConsumptionForm((prev) => ({
      ...prev,
      items: chemData.map((item) => ({ nombre: item.nombre, consumo_diario: 0 }))
    }));
  };

  useEffect(() => {
    refreshAll().catch((err) => setErrorMessage(err.message));
  }, []);

  useEffect(() => {
    localStorage.setItem("role", role);
  }, [role]);

  const handleOperationalSubmit = async (event) => {
    event.preventDefault();
    setStatusMessage("");
    setErrorMessage("");
    try {
      await apiFetch("/api/operational", {
        method: "POST",
        body: JSON.stringify(opForm)
      });
      setStatusMessage("Registro operativo guardado.");
      setOpForm(initialOperational);
      await refreshAll();
    } catch (err) {
      setErrorMessage(err.message);
    }
  };

  const handleConsumptionSubmit = async (event) => {
    event.preventDefault();
    setStatusMessage("");
    setErrorMessage("");
    try {
      await apiFetch("/api/chemicals/consume", {
        method: "POST",
        body: JSON.stringify(consumptionForm)
      });
      setStatusMessage("Consumo de químicos actualizado.");
      await refreshAll();
    } catch (err) {
      setErrorMessage(err.message);
    }
  };

  const handleConfigSubmit = async (event) => {
    event.preventDefault();
    setStatusMessage("");
    setErrorMessage("");
    try {
      await apiFetch("/api/config", {
        method: "POST",
        body: JSON.stringify({ data_dir: config.data_dir })
      });
      setStatusMessage("Ruta de datos actualizada.");
    } catch (err) {
      setErrorMessage(err.message);
    }
  };

  const pressureChartData = useMemo(
    () =>
      operational.map((item) => ({
        fecha: formatDate(item.fecha),
        entrada: item.presiones.entrada,
        salida: item.presiones.salida,
        rechazo: item.presiones.rechazo,
        delta_p: item.presiones.entrada - item.presiones.salida
      })),
    [operational]
  );

  const flowChartData = useMemo(
    () =>
      operational.map((item) => ({
        fecha: formatDate(item.fecha),
        permeado: item.caudales_gpm.permeado,
        rechazo: item.caudales_gpm.rechazo,
        recirculacion: item.caudales_gpm.recirculacion
      })),
    [operational]
  );

  const consumptionChartData = useMemo(() => {
    const grouped = {};
    consumption.forEach((item) => {
      if (!grouped[item.fecha]) {
        grouped[item.fecha] = { fecha: formatDate(item.fecha) };
      }
      grouped[item.fecha][item.nombre] = (grouped[item.fecha][item.nombre] || 0) + item.consumo;
    });
    return Object.values(grouped);
  }, [consumption]);

  const lastOperational = operational[operational.length - 1];

  return (
    <div className="app">
      <aside className="sidebar">
        <h1>PTAP Monitor</h1>
        <p className="subtitle">Ósmosis inversa · Planta de tratamiento</p>
        <div className="card">
          <label>Rol activo</label>
          <select value={role} onChange={(event) => setRole(event.target.value)}>
            {roles.map((item) => (
              <option key={item} value={item}>
                {item}
              </option>
            ))}
          </select>
        </div>
        <div className="card">
          <h3>Alertas</h3>
          {alerts.delta_p.length === 0 && alerts.stock.length === 0 ? (
            <span className="muted">Sin alertas críticas.</span>
          ) : (
            <>
              {alerts.delta_p.map((alert, index) => (
                <AlertBadge
                  key={`dp-${index}`}
                  label={`${alert.mensaje} (ΔP ${alert.delta_p})`}
                />
              ))}
              {alerts.stock.map((alert, index) => (
                <AlertBadge
                  key={`stock-${index}`}
                  label={`Stock bajo: ${alert.nombre} (${alert.percent}%)`}
                />
              ))}
            </>
          )}
        </div>
        <div className="card">
          <h3>Ruta de datos</h3>
          <p className="muted">{config.data_dir || "Sin configurar"}</p>
        </div>
      </aside>

      <main className="content">
        <header className="header">
          <div>
            <h2>Panel operativo</h2>
            <p className="muted">
              Registro diario de presiones, caudales y químicos · {role}
            </p>
          </div>
          <div className="header-cards">
            <div className="stat">
              <span>Última lectura</span>
              <strong>{lastOperational?.fecha ?? "--"}</strong>
            </div>
            <div className="stat">
              <span>ΔP umbral</span>
              <strong>{config.dp_threshold} psi</strong>
            </div>
          </div>
        </header>

        {statusMessage && <div className="notice success">{statusMessage}</div>}
        {errorMessage && <div className="notice error">{errorMessage}</div>}

        <section className="grid">
          <div className="panel">
            <h3>Registrar presiones y caudales</h3>
            <form onSubmit={handleOperationalSubmit} className="form">
              <label>
                Fecha
                <input
                  type="date"
                  value={opForm.fecha}
                  onChange={(event) =>
                    setOpForm({ ...opForm, fecha: event.target.value })
                  }
                />
              </label>
              <div className="form-row">
                <label>
                  Presión de entrada (psi)
                  <input
                    type="number"
                    min="0"
                    value={opForm.presiones.entrada}
                    onChange={(event) =>
                      setOpForm({
                        ...opForm,
                        presiones: {
                          ...opForm.presiones,
                          entrada: Number(event.target.value)
                        }
                      })
                    }
                  />
                </label>
                <label>
                  Presión de salida (psi)
                  <input
                    type="number"
                    min="0"
                    value={opForm.presiones.salida}
                    onChange={(event) =>
                      setOpForm({
                        ...opForm,
                        presiones: {
                          ...opForm.presiones,
                          salida: Number(event.target.value)
                        }
                      })
                    }
                  />
                </label>
                <label>
                  Presión de rechazo (psi)
                  <input
                    type="number"
                    min="0"
                    value={opForm.presiones.rechazo}
                    onChange={(event) =>
                      setOpForm({
                        ...opForm,
                        presiones: {
                          ...opForm.presiones,
                          rechazo: Number(event.target.value)
                        }
                      })
                    }
                  />
                </label>
              </div>
              <div className="form-row">
                <label>
                  Caudal de permeado (GPM)
                  <input
                    type="number"
                    min="0"
                    value={opForm.caudales_gpm.permeado}
                    onChange={(event) =>
                      setOpForm({
                        ...opForm,
                        caudales_gpm: {
                          ...opForm.caudales_gpm,
                          permeado: Number(event.target.value)
                        }
                      })
                    }
                  />
                </label>
                <label>
                  Caudal de rechazo (GPM)
                  <input
                    type="number"
                    min="0"
                    value={opForm.caudales_gpm.rechazo}
                    onChange={(event) =>
                      setOpForm({
                        ...opForm,
                        caudales_gpm: {
                          ...opForm.caudales_gpm,
                          rechazo: Number(event.target.value)
                        }
                      })
                    }
                  />
                </label>
                <label>
                  Caudal de recirculación (GPM)
                  <input
                    type="number"
                    min="0"
                    value={opForm.caudales_gpm.recirculacion}
                    onChange={(event) =>
                      setOpForm({
                        ...opForm,
                        caudales_gpm: {
                          ...opForm.caudales_gpm,
                          recirculacion: Number(event.target.value)
                        }
                      })
                    }
                  />
                </label>
              </div>
              <button type="submit">Guardar registro</button>
            </form>
          </div>

          <div className="panel">
            <h3>Consumo diario de químicos</h3>
            <form onSubmit={handleConsumptionSubmit} className="form">
              <label>
                Fecha
                <input
                  type="date"
                  value={consumptionForm.fecha}
                  onChange={(event) =>
                    setConsumptionForm({
                      ...consumptionForm,
                      fecha: event.target.value
                    })
                  }
                />
              </label>
              <div className="form-row">
                {consumptionForm.items.map((item, index) => (
                  <label key={item.nombre}>
                    {item.nombre} (L)
                    <input
                      type="number"
                      min="0"
                      value={item.consumo_diario}
                      onChange={(event) => {
                        const items = [...consumptionForm.items];
                        items[index] = {
                          ...items[index],
                          consumo_diario: Number(event.target.value)
                        };
                        setConsumptionForm({ ...consumptionForm, items });
                      }}
                    />
                  </label>
                ))}
              </div>
              <button type="submit">Registrar consumo</button>
            </form>
            <div className="chem-list">
              {chemicals.map((item) => (
                <div
                  key={item.nombre}
                  className={`chem-card ${{
                    danger:
                      item.stock_inicial > 0 &&
                      (item.stock / item.stock_inicial) * 100 < 20
                  }.danger ? "danger" : ""}`}
                >
                  <h4>{item.nombre}</h4>
                  <p>
                    Stock restante: <strong>{item.stock}</strong> {item.unidad}
                  </p>
                  <p className="muted">Inicial: {item.stock_inicial} {item.unidad}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="grid">
          <div className="panel">
            <h3>Tendencia de presiones (psi)</h3>
            <div className="chart">
              <ResponsiveContainer width="100%" height={260}>
                <LineChart data={pressureChartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="fecha" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="entrada" stroke="#2563eb" />
                  <Line type="monotone" dataKey="salida" stroke="#0ea5e9" />
                  <Line type="monotone" dataKey="rechazo" stroke="#f97316" />
                  <Line type="monotone" dataKey="delta_p" stroke="#ef4444" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
          <div className="panel">
            <h3>Tendencia de caudales (GPM)</h3>
            <div className="chart">
              <ResponsiveContainer width="100%" height={260}>
                <LineChart data={flowChartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="fecha" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="permeado" stroke="#22c55e" />
                  <Line type="monotone" dataKey="rechazo" stroke="#f59e0b" />
                  <Line type="monotone" dataKey="recirculacion" stroke="#0f766e" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </section>

        <section className="grid">
          <div className="panel">
            <h3>Consumo de químicos (L)</h3>
            <div className="chart">
              <ResponsiveContainer width="100%" height={260}>
                <LineChart data={consumptionChartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="fecha" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  {chemicals.map((item) => (
                    <Line
                      key={item.nombre}
                      type="monotone"
                      dataKey={item.nombre}
                      stroke="#64748b"
                    />
                  ))}
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="panel">
            <h3>Configuración de almacenamiento</h3>
            <form onSubmit={handleConfigSubmit} className="form">
              <label>
                Ruta de datos local
                <input
                  type="text"
                  value={config.data_dir}
                  onChange={(event) =>
                    setConfig({ ...config, data_dir: event.target.value })
                  }
                />
              </label>
              {role !== "Supervisor" && (
                <p className="muted">
                  Solo los supervisores pueden cambiar la ruta de datos.
                </p>
              )}
              <button type="submit" disabled={role !== "Supervisor"}>
                Guardar configuración
              </button>
            </form>
          </div>
        </section>
      </main>
    </div>
  );
}
