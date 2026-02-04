import streamlit as st
import yfinance as yf
import pickle
import numpy as np
from datetime import datetime

# --- PAGE CONFIG ---
st.set_page_config(page_title="Gold AI Premium", page_icon="✨", layout="wide")

# --- ADVANCED CUSTOM CSS ---
st.markdown("""
    <style>
    /* Background Image & Overlay */
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), 
                    url("https://images.moneycontrol.com/static-mcnews/2025/08/20250805152150_Gold-rep-2.jpg?impolicy=website&width=770&height=431=80");
        background-size: cover;
        background-attachment: fixed;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a1a 0%, #2d2d2d 100%);
        border-right: 2px solid #fbbf24;
    }
    
    /* Luxury Header */
    .main-title {
        background: -webkit-linear-gradient(#fbbf24, #d97706);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        font-size: 4rem;
        font-weight: 900;
        letter-spacing: -1px;
        margin-bottom: 0px;
    }

    /* Glassmorphism Metric Cards */
    div[data-testid="stMetric"] {
        background: rgba(255, 215, 0, 0.05);
        border: 1px solid rgba(251, 191, 36, 0.3);
        backdrop-filter: blur(10px);
        padding: 20px;
        border-radius: 20px;
        text-align: center;
        transition: 0.4s;
    }
    div[data-testid="stMetric"]:hover {
        border: 1px solid #fbbf24;
        background: rgba(251, 191, 36, 0.1);
    }

    /* Input Fields styling */
    .stNumberInput, .stDateInput {
        background-color: rgba(255,255,255,0.05);
        border-radius: 10px;
    }

    /* Golden Button */
    .stButton>button {
        background: linear-gradient(90deg, #fbbf24 0%, #d97706 100%) !important;
        color: black !important;
        font-size: 20px !important;
        font-weight: bold !important;
        border-radius: 50px !important;
        border: none !important;
        box-shadow: 0 10px 20px rgba(217, 119, 6, 0.3);
    }
    </style>
    """, unsafe_allow_html=True)

# --- LOAD MODEL ---
@st.cache_resource
def load_model():
    # Ensure this matches your filename
    with open('gold_model_live.pkl', 'rb') as f:
        return pickle.load(f)

try:
    model = load_model()
except Exception as e:
    st.error("⚠️ Model brain not found! Run the training script first.")
    st.stop()

# --- HEADER ---
st.markdown("<h1 class='main-title'>🥇 GOLD AI TERMINAL</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#FFD700; font-size:18px;'>Real-time Institutional Grade Forecasting</p>", unsafe_allow_html=True)
st.write("<br>", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("## ⚙️ Terminal Settings")
    st.image("https://images.cnbctv18.com/uploads/2024/08/shutterstock-2480509399-2024-08-368b960cfc07a7fc6986b47f60f0159d-scaled.jpg?impolicy=website&width=400&height=225", width=200)
    st.write("---")
    st.markdown("### 📡 API Connection")
    if st.button("SYNC LIVE DATA"):
        with st.spinner("Accessing COMEX..."):
            live_data = yf.download("GC=F", period="1d", interval="1m").tail(1)
            if not live_data.empty:
                st.session_state.update({
                    'close': float(live_data['Close'].iloc[0]),
                    'open': float(live_data['Open'].iloc[0]),
                    'high': float(live_data['High'].iloc[0]),
                    'low': float(live_data['Low'].iloc[0]),
                    'vol': float(live_data['Volume'].iloc[0])
                })
                st.toast("Sync Complete!", icon="✨")

# --- DATA INPUTS ---
with st.container():
    st.markdown("### 📈 Market Pulse")
    c1, c2, c3 = st.columns(3)
    with c1:
        c_val = st.number_input("Last Traded Price", value=st.session_state.get('close', 2000.00))
        o_val = st.number_input("Opening Tick", value=st.session_state.get('open', 1995.00))
    with c2:
        h_val = st.number_input("Session High", value=st.session_state.get('high', 2010.00))
        l_val = st.number_input("Session Low", value=st.session_state.get('low', 1985.00))
    with c3:
        v_val = st.number_input("24h Volume", value=st.session_state.get('vol', 120000.0))
        d_val = st.date_input("Forecast Window", datetime.now())

# --- EXECUTION ---
st.write("<br>", unsafe_allow_html=True)
if st.button("🚀 EXECUTE QUANT ANALYSIS"):
    y, m, d, dow = d_val.year, d_val.month, d_val.day, d_val.weekday()
    features = np.array([[c_val, v_val, o_val, h_val, l_val, y, m, d, dow]])
    
    prediction = model.predict(features)[0]
    net_change = prediction - c_val
    pct_change = (net_change / c_val) * 100
    
    st.markdown("---")
    st.markdown("### 🎯 Prediction Engine Output")
    
    res1, res2, res3 = st.columns(3)
    res1.metric("Predicted Target", f"${prediction:,.2f}")
    res2.metric("Projected Yield", f"${net_change:.2f}", delta=f"{pct_change:.2f}%")
    
    sentiment = "BULLISH 📈" if net_change > 0 else "BEARISH 📉"
    res3.metric("Trade Sentiment", sentiment)

    # Descriptive logic for "Charming" factor
    if net_change > 0:
        st.success(f"AI suggests a positive breakout of ${net_change:.2f} above current resistance levels.")
    else:
        st.warning(f"AI suggests a corrective pullback of ${abs(net_change):.2f} toward support levels.")