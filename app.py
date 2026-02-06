import streamlit as st
from PIL import Image
import math
import os

# --- BASE DE DATOS COMPLETA NTP ISO 4427:2008 ---
DATOS_TUBERIA = {
    "SDR 33": {315: 9.7, 355: 10.9, 400: 12.3, 450: 13.8, 500: 15.3, 560: 17.2, 630: 19.3, 710: 21.8, 800: 24.5, 900: 27.6, 1000: 30.6, 1200: 36.7, 1400: 42.9, 1600: 49.0, 1800: 54.5, 2000: 60.6},
    "SDR 26": {50: 2.0, 63: 2.5, 75: 2.9, 90: 3.5, 110: 4.2, 160: 6.2, 200: 7.7, 250: 9.6, 280: 10.7, 315: 12.1, 355: 13.6, 400: 15.3, 450: 17.2, 500: 19.1, 560: 21.4, 630: 24.1, 710: 27.2, 800: 30.6, 900: 34.4, 1000: 38.2, 1200: 45.9, 1400: 53.5, 1600: 61.2, 1800: 69.1, 2000: 76.9},
    "SDR 21": {40: 2.0, 50: 2.4, 63: 3.0, 75: 3.6, 90: 4.3, 110: 5.3, 160: 7.7, 200: 9.6, 250: 11.9, 280: 13.4, 315: 15.0, 355: 16.9, 400: 19.1, 450: 21.5, 500: 23.9, 560: 26.7, 630: 30.0, 710: 33.8, 800: 38.1, 900: 42.9, 1000: 47.7, 1200: 57.2, 1400: 66.7, 1600: 76.2, 1800: 85.7, 2000: 95.2},
    "SDR 17": {32: 2.0, 40: 2.4, 50: 3.0, 63: 3.8, 75: 4.5, 90: 5.4, 110: 6.6, 160: 9.5, 200: 11.9, 250: 14.8, 280: 16.6, 315: 18.7, 355: 21.1, 400: 23.7, 450: 26.7, 500: 29.7, 560: 33.2, 630: 37.4, 710: 42.1, 800: 47.4, 900: 53.3, 1000: 59.3, 1200: 71.1, 1400: 82.4, 1600: 94.1, 1800: 105.9, 2000: 117.6},
    "SDR 13.6": {25: 2.0, 32: 2.4, 40: 3.0, 50: 3.7, 63: 4.7, 75: 5.6, 90: 6.7, 110: 8.1, 160: 11.8, 200: 14.7, 250: 18.4, 280: 20.6, 315: 23.2, 355: 26.1, 400: 29.4, 450: 33.1, 500: 36.8, 560: 41.2, 630: 46.3, 710: 52.2, 800: 58.8, 900: 66.2, 1000: 72.5, 1200: 88.2, 1400: 102.9, 1600: 117.6},
    "SDR 11": {20: 2.0, 25: 2.3, 32: 3.0, 40: 3.7, 50: 4.6, 63: 5.8, 75: 6.8, 90: 8.2, 110: 10.0, 160: 14.6, 200: 18.2, 250: 22.7, 280: 25.4, 315: 28.6, 355: 32.2, 400: 36.3, 450: 40.9, 500: 45.4, 560: 50.8, 630: 57.2, 710: 64.5, 800: 72.6, 900: 81.7, 1000: 90.2},
    "SDR 9": {20: 2.3, 25: 3.0, 32: 3.6, 40: 4.5, 50: 5.6, 63: 8.1, 75: 8.4, 90: 10.1, 110: 12.3, 160: 17.9, 200: 22.4, 250: 27.9, 280: 31.3, 315: 35.2, 355: 39.7, 400: 44.7, 450: 50.3, 500: 55.8, 560: 62.5, 630: 70.3, 710: 79.3, 800: 89.3},
    "SDR 7.4": {20: 3.0, 25: 3.5, 32: 4.4, 40: 5.5, 50: 6.9, 63: 8.6, 75: 10.3, 90: 12.3, 110: 15.1, 160: 21.9, 200: 27.4, 250: 34.2, 280: 38.3, 315: 43.1, 355: 48.5, 400: 54.7, 450: 61.5}
}

DN_PULGADAS = {
    20: "1/2", 25: "3/4", 32: "1", 40: "1-1/4", 50: "1-1/2", 63: "2.00", 75: "2-1/2", 
    90: "3", 110: "4", 160: "6", 200: "8", 250: "10", 280: "11", 315: "12", 355: "14", 
    400: "16", 450: "18", 500: "20", 560: "22", 630: "24", 710: "28", 800: "32", 900: "36", 1000: "40",
    1200: "48", 1400: "54", 1600: "64", 1800: "72", 2000: "80"
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

# --- INTERFAZ ---
st.set_page_config(page_title="Hans Longa - ADT HDPE", layout="centered")

# Carga de Logo
NOMBRE_IMAGEN = "LOGO PRINCIPAL.png"
if os.path.exists(NOMBRE_IMAGEN):
    st.image(NOMBRE_IMAGEN, width=250)
else:
    st.title("HIDRO-CALC ADT")

st.header("Cálculo de Altura Dinámica Total (ADT)")

col1, col2 = st.columns(2)
with col1:
    q_val = st.number_input("Caudal de Diseño", min_value=0.0, value=10.0)
    combo_q = st.selectbox("Unidades", ["L/s", "m³/h"])
with col2:
    temp = st.number_input("Temperatura del Agua (°C)", min_value=0.0, value=20.0)

st.subheader("Configuración de Tubería (NTP ISO 4427)")
sdr = st.selectbox("Seleccione SDR", list(DATOS_TUBERIA.keys()), index=5)
lista_dn_keys = sorted(DATOS_TUBERIA[sdr].keys())
lista_dn_labels = [f"{k} mm ({DN_PULGADAS.get(k, '?')}\")" for k in lista_dn_keys]
dn_seleccionado = st.selectbox("Diámetro Nominal (DN)", lista_dn_labels)
dn_mm = int(dn_seleccionado.split(" ")[0])

longitud = st.number_input("Longitud de Tubería (m)", min_value=0.0, value=100.0)
cota = st.number_input("Elevación / Cota (m)", min_value=0.0, value=10.0)

st.write("**Accesorios**")
c1, c2 = st.columns(2)
with c1: check_valvula = st.checkbox("Válvula Check (K=2.5)")
with c2: check_codo = st.checkbox("Codo 90° (K=2.5)")

if st.button("CALCULAR ADT", use_container_width=True):
    caudal = q_val / 1000 if combo_q == "L/s" else q_val / 3600
    espesor_mm = DATOS_TUBERIA[sdr].get(dn_mm)
    diam_int = (dn_mm - 2 * espesor_mm) / 1000
    
    vel = caudal / ((math.pi * (diam_int**2)) / 4)
    visco_cin = obtener_viscosidad(temp) / 1000 
    re = (vel * diam_int) / visco_cin
    f = calcular_friccion_colebrook(re, 0.000008 / diam_int)
    
    per_friccion = f * (longitud / diam_int) * (vel**2 / 19.62)
    per_secundarias = ((2.5 if check_valvula else 0) + (2.5 if check_codo else 0)) * (vel**2 / 19.62)
    
    adt = cota + per_friccion + per_secundarias
    st.success(f"### ADT: {adt:.2f} m.c.a.")
    st.info(f"Velocidad: {vel:.2f} m/s | Espesor: {espesor_mm} mm")

st.markdown("---")
st.caption("Aplicativo desarrollado por: Ing. Hans Longa")
