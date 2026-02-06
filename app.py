Para que Streamlit encuentre la imagen en tu repositorio de GitHub, simplemente debemos usar el nombre exacto del archivo. Al desplegar la aplicación en la nube, el sistema buscará el archivo LOGO PRINCIPAL.png en la raíz de tu proyecto.

He actualizado la variable NOMBRE_IMAGEN y el bloque de carga para que coincida exactamente con tu archivo.

Python
import streamlit as st
from PIL import Image
import math
import os

# --- DATOS DE LA NORMA NTP ISO 4427 ---
DATOS_TUBERIA = {
    "SDR 33": {315: 9.7, 355: 10.9, 400: 12.3, 450: 13.8, 500: 15.3, 630: 19.3, 800: 24.5, 1000: 30.6},
    "SDR 26": {50: 2.0, 63: 2.5, 75: 2.9, 90: 3.5, 110: 4.2, 160: 6.2, 200: 7.7, 250: 9.6, 315: 12.1, 400: 15.3, 500: 19.1, 630: 24.1},
    "SDR 21": {40: 2.0, 50: 2.4, 63: 3.0, 75: 3.6, 90: 4.3, 110: 5.3, 160: 7.7, 200: 9.6, 250: 11.9, 315: 15.0, 400: 19.1, 500: 23.9},
    "SDR 17": {32: 2.0, 40: 2.4, 50: 3.0, 63: 3.8, 75: 4.5, 90: 5.4, 110: 6.6, 160: 9.5, 200: 11.9, 250: 14.8, 315: 18.7, 400: 23.7, 500: 29.7},
    "SDR 13.6": {25: 2.0, 32: 2.4, 40: 3.0, 50: 3.7, 63: 4.7, 75: 5.6, 90: 6.7, 110: 8.1, 160: 11.8, 200: 14.7, 250: 18.4, 315: 23.2, 400: 29.4, 500: 36.8},
    "SDR 11": {20: 2.0, 25: 2.3, 32: 3.0, 40: 3.7, 50: 4.6, 63: 5.8, 75: 6.8, 90: 8.2, 110: 10.0, 160: 14.6, 200: 18.2, 250: 22.7, 315: 28.6, 400: 36.3, 500: 45.4},
    "SDR 9": {20: 2.3, 25: 3.0, 32: 3.6, 40: 4.5, 50: 5.6, 63: 8.1, 75: 8.4, 90: 10.1, 110: 12.3, 160: 17.9, 200: 22.4, 250: 27.9, 315: 35.2, 400: 44.7, 500: 55.8},
    "SDR 7.4": {20: 3.0, 25: 3.5, 32: 4.4, 40: 5.5, 50: 6.9, 63: 8.6, 75: 10.3, 90: 12.3, 110: 15.1, 160: 21.9, 200: 27.4, 250: 34.2, 315: 43.1, 400: 54.7, 450: 61.5}
}

DN_PULGADAS = {
    20: "1/2", 25: "3/4", 32: "1", 40: "1-1/4", 50: "1-1/2", 63: "2.00", 75: "2-1/2", 
    90: "3", 110: "4", 160: "6", 200: "8", 250: "10", 315: "12", 400: "16", 450: "18", 500: "20"
}

