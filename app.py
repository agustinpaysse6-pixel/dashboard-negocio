import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from openai import OpenAI
import os

st.set_page_config(page_title="Dashboard Negocio", page_icon="📊", layout="wide")

st.title("📊 Dashboard de tu Negocio")
st.markdown("---")

archivo = st.file_uploader("Subí tu Excel de ventas", type=["xlsx"])

if archivo:
    df = pd.read_excel(archivo)
    df["Total"] = df["Cantidad"] * df["Precio Unitario"]

    ventas = df[df["Tipo"] == "Venta"]["Total"].sum()
    gastos = df[df["Tipo"] == "Gasto"]["Total"].sum()
    ganancia = ventas - gastos

    col1, col2, col3 = st.columns(3)
    col1.metric("💰 Ventas totales", f"$ {ventas:,.0f}")
    col2.metric("📦 Gastos totales", f"$ {gastos:,.0f}")
    col3.metric("✅ Ganancia", f"$ {ganancia:,.0f}")

    st.markdown("---")

    # Ventas por día
    ventas_dia = df[df["Tipo"] == "Venta"].groupby("Fecha")["Total"].sum().reset_index()
    fig1 = go.Figure(go.Bar(x=ventas_dia["Fecha"].astype(str), y=ventas_dia["Total"], marker_color="#2E75B6"))
    fig1.update_layout(title="Ventas por día", xaxis_title="Fecha", yaxis_title="Total")
    st.plotly_chart(fig1, use_container_width=True)

    # Productos
    productos = df[df["Tipo"] == "Venta"].groupby("Producto").agg(
        Total=("Total", "sum"),
        Cantidad=("Cantidad", "sum")
    ).reset_index().sort_values("Total", ascending=False)

    productos["Rentabilidad"] = productos["Total"] / productos["Cantidad"]

    col4, col5 = st.columns(2)

    with col4:
        fig2 = go.Figure(go.Bar(
            x=productos["Producto"], y=productos["Total"],
            marker_color="#70AD47"
        ))
        fig2.update_layout(title="Ventas por producto", xaxis_title="Producto", yaxis_title="Total")
        st.plotly_chart(fig2, use_container_width=True)

    with col5:
        fig3 = go.Figure(go.Bar(
            x=productos["Producto"], y=productos["Rentabilidad"],
            marker_color="#ED7D31"
        ))
        fig3.update_layout(title="Rentabilidad por producto ($ por unidad)", xaxis_title="Producto", yaxis_title="$ por unidad")
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown("---")
    st.subheader("🏆 Ranking de productos")
    col6, col7 = st.columns(2)
    with col6:
        st.markdown("**Más vendidos**")
        st.dataframe(productos[["Producto", "Total", "Cantidad"]].head(3).reset_index(drop=True))
    with col7:
        st.markdown("**Menos vendidos**")
        st.dataframe(productos[["Producto", "Total", "Cantidad"]].tail(3).reset_index(drop=True))

    st.markdown("---")
    st.subheader("🤖 Preguntale a la IA sobre tu negocio")
    pregunta = st.text_input("¿Qué querés saber?", placeholder="Ej: ¿Cuál fue el producto más vendido?")

    if pregunta:
        api_key = st.secrets["OPENAI_API_KEY"]
        client = OpenAI(api_key=api_key)
        resumen = df.to_string(index=False)
        respuesta = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Sos un asistente que analiza datos de un negocio. Respondé en español, de forma clara y concisa."},
                {"role": "user", "content": f"Estos son los datos del negocio:\n{resumen}\n\nPregunta: {pregunta}"}
            ]
        )
        st.success(respuesta.choices[0].message.content)

    st.markdown("---")
    st.subheader("🗂 Datos completos")
    st.dataframe(df)

else:
    st.info("Subí un archivo Excel para ver el análisis.")