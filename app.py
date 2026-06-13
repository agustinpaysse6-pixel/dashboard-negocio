import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from openai import OpenAI

st.set_page_config(page_title="Dashboard Negocio", page_icon="📊", layout="wide")

st.title("📊 Dashboard de tu Negocio")
st.markdown("---")

api_key = st.sidebar.text_input("🔑 OpenAI API Key", type="password")
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

    ventas_dia = df[df["Tipo"] == "Venta"].groupby("Fecha")["Total"].sum().reset_index()
    fig1, ax1 = plt.subplots(figsize=(7, 3))
    ax1.bar(ventas_dia["Fecha"].astype(str), ventas_dia["Total"], color="#2E75B6")
    ax1.set_title("Ventas por día")
    plt.xticks(rotation=45)
    st.pyplot(fig1)

    top_productos = df[df["Tipo"] == "Venta"].groupby("Producto")["Total"].sum().sort_values(ascending=False).reset_index()
    fig2, ax2 = plt.subplots(figsize=(7, 3))
    ax2.bar(top_productos["Producto"], top_productos["Total"], color="#70AD47")
    ax2.set_title("Top productos más vendidos")
    plt.xticks(rotation=45)
    st.pyplot(fig2)

    st.markdown("---")
    st.subheader("🤖 Preguntale a la IA sobre tu negocio")

    pregunta = st.text_input("¿Qué querés saber?", placeholder="Ej: ¿Cuál fue el producto más vendido?")

    if pregunta and api_key:
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
    elif pregunta and not api_key:
        st.warning("Ingresá tu API Key en el panel izquierdo.")

    st.markdown("---")
    st.subheader("🗂 Datos completos")
    st.dataframe(df)

else:
    st.info("Subí un archivo Excel para ver el análisis.")