import plotly.graph_objects as go
import streamlit as st

def create_gauge(value, title, unit, min_val=0, max_val=10, thresholds=None):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = value,
        title = {'text': f"{title} ({unit})", 'font': {'size': 18}},
        gauge = {
            'axis': {'range': [min_val, max_val]},
            'bar': {'color': "#00cc96"},
            'steps': thresholds if thresholds else [],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': max_val * 0.9
            }
        }
    ))
    fig.update_layout(height=250, margin=dict(l=20, r=20, t=50, b=20))
    return fig

def create_line_chart(df, y_columns, title):
    fig = go.Figure()
    for col in y_columns:
        fig.add_trace(go.Scatter(x=df['Date'], y=df[col], name=col, mode='lines+markers'))
    
    fig.update_layout(
        title=title,
        xaxis_title="Fecha",
        yaxis_title="Valor",
        legend_title="Parámetro",
        hovermode="x unified",
        template="plotly_dark" if st.session_state.get('theme') == 'dark' else "plotly_white"
    )
    return fig
