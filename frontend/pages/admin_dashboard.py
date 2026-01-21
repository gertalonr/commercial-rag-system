import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from frontend.utils import api_request, format_tokens, format_cost, format_datetime

def show_admin_dashboard():
    st.title("📊 Dashboard Administrativo")
    
    # Botón de actualización
    col1, col2 = st.columns([6, 1])
    with col2:
        if st.button("🔄 Actualizar"):
            st.rerun()
    
    st.markdown("---")
    
    # Obtener métricas en tiempo real
    success, metrics = api_request("GET", "/admin/usage/realtime?hours=24")
    
    if success:
        # Tarjetas de métricas
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="📊 Total Tokens",
                value=format_tokens(metrics.get("total_tokens", 0)),
                delta=None
            )
        
        with col2:
            st.metric(
                label="💰 Coste Total",
                value=format_cost(metrics.get("total_cost_usd", 0.0)),
                delta=None
            )
        
        with col3:
            st.metric(
                label="🔍 Consultas",
                value=metrics.get("total_queries", 0),
                delta=None
            )
        
        with col4:
            st.metric(
                label="👥 Usuarios Activos",
                value=metrics.get("active_users", 0),
                delta=None
            )
        
        st.caption(f"Última actualización: {format_datetime(metrics.get('last_updated', ''))}")
    
    st.markdown("---")
    
    # Gráfico: Top usuarios por consumo
    st.subheader("🏆 Top Usuarios por Consumo (Hoy)")
    
    success_glob, users_data = api_request("GET", "/admin/usage/global")
    
    if success_glob and users_data:
        # Preparar datos para gráfico
        # Sorting by cost descending to get top consumers
        sorted_users = sorted(users_data, key=lambda x: x['total_cost_usd'], reverse=True)
        
        df = pd.DataFrame([
            {
                "usuario": u["user"]["username"],
                "coste": u["total_cost_usd"],
                "queries": u["total_queries"]
            }
            for u in sorted_users[:10]  # Top 10
        ])
        
        if not df.empty:
            # Gráfico de barras horizontal
            fig = px.bar(
                df,
                x="coste",
                y="usuario",
                orientation="h",
                text="coste",
                labels={"coste": "Coste (USD)", "usuario": "Usuario"},
                color="coste",
                color_continuous_scale="Blues"
            )
            
            fig.update_traces(texttemplate='$%{text:.4f}', textposition='outside')
            fig.update_layout(showlegend=False, height=400, yaxis={'categoryorder':'total ascending'})
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay datos de consumo para mostrar.")
    
    st.markdown("---")
    
    # Gráfico: Evolución temporal (últimos 7 días)
    st.subheader("📈 Uso en el Tiempo (Últimos 7 Días)")
    
    # TODO: Obtener datos históricos por día
    # Por ahora, datos de ejemplo
    # En la implementación real, necesitarías un endpoint que devuelva datos diarios
    
    st.info("💡 Gráfico de evolución temporal - Implementar con datos históricos")
    
    # Auto-refresh cada 30 segundos (opcional)
    # import time
    # time.sleep(30)
    # st.rerun()

# Alias para mantener compatibilidad con streamlit_app.py
admin_page = show_admin_dashboard
