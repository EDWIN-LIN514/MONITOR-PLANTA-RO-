import streamlit as st
import pandas as pd
from datetime import datetime
import os

from storage import ROStorage
from logic import analyze_dp_trend, calculate_daily_production, check_stock_alerts
from dashboard import create_gauge, create_line_chart

# Page config
st.set_page_config(page_title="RO Monitoring System", layout="wide", initial_sidebar_state="expanded")

# CSS for styling
st.markdown("""
<style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    [data-testid="stSidebar"] { background-color: #1e293b; color: white; }
</style>
""", unsafe_allow_html=True)

# Session State Initialization
if 'role' not in st.session_state:
    st.session_state.role = None
if 'data_path' not in st.session_state:
    st.session_state.data_path = os.getcwd()

# Sidebar Navigation
with st.sidebar:
    st.title("🌊 RO Plant Pro")
    if st.session_state.role is None:
        st.subheader("Login")
        user = st.text_input("Usuario")
        passw = st.text_input("Contraseña", type="password")
        if st.button("Ingresar"):
            if user.lower() == "admin" and passw == "admin":
                st.session_state.role = "Supervisor"
            elif user.lower() == "oper" and passw == "oper":
                st.session_state.role = "Operador"
            else:
                st.error("Credenciales incorrectas")
    else:
        st.write(f"Conectado como: **{st.session_state.role}**")
        if st.button("Cerrar Sesión"):
            st.session_state.role = None
            st.rerun()
            
    st.divider()
    page = st.selectbox("Menu", ["Dashboard", "Ingreso de Datos", "Inventario", "Configuración"])

# Initialize storage
storage = ROStorage(st.session_state.data_path)

# --- Pages Logic ---

if st.session_state.role is None:
    st.warning("Por favor inicie sesión para continuar.")
    st.info("Demo: admin/admin o oper/oper")
else:
    if page == "Dashboard":
        st.title("📊 Panel de Monitoreo")
        df = storage.get_operational_data()
        
        if df.empty:
            st.info("No hay datos históricos. Por favor ingrese datos diarios.")
        else:
            # Alerts row
            is_inc, slope = analyze_dp_trend(df)
            if is_inc:
                st.error(f"🚨 **ALERTA: Anticipación de Saturación de Membranas** (Tendencia ΔP positiva: {slope:.3f})")
            
            # Gauges
            last_entry = df.iloc[-1]
            c1, c2, c3, c4 = st.columns(4)
            with c1: st.plotly_chart(create_gauge(last_entry['P_In'], "P. Entrada", "psi", 0, 400), use_container_width=True)
            with c2: st.plotly_chart(create_gauge(last_entry['P_Out'], "P. Salida", "psi", 0, 400), use_container_width=True)
            with c3: st.plotly_chart(create_gauge(last_entry['F_Perm'], "C. Permeado", "LPH", 0, 2000), use_container_width=True)
            with c4: st.plotly_chart(create_gauge(last_entry['F_Rej'], "C. Rechazo", "LPH", 0, 2000), use_container_width=True)

            # Trends
            st.subheader("Evolución de Presiones (ΔP)")
            df['DP'] = df['P_In'] - df['P_Out']
            st.plotly_chart(create_line_chart(df, ['P_In', 'P_Out', 'DP'], "Tendencia de Presiones"), use_container_width=True)

    elif page == "Ingreso de Datos":
        st.title("📝 Registro de Operación Diaria")
        with st.form("entry_form"):
            c1, c2 = st.columns(2)
            with c1:
                st.subheader("Presiones (psi)")
                p_in = st.number_input("Entrada", min_value=0.0)
                p_out = st.number_input("Salida", min_value=0.0)
                p_perm = st.number_input("Permeado", min_value=0.0)
                p_rej = st.number_input("Rechazo", min_value=0.0)
                p_rec = st.number_input("Recirculación", min_value=0.0)
            with c2:
                st.subheader("Caudales (LPH)")
                f_perm = st.number_input("Flujo Permeado", min_value=0.0)
                f_rej = st.number_input("Flujo Rechazo", min_value=0.0)
                f_rec = st.number_input("Flujo Recirculación", min_value=0.0)
                st.subheader("Producción")
                meter = st.number_input("Lectura Contómetro (L)", min_value=0.0)
            
            st.subheader("Consumo Químicos")
            chem_cons = {}
            inv_df = storage.get_inventory()
            for chem in inv_df['Chemical']:
                chem_cons[chem] = st.number_input(f"Consumo {chem} (L)", min_value=0.0)

            if st.form_submit_button("Guardar Registro"):
                # Calculate production diff
                df = storage.get_operational_data()
                last_meter = df.iloc[-1]['Meter_Reading'] if not df.empty else meter
                daily_prod = calculate_daily_production(meter, last_meter)
                
                # Save operational
                new_data = {
                    'Date': datetime.now().strftime("%Y-%m-%d"),
                    'P_In': p_in, 'P_Out': p_out, 'P_Perm': p_perm, 'P_Rej': p_rej, 'P_Rec': p_rec,
                    'F_Perm': f_perm, 'F_Rej': f_rej, 'F_Rec': f_rec, 'Meter_Reading': meter
                }
                storage.save_operational_entry(new_data)
                
                # Update inventory
                for chem, cons in chem_cons.items():
                    inv_df.loc[inv_df['Chemical'] == chem, 'Stock'] -= cons
                storage.update_inventory(inv_df)
                
                st.success(f"Registro guardado con éxito. Producción del día: {daily_prod} L")

    elif page == "Inventario":
        st.title("🧪 Gestión de Químicos")
        inv_df = storage.get_inventory()
        
        # Alerts
        alerts = check_stock_alerts(inv_df)
        for alert in alerts:
            st.error(alert)
        
        # Display table
        st.table(inv_df)
        
        if st.session_state.role == "Supervisor":
            st.subheader("Ajuste de Stock (Solo Supervisor)")
            with st.form("inv_adjust"):
                chem_to_adj = st.selectbox("Químico", inv_df['Chemical'])
                new_stock = st.number_input("Nuevo Stock Inicial", min_value=0.0)
                if st.form_submit_button("Actualizar Stock"):
                    inv_df.loc[inv_df['Chemical'] == chem_to_adj, 'Stock'] = new_stock
                    storage.update_inventory(inv_df)
                    st.success("Stock actualizado")
                    st.rerun()

    elif page == "Configuración":
        st.title("⚙️ Configuración del Sistema")
        if st.session_state.role != "Supervisor":
            st.error("Acceso restringido a Supervisores.")
        else:
            new_path = st.text_input("Ruta de Almacenamiento Local", value=st.session_state.data_path)
            if st.button("Guardar Configuración"):
                st.session_state.data_path = new_path
                st.success("Configuración actualizada. Reinicie para aplicar cambios profundos.")
