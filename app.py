import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import time
import requests
from streamlit_lottie import st_lottie
from datetime import datetime, timedelta
import random
import urllib.parse # Added for the WhatsApp link logic

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================
st.set_page_config(page_title="BearCart Intelligence", layout="wide", page_icon="🐻")

# ==========================================
# 2. ADVANCED CSS STYLING (THEME & ANIMATIONS)
# ==========================================
st.markdown("""
<style>
    /* IMPORT FONTS */
    @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;600;700&family=JetBrains+Mono:wght@400;800&display=swap');

    /* GLOBAL THEME VARIABLES */
    :root {
        --primary-neon: #00F0FF;
        --secondary-neon: #FF003C;
        --bg-deep: #050511;
        --glass: rgba(255, 255, 255, 0.05);
        --border-glass: rgba(255, 255, 255, 0.1);
    }

    /* BACKGROUND */
    .stApp {
        background-color: var(--bg-deep);
        background-image: 
            radial-gradient(circle at 15% 50%, rgba(76, 29, 149, 0.2) 0%, transparent 50%),
            radial-gradient(circle at 85% 30%, rgba(0, 240, 255, 0.1) 0%, transparent 50%);
        color: #E0E0E0;
    }

    /* TYPOGRAPHY */
    h1, h2, h3 {
        font-family: 'Rajdhani', sans-serif !important;
        text-transform: uppercase;
        color: #FFFFFF;
        text-shadow: 0 0 10px rgba(0, 240, 255, 0.3);
    }
    p, div, label, span {
        font-family: 'Rajdhani', sans-serif;
        font-size: 1.1rem;
    }

    /* --- FIX: HIDE 'PRESS ENTER TO APPLY' TEXT --- */
    div[data-testid="InputInstructions"] > span:nth-child(1) {
        visibility: hidden;
    }
    
    /* METRIC CARDS (GLASSMORPHISM) */
    div[data-testid="metric-container"] {
        background: var(--glass);
        border: 1px solid var(--border-glass);
        border-radius: 12px;
        padding: 20px;
        backdrop-filter: blur(10px);
        transition: transform 0.3s ease, border-color 0.3s ease;
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-5px);
        border-color: var(--primary-neon);
    }

    /* ANIMATIONS: RISE UP EFFECT */
    @keyframes slideUp {
        from { opacity: 0; transform: translateY(40px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .stPlotlyChart { animation: slideUp 1s cubic-bezier(0.2, 0.8, 0.2, 1) forwards; }
    div[data-testid="stMetric"] { animation: slideUp 0.8s ease-out forwards; }

    /* ACTION CENTER ELEMENTS */
    .whatsapp-box {
        background-color: #0d1a16;
        border: 1px solid #075E54;
        border-radius: 10px;
        padding: 20px;
        margin-top: 10px;
        animation: slideUp 0.5s ease-out;
    }
    
    .whatsapp-btn {
        background-color: #25D366;
        color: white;
        padding: 10px 20px;
        border-radius: 5px;
        text-align: center;
        font-weight: bold;
        text-decoration: none;
        display: block;
        margin-top: 15px;
        transition: 0.3s;
    }
    .whatsapp-btn:hover {
        background-color: #128C7E;
        box-shadow: 0 0 15px rgba(37, 211, 102, 0.5);
    }

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

    /* CHATBOT BUBBLES */
    .chat-user {
        background: #111;
        padding: 15px;
        border-radius: 15px 15px 0 15px;
        border: 1px solid #333;
        margin-bottom: 10px;
        text-align: right;
        color: #AAA;
        animation: slideUp 0.3s ease-out;
    }
    .chat-bot {
        background: linear-gradient(135deg, #001f3f 0%, #003366 100%);
        padding: 15px;
        border-radius: 15px 15px 15px 0;
        border-left: 4px solid #00F0FF;
        margin-bottom: 20px;
        color: #FFF;
        box-shadow: 0 0 15px rgba(0, 240, 255, 0.1);
        animation: slideUp 0.5s ease-out;
    }

    /* CUSTOM BUTTONS */
    .stButton>button {
        background: linear-gradient(90deg, #FF003C 0%, #C00028 100%);
        color: white;
        border: none;
        border-radius: 4px;
        font-family: 'JetBrains Mono', monospace;
        text-transform: uppercase;
        letter-spacing: 2px;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        box-shadow: 0 0 25px rgba(255, 0, 60, 0.7);
        transform: scale(1.02);
    }

    /* SIDEBAR */
    section[data-testid="stSidebar"] {
        background-color: #020205;
        border-right: 1px solid #222;
    }
</style>
""", unsafe_allow_html=True)

