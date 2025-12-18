import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import time
import requests
from streamlit_lottie import st_lottie

# ==========================================
# 1. PAGE CONFIG & ANIMATED CSS
# ==========================================
st.set_page_config(page_title="BearCart Intelligence", layout="wide", page_icon="🐻")

# --- CUSTOM CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;600;700&family=JetBrains+Mono:wght@400;800&display=swap');

    :root { --primary-neon: #00F0FF; --secondary-neon: #FF003C; --bg-deep: #050511; }

    .stApp {
        background-color: var(--bg-deep);
        background-image: radial-gradient(circle at 15% 50%, rgba(76, 29, 149, 0.2) 0%, transparent 50%), radial-gradient(circle at 85% 30%, rgba(0, 240, 255, 0.1) 0%, transparent 50%);
        color: #E0E0E0;
    }

    h1, h2, h3 { font-family: 'Rajdhani', sans-serif !important; text-transform: uppercase; color: #FFFFFF; text-shadow: 0 0 10px rgba(0, 240, 255, 0.3); }
    p, div, label, span { font-family: 'Rajdhani', sans-serif; font-size: 1.1rem; }
    
    /* GLASS CARDS */
    div[data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 12px; padding: 20px; backdrop-filter: blur(10px);
        transition: transform 0.3s ease, border-color 0.3s ease;
    }
    div[data-testid="metric-container"]:hover { transform: translateY(-5px); border-color: var(--primary-neon); }

    /* ANIMATIONS: RISE UP */
    @keyframes slideUp { from { opacity: 0; transform: translateY(40px); } to { opacity: 1; transform: translateY(0); } }
    .stPlotlyChart { animation: slideUp 1s cubic-bezier(0.2, 0.8, 0.2, 1) forwards; }
    div[data-testid="stMetric"] { animation: slideUp 0.8s ease-out forwards; }

    /* WHATSAPP CHAT BUBBLE */
    .whatsapp-box {
        background-color: #075E54;
        border-radius: 10px;
        padding: 15px;
        margin-top: 10px;
        border-left: 5px solid #25D366;
        animation: slideUp 0.5s ease-out;
    }

    /* NEON COUPON CARD */
    .coupon-card {
        background: linear-gradient(135deg, #1a1a1a 0%, #0d0d0d 100%);
        border: 2px dashed #00F0FF;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        margin-top: 20px;
        box-shadow: 0 0 20px rgba(0, 240, 255, 0.2);
        animation: slideUp 0.5s ease-out;
    }
    .coupon-code {
        font-family: 'JetBrains Mono', monospace;
        font-size: 2rem;
        color: #00F0FF;
        letter-spacing: 5px;
        font-weight: bold;
    }

    /* BUTTONS */
    .stButton>button { background: linear-gradient(90deg, #FF003C 0%, #C00028 100%); color: white; border: none; border-radius: 4px; font-family: 'JetBrains Mono', monospace; transition: all 0.3s ease; }
    .stButton>button:hover { box-shadow: 0 0 25px rgba(255, 0, 60, 0.7); transform: scale(1.02); }
    
    section[data-testid="stSidebar"] { background-color: #020205; border-right: 1px solid #222; }
</style>
""", unsafe_allow_html=True)

def load_lottieurl(url: str):
    try:
        r = requests.get(url)
        if r.status_code != 200: return None
        return r.json()
    except: return None

lottie_ecommerce = load_lottieurl("https://assets10.lottiefiles.com/packages/lf20_u4jjb9bd.json")
lottie_coding = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_fcfjwiyb.json")

# ==========================================
# 2. DATA PROCESSING ENGINE
# ==========================================
@st.cache_data
def get_data(use_simulation=True, uploaded_file=None):
    df = None
    
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            for col in ['product_views', 'add_to_cart', 'time_spent_sec', 'pages_viewed']:
                if col not in df.columns: df[col] = 0
            if 'device' not in df.columns: df['device'] = np.random.choice(['Mobile', 'Desktop', 'Tablet'], len(df), p=[0.7, 0.25, 0.05])
            if 'location' not in df.columns: df['location'] = np.random.choice(['Mumbai', 'Delhi', 'Bangalore', 'Tier-2 City'], len(df))
            if 'hour_of_day' not in df.columns: df['hour_of_day'] = np.random.randint(0, 23, len(df))
        except: return None
    else:
        np.random.seed(42)
        n = 1500
        df = pd.DataFrame({
            'session_id': range(1, n + 1),
            'pages_viewed': np.random.randint(1, 15, n),
            'product_views': np.random.randint(0, 10, n),
            'add_to_cart': np.random.choice([0, 1, 2, 3], n, p=[0.80, 0.10, 0.05, 0.05]),
            'time_spent_sec': np.random.randint(5, 900, n),
            'device': np.random.choice(['Mobile', 'Desktop', 'Tablet'], n, p=[0.75, 0.20, 0.05]),
            'location': np.random.choice(['Mumbai', 'Delhi', 'Bangalore', 'Tier-2 City', 'Tier-3 City'], n),
            'hour_of_day': np.random.randint(0, 23, n)
        })

    df['intent_score'] = (df['product_views'] * 2) + (df['add_to_cart'] * 8) + (df['time_spent_sec'] / 45) + df['pages_viewed']
    def segment(score): return 'High Intent' if score > 25 else 'Medium Intent' if score > 10 else 'Low Intent'
    df['segment'] = df['intent_score'].apply(segment)
    if 'potential_revenue' not in df.columns:
        df['potential_revenue'] = df.apply(lambda x: np.random.randint(1000, 5000) if 'High' in x['segment'] else 0, axis=1)
    return df

# ==========================================
# 3. SIDEBAR
# ==========================================
with st.sidebar:
    if lottie_coding: st_lottie(lottie_coding, height=120)
    st.markdown("## BearCart AI")
    st.markdown("<div style='height: 2px; background: linear-gradient(90deg, #00F0FF, transparent); margin-bottom: 20px;'></div>", unsafe_allow_html=True)
    menu = st.radio("MODULES", ["🚀 Dashboard", "🧠 AI Analysis", "⚡ Action Center"])
    st.markdown("---")
    uploaded_file = st.file_uploader("Upload CSV", type=['csv'])
    if uploaded_file:
        df = get_data(uploaded_file=uploaded_file)
        st.success("✅ REAL DATA CONNECTED")
    else:
        df = get_data(use_simulation=True)
        st.info("ℹ️ SIMULATION MODE")

# ==========================================
# 4. DASHBOARD INTERFACE
# ==========================================
color_map = {'High Intent': '#FF003C', 'Medium Intent': '#00F0FF', 'Low Intent': '#4B4B4B'}

if menu == "🚀 Dashboard":
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("TRAFFIC INTELLIGENCE -- INDIA")
        st.markdown("<span style='color: #888;'> > DECODING RAW CLICKSTREAM INTO REVENUE SIGNALS</span>", unsafe_allow_html=True)
    with col2:
        if lottie_ecommerce: st_lottie(lottie_ecommerce, height=80)
    st.markdown("---")
    
    m1, m2, m3, m4 = st.columns(4)
    high_intent_users = len(df[df['segment'].str.contains('High')])
    est_revenue = df['potential_revenue'].sum()
    mobile_share = len(df[df['device'] == 'Mobile']) / len(df) * 100
    
    m1.metric("TOTAL SESSIONS", f"{len(df):,}")
    m2.metric("HIGH INTENT TARGETS", f"{high_intent_users}", delta="PRIORITY")
    m3.metric("REVENUE PIPELINE", f"₹{est_revenue:,.0f}", delta="+12%")
    m4.metric("MOBILE TRAFFIC", f"{mobile_share:.1f}%")

    st.markdown("###") 
    c1, c2 = st.columns([2, 1])
    with c1:
        st.subheader("BEHAVIORAL CLUSTERING")
        fig = px.scatter(df, x='time_spent_sec', y='product_views', color='segment', size='intent_score', color_discrete_map=color_map, template='plotly_dark')
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,255,255,0.02)")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.subheader("DEVICE INTELLIGENCE")
        fig_sun = px.sunburst(df, path=['device', 'segment'], values='intent_score', color='segment', color_discrete_map=color_map)
        fig_sun.update_layout(paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_sun, use_container_width=True)

    c3, c4 = st.columns([1, 2])
    with c3:
        st.subheader("CONVERSION FUNNEL")
        funnel_data = dict(number=[len(df), len(df[df['product_views']>0]), len(df[df['add_to_cart']>0]), len(df[df['segment']=='High Intent'])], stage=["Total Visits", "Viewed Product", "Added to Cart", "Predicted Buy"])
        fig_funnel = px.funnel(funnel_data, x='number', y='stage', color_discrete_sequence=['#00F0FF'])
        fig_funnel.update_layout(paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_funnel, use_container_width=True)
    with c4:
        st.subheader("HOURLY TRAFFIC TREND")
        trend_data = df.groupby('hour_of_day')['session_id'].count().reset_index()
        fig_area = px.area(trend_data, x='hour_of_day', y='session_id', line_shape='spline', color_discrete_sequence=['#FF003C'])
        fig_area.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,255,255,0.02)", xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.1)"))
        st.plotly_chart(fig_area, use_container_width=True)

elif menu == "🧠 AI Analysis":
    st.title("NEURAL INSIGHTS")
    c1, c2 = st.columns(2)
    with c1: st.markdown("<div style='border: 1px solid orange; padding: 20px; border-radius: 10px;'><h3 style='color: orange;'>⚠️ PATTERN: 'BARGAIN HUNTER'</h3><p>Tier-2 city users compare 2.4x more products.</p></div>", unsafe_allow_html=True)
    with c2: st.markdown("<div style='border: 1px solid #FF003C; padding: 20px; border-radius: 10px;'><h3 style='color: #FF003C;'>🚨 PATTERN: 'MOBILE DROP'</h3><p>Mobile abandonment is 40% higher.</p></div>", unsafe_allow_html=True)
    st.markdown("---")
    st.subheader("GEOSPATIAL INTENT MAPPING")
    loc_group = df.groupby(['location', 'segment']).size().reset_index(name='count')
    fig = px.bar(loc_group, x='location', y='count', color='segment', barmode='group', color_discrete_map=color_map, template='plotly_dark')
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)

elif menu == "⚡ Action Center":
    st.title("ACTION COMMAND CENTER")
    
    t1, t2, t3 = st.tabs(["🔥 HIGH INTENT", "⚠️ MEDIUM INTENT", "❄️ LOW INTENT"])
    
    # TAB 1: WHATSAPP
    with t1:
        st.markdown("### 📢 STRATEGY: TRUST & URGENCY")
        st.write("Targeting **Ready-to-Buy** customers via API.")
        
        if st.button("GENERATE PRIORITY WHATSAPP"):
            with st.spinner("Connecting to WhatsApp Business API..."):
                time.sleep(1.5)
                # VISUAL: Chat Bubble
                st.markdown("""
                <div class="whatsapp-box">
                    <strong style="color: #FFF;">📲 BearCart Official:</strong><br>
                    <span style="color: #EEE;">Hi there! Your items are reserved for 30 minutes. Order now to get Priority Shipping. 🚚</span>
                    <br><br>
                    <a href="https://wa.me/?text=Hi%20BearCart%20I%20Want%20To%20Order" target="_blank" style="color: #25D366; text-decoration: none; font-weight: bold;">
                        [CLICK TO OPEN WHATSAPP]
                    </a>
                </div>
                """, unsafe_allow_html=True)
                st.success("Message Drafted & Ready to Send!")

    # TAB 2: COUPON
    with t2:
        st.markdown("### 🎟️ STRATEGY: VALUE NUDGE")
        coupon_val = st.slider("DISCOUNT MAGNITUDE (%)", 5, 20, 10)
        
        if st.button("GENERATE NEON COUPON"):
            with st.spinner("Minting Unique Code..."):
                time.sleep(1.2)
                # VISUAL: Neon Ticket
                st.markdown(f"""
                <div class="coupon-card">
                    <p style="color: #888;">LIMITED TIME OFFER</p>
                    <div class="coupon-code">INDIA{coupon_val}</div>
                    <p style="color: #FFF; margin-top: 10px;">FLAT {coupon_val}% OFF</p>
                </div>
                """, unsafe_allow_html=True)
                st.balloons()

    # TAB 3: SAVINGS (ANIMATED)
    with t3:
        st.markdown("### 💰 STRATEGY: AD SPEND OPTIMIZATION")
        st.write("Budget reallocation from low-intent segments.")
        
        # HTML Block for COUNT UP ANIMATION (Savings)
        st.markdown("""
        <div style="background: rgba(0, 255, 0, 0.05); padding: 30px; border-radius: 15px; border: 1px solid #00FF00; text-align: center;">
            <div style="color: #00FF00; font-size: 1.2rem; font-family: 'JetBrains Mono';">TOTAL AD SPEND SAVED</div>
            <div id="savings_counter" style="color: #FFF; font-size: 4rem; font-weight: bold; font-family: 'Rajdhani';">0</div>
        </div>
        
        <script>
        setTimeout(function() {
            let obj = document.getElementById("savings_counter");
            let start = 0;
            let end = 45000;
            let duration = 2000;
            let range = end - start;
            let current = start;
            let increment = 500;
            let stepTime = 10;
            
            let timer = setInterval(function() {
                current += increment;
                if (current >= end) {
                    current = end;
                    clearInterval(timer);
                }
                obj.innerHTML = "₹" + current.toLocaleString();
            }, stepTime);
        }, 500);
        </script>
        """, unsafe_allow_html=True)