def obtener_viscosidad(temp):
    datos_visco = {0: 0.001792, 10: 0.001308, 20: 0.001003, 30: 0.000798, 40: 0.000653, 
                   50: 0.000547, 60: 0.000467, 70: 0.000404, 80: 0.000355, 90: 0.000315, 100: 0.000282}
    t_base = (temp // 10) * 10
    if t_base >= 100: return datos_visco[100]
    v1, v2 = datos_visco[t_base], datos_visco[t_base + 10]
    return v1 + (v2 - v1) * (temp - t_base) / 10

def calcular_friccion_colebrook(re, rugosidad_relativa):
    if re < 2300: return 64 / re
    f = 0.02
    for _ in range(15):
        f = 1 / (-2 * math.log10((rugosidad_relativa / 3.7) + (2.51 / (re * math.sqrt(f)))))**2
    return f

# --- INTERFAZ STREAMLIT ---
st.set_page_config(page_title="Hans Longa - Innovación", layout="centered")

# --- ACTUALIZACIÓN DE LOGO PARA GITHUB ---
NOMBRE_IMAGEN = "LOGO PRINCIPAL.png"

if os.path.exists(NOMBRE_IMAGEN):
    st.image(NOMBRE_IMAGEN, width=250)
else:
    # Si no encuentra la imagen en el repo, muestra el texto alternativo
    st.title("TOMOCORP")
    st.info(f"Nota: Asegúrate de que '{NOMBRE_IMAGEN}' esté en la raíz de tu repositorio de GitHub.")

st.header("Cálculo de Altura Dinámica Total (ADT)")

# Entradas de Datos
col1, col2 = st.columns(2)
with col1:
    q_val = st.number_input("Caudal de Diseño", min_value=0.0, value=10.0, step=0.1)
    combo_q = st.selectbox("Unidades", ["L/s", "m³/h"])
with col2:
    temp = st.number_input("Temperatura del Agua (°C)", min_value=0.0, value=20.0)

st.subheader("Configuración de Tubería")
mrs = st.selectbox("Resistencia mínima requerida a largo plazo", ["PE-80", "PE-100"])
sdr = st.selectbox("SDR (Relación de Dimensiones)", list(DATOS_TUBERIA.keys()), index=5)

lista_dn_keys = sorted(DATOS_TUBERIA[sdr].keys())
lista_dn_labels = [f"{k} mm ({DN_PULGADAS.get(k, '?')}\")" for k in lista_dn_keys]
dn_seleccionado = st.selectbox("Diámetro Nominal (DN)", lista_dn_labels)
dn_mm = int(dn_seleccionado.split(" ")[0])

st.subheader("Instalación")
longitud = st.number_input("Longitud de Tubería (m)", min_value=0.0, value=100.0)
cota = st.number_input("Elevación / Cota (m)", min_value=0.0, value=10.0)

st.subheader("Accesorios")
check_valvula = st.checkbox("Válvula Check (K=2.5)")
check_codo = st.checkbox("Codo 90° (K=2.5)")

if st.button("CALCULAR ADT", use_container_width=True):
    try:
        caudal = q_val / 1000 if combo_q == "L/s" else q_val / 3600
        espesor_mm = DATOS_TUBERIA[sdr].get(dn_mm)
        diam_int = (dn_mm - 2 * espesor_mm) / 1000
        
        rugosidad_abs = 0.000008 
        visco_cin = obtener_viscosidad(temp) / 1000 
        area = (math.pi * (diam_int**2)) / 4
        vel = caudal / area
        re = (vel * diam_int) / visco_cin
        
        f = calcular_friccion_colebrook(re, rugosidad_abs / diam_int)
        g = 9.81
        
        per_friccion = f * (longitud / diam_int) * (vel**2 / (2 * g))
        k_total = (2.5 if check_valvula else 0) + (2.5 if check_codo else 0)
        per_secundarias = k_total * (vel**2 / (2 * g))
        
        adt = cota + per_friccion + per_secundarias
        
        st.success(f"### ADT Total: {adt:.2f} m.c.a.")
        
        with st.expander("Ver detalles técnicos del cálculo"):
            st.write(f"**Espesor:** {espesor_mm} mm")
            st.write(f"**Diámetro Interno:** {diam_int*1000:.2f} mm")
            st.write(f"**Velocidad:** {vel:.2f} m/s")
            st.write(f"**Pérdidas Mayores:** {per_friccion:.3f} m")
            st.write(f"**Pérdidas Menores:** {per_secundarias:.3f} m")

    except Exception as e:
        st.error(f"Error: {e}")

# --- PIE DE PÁGINA ---
st.markdown("---")
st.caption("Aplicativo desarrollado por: Ing. Hans Longa")