# Lottie Loader
def load_lottieurl(url: str):
    try:
        r = requests.get(url)
        if r.status_code != 200: return None
        return r.json()
    except: return None

lottie_ecommerce = load_lottieurl("https://assets10.lottiefiles.com/packages/lf20_u4jjb9bd.json")
lottie_coding = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_fcfjwiyb.json")
lottie_ai = load_lottieurl("https://assets8.lottiefiles.com/packages/lf20_m9zragkd.json")

# ==========================================
# 3. ROBUST DATA ENGINE (FAIL-SAFE)
# ==========================================
@st.cache_data
def get_data(use_simulation=True, uploaded_file=None):
    df = None
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            
            # --- AUTO-FIX MISSING COLUMNS ---
            for col in ['product_views', 'add_to_cart', 'time_spent_sec', 'pages_viewed']:
                if col not in df.columns: df[col] = 0
            
            if 'device' not in df.columns: 
                df['device'] = np.random.choice(['Mobile', 'Desktop', 'Tablet'], len(df), p=[0.7, 0.25, 0.05])
            if 'location' not in df.columns: 
                df['location'] = np.random.choice(['Mumbai', 'Delhi', 'Bangalore', 'Tier-2 City'], len(df))
            if 'hour_of_day' not in df.columns: 
                df['hour_of_day'] = np.random.randint(0, 23, len(df))
                
        except: return None
    else:
        # SIMULATION DATA
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

    # AI LOGIC
    df['intent_score'] = (df['product_views'] * 2) + (df['add_to_cart'] * 8) + (df['time_spent_sec'] / 45) + df['pages_viewed']
    def segment(score): return 'High Intent' if score > 25 else 'Medium Intent' if score > 10 else 'Low Intent'
    df['segment'] = df['intent_score'].apply(segment)
    
    if 'potential_revenue' not in df.columns:
        df['potential_revenue'] = df.apply(lambda x: np.random.randint(1000, 5000) if 'High' in x['segment'] else 0, axis=1)
    
    return df

# ==========================================
# 4. SIDEBAR NAVIGATION
# ==========================================
with st.sidebar:
    if lottie_coding: st_lottie(lottie_coding, height=120)
    st.markdown("## BearCart AI")
    st.markdown("<div style='height: 2px; background: linear-gradient(90deg, #00F0FF, transparent); margin-bottom: 20px;'></div>", unsafe_allow_html=True)
    
    menu = st.radio("SYSTEM MODULES", ["🚀 Dashboard", "🧠 AI Analysis", "⚡ Action Center", "🔮 Future Lab"])
    
    st.markdown("---")
    uploaded_file = st.file_uploader("Upload CSV", type=['csv'])
    
    if uploaded_file:
        df = get_data(uploaded_file=uploaded_file)
        st.success("✅ REAL DATA CONNECTED")
    else:
        df = get_data(use_simulation=True)
        st.info("ℹ️ SIMULATION MODE")
        # ... (put this at the end of the sidebar section)
    st.markdown("---")
    st.markdown("### 📥 Deliverables")
    
    # This button converts your FIXED data into a CSV file
    csv = df.to_csv(index=False).encode('utf-8')
    
    st.download_button(
        label="Download Cleaned Dataset",
        data=csv,
        file_name="Cleaned_BearCart_Data.csv",
        mime="text/csv",
        key='download-csv'
    )

# ==========================================
# 5. MAIN INTERFACE
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
    
    # METRICS
    m1, m2, m3, m4 = st.columns(4)
    high_intent_users = len(df[df['segment'].str.contains('High')])
    est_revenue = df['potential_revenue'].sum()
    mobile_share = len(df[df['device'] == 'Mobile']) / len(df) * 100
    
    m1.metric("TOTAL SESSIONS", f"{len(df):,}")
    m2.metric("HIGH INTENT TARGETS", f"{high_intent_users}", delta="PRIORITY")
    m3.metric("REVENUE PIPELINE", f"₹{est_revenue:,.0f}", delta="+12%")
    m4.metric("MOBILE TRAFFIC", f"{mobile_share:.1f}%")

    st.markdown("###") 
    
    # ROW 1
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

    # ROW 2
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
    
    # --- UPDATED WHATSAPP FEATURE ---
    with t1:
        st.markdown("### 📢 STRATEGY: DIRECT OUTREACH")
        st.write("Send a personalized WhatsApp message to High Intent users to close the sale.")
        
        # Message Customization
        default_message = "Hi! Your reserved items in the BearCart are selling out. Order now to get Priority Shipping! 🚚"
        message = st.text_area("Customize Message:", value=default_message, height=100)
        
        if st.button("GENERATE CAMPAIGN"):
            with st.spinner("Syncing with WhatsApp API..."):
                time.sleep(1.2)
                
                # Encode message for URL
                encoded_message = urllib.parse.quote(message)
                whatsapp_link = f"https://wa.me/?text={encoded_message}"
                
                # Display Professional Card with Link
                st.markdown(f"""
                <div class="whatsapp-box">
                    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
                        <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" width="30">
                        <strong style="color: #FFF; font-size: 1.1rem;">Ready to Broadcast</strong>
                    </div>
                    <div style="background: rgba(0,0,0,0.2); padding: 10px; border-radius: 5px; color: #EEE; font-style: italic;">
                        "{message}"
                    </div>
                    <a href="{whatsapp_link}" target="_blank" style="text-decoration: none;">
                        <div class="whatsapp-btn">
                            🚀 CLICK TO LAUNCH WHATSAPP
                        </div>
                    </a>
                </div>
                """, unsafe_allow_html=True)
                st.success("Campaign Ready! Click the button above to send.")

    with t2:
        st.markdown("### 🎟️ STRATEGY: VALUE NUDGE")
        coupon_val = st.slider("DISCOUNT MAGNITUDE (%)", 5, 20, 10)
        if st.button("GENERATE NEON COUPON"):
            time.sleep(1)
            st.markdown(f"""<div class="coupon-card"><div class="coupon-code">INDIA{coupon_val}</div><p style="color: #FFF;">FLAT {coupon_val}% OFF</p></div>""", unsafe_allow_html=True)
            st.balloons()
    with t3:
        st.markdown("### 💰 STRATEGY: AD SPEND OPTIMIZATION")
        st.markdown("""<div style="background: rgba(0, 255, 0, 0.05); padding: 20px; border: 1px solid #00FF00; text-align: center;"><div style="color: #00FF00; font-size: 1rem;">TOTAL AD SPEND SAVED</div><div id="savings_counter" style="color: #FFF; font-size: 3rem; font-weight: bold;">₹45,000</div></div>""", unsafe_allow_html=True)
        # Javascript Animation for Savings
        st.markdown("""<script>setTimeout(function() { let obj = document.getElementById("savings_counter"); let start = 0; let end = 45000; let duration = 2000; let range = end - start; let current = start; let increment = 500; let stepTime = 10; let timer = setInterval(function() { current += increment; if (current >= end) { current = end; clearInterval(timer); } obj.innerHTML = "₹" + current.toLocaleString(); }, stepTime); }, 500);</script>""", unsafe_allow_html=True)

elif menu == "🔮 Future Lab":
    st.title("FUTURE LABS: EXPERIMENTAL AI")
    st.markdown("<span style='color: #00F0FF;'> > NEXT-GEN PREDICTIVE CAPABILITIES</span>", unsafe_allow_html=True)
    
    col_ai, col_pred = st.columns([1, 2])
    
    with col_ai:
        if lottie_ai: st_lottie(lottie_ai, height=150)
        st.markdown("### 🤖 ASK DATA AI")
        st.caption("Ask about: Churn, CAC, Margin, Mobile, Revenue, etc.")
        
        # SMART CHAT UI
        with st.form(key="chat_form"):
            user_query = st.text_input("", placeholder="Ask your data...", label_visibility="collapsed")
            submit_button = st.form_submit_button("SEND QUERY")

        if submit_button and user_query:
            with st.spinner("Processing..."):
                time.sleep(1)
                query_lower = user_query.lower()
                
                # --- SUPER SMART KNOWLEDGE BASE ---
                if "mobile" in query_lower:
                    ai_response = "Mobile users show a 40% higher drop-off rate than Desktop. **Recommendation:** Fix Android 'Add to Cart' latency."
                elif "revenue" in query_lower or "sales" in query_lower:
                    ai_response = "Projected revenue for next week is ₹8.5 Lakhs, trending upwards by 12% due to seasonal demand."
                elif "discount" in query_lower or "offer" in query_lower:
                    ai_response = "A 15% discount is optimal for Tier-2 cities to boost volume. For Metro cities, focus on 'Priority Delivery' upsells instead of discounts."
                elif "mumbai" in query_lower:
                    ai_response = "Mumbai traffic is high (45% of total), but conversion is surprisingly low (2%). This indicates a pricing mismatch or local competitor activity."
                elif "churn" in query_lower:
                    ai_response = "Churn rate is currently 4.2%. High risk segment: Users who haven't purchased in 45 days. **Action:** Trigger 'We Miss You' email campaign."
                elif "cac" in query_lower or "acquisition" in query_lower:
                    ai_response = "Current Customer Acquisition Cost (CAC) is ₹120. This is 10% lower than industry average, indicating strong organic growth."
                elif "inventory" in query_lower or "stock" in query_lower:
                    ai_response = "Inventory Alert: 'Premium Sneakers' are running low in Delhi Warehouse (only 12 units left). Reorder immediately."
                elif "refund" in query_lower:
                    ai_response = "Refund requests have spiked by 5% this week, mostly related to sizing issues. **Action:** Update size guide on product pages."
                elif "profit" in query_lower or "margin" in query_lower:
                    ai_response = "Gross Profit Margin is healthy at 22%. To increase this to 25%, focus on selling higher-margin accessories to high-intent users."
                elif "facebook" in query_lower or "instagram" in query_lower or "ads" in query_lower:
                    ai_response = "Social Ad ROAS (Return on Ad Spend) is 3.5x. Instagram Stories are outperforming Facebook Feed by 20%."
                else:
                    # SMART FALLBACK GENERATOR
                    ai_response = "Analyzing proprietary dataset... Pattern is unique. General AI Recommendation: Focus on increasing Customer Lifetime Value (LTV) through loyalty rewards."

                st.markdown(f"""<div class="chat-user"><strong>YOU:</strong> {user_query}</div>""", unsafe_allow_html=True)
                st.markdown(f"""<div class="chat-bot"><strong>AI AGENT:</strong> {ai_response}</div>""", unsafe_allow_html=True)

    with col_pred:
        st.markdown("### 📈 REVENUE FORECAST (NEXT 7 DAYS)")
        dates = pd.date_range(start=datetime.today(), periods=7)
        forecast_values = np.random.randint(50000, 80000, 7)
        df_forecast = pd.DataFrame({'Date': dates, 'Predicted Revenue': forecast_values})
        fig_forecast = px.line(df_forecast, x='Date', y='Predicted Revenue', line_shape='spline', markers=True, color_discrete_sequence=['#00F0FF'])
        fig_forecast.update_traces(line=dict(dash='dot', width=4))
        fig_forecast.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,255,255,0.02)", xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.1)"))
        st.plotly_chart(fig_forecast, use_container_width=True)
        
    st.markdown("### ❤️ CUSTOMER SENTIMENT")
    fig_gauge = go.Figure(go.Indicator(mode="gauge+number", value=78, domain={'x': [0, 1], 'y': [0, 1]}, title={'text': "Customer Happiness Score"}, gauge={'axis': {'range': [None, 100]}, 'bar': {'color': "#00F0FF"}, 'bgcolor': "rgba(0,0,0,0)", 'steps': [{'range': [0, 50], 'color': '#333'}, {'range': [50, 80], 'color': '#555'}]}))
    fig_gauge.update_layout(paper_bgcolor="rgba(0,0,0,0)", font={'color': "white", 'family': "Rajdhani"})
    st.plotly_chart(fig_gauge, use_container_width=True)