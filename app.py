import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# --- PAGE CONFIGURATION & CSS ---
st.set_page_config(layout="wide", page_title="Portfolio Stress Test", page_icon="⚡")

# Custom CSS to force high contrast and professional styling
st.markdown("""
    <style>
    /* Force dark text for readability */
    p, h1, h2, h3, h4, .stMarkdown, .stRadio label {
        color: #333333 !important;
    }
    /* Metric styling */
    div[data-testid="stMetricValue"] {
        font-weight: bold;
        color: #1f1f1f;
    }
    /* Success/Error message styling */
    .stAlert {
        font-weight: 500;
    }
    </style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.title("⚡ Portfolio Stress-Test Engine")
st.markdown("**Live Scenario Analysis: Shekhar (Solvency) & Sunita (Longevity)**")
st.divider()

# --- TABS FOR PERSONAS ---
tab_sunita, tab_shekhar = st.tabs(["👵 Sunita: Longevity Risk", "👤 Shekhar: Solvency Shield"])

# ==========================================
# TAB 1: SUNITA (LONGEVITY SIMULATION)
# ==========================================
with tab_sunita:
    st.subheader("Sunita: Will the money last?")
    
    col_input, col_viz = st.columns([1, 2])
    
    with col_input:
        with st.container(border=True):
            st.markdown("### 🎛️ Stress Variables")
            
            # INPUTS
            inflation = st.slider("📉 Inflation Rate (%)", 4.0, 10.0, 6.0, 0.5)
            rent_strategy = st.radio("🏠 Living Strategy", 
                                   ["Paying Rent (₹10k/mo)", "Move to Family Home (₹0)"])
            medical_shock = st.selectbox("🏥 Medical Shock (Year 5)", [0, 300000, 500000])

    with col_viz:
        # LOGIC ENGINE: SUNITA
        corpus = 2500000
        pension = 300000 # 25k * 12
        base_living_expense = 480000 # 40k * 12
        rent_expense = 120000 if rent_strategy == "Paying Rent (₹10k/mo)" else 0
        total_expense_y1 = base_living_expense + rent_expense
        
        simulation_data = []
        current_corpus = corpus
        depletion_age = "95+"
        status_color = "green"
        
        # Simulate 30 Years
        for year in range(1, 31):
            age = 65 + year
            # Inflate expenses
            annual_expense = total_expense_y1 * ((1 + inflation/100)**(year-1))
            if year == 5: annual_expense += medical_shock
            
            # Income (Pension + 7.8% blended yield on remaining corpus)
            portfolio_income = max(0, current_corpus * 0.078)
            total_inflow = pension + portfolio_income
            
            # Drawdown
            drawdown = max(0, annual_expense - total_inflow)
            current_corpus -= drawdown
            
            if current_corpus <= 0:
                current_corpus = 0
                if depletion_age == "95+":
                    depletion_age = age
                    status_color = "red"
            
            simulation_data.append({"Age": age, "Corpus": current_corpus})

        df_sunita = pd.DataFrame(simulation_data)

        # OUTPUT METRICS (In a visible container)
        with st.container(border=True):
            m1, m2, m3 = st.columns(3)
            m1.metric("Monthly Gap", f"₹{(total_expense_y1 - pension)/12:,.0f}", delta="Deficit", delta_color="inverse")
            m2.metric("Projected Depletion Age", f"{depletion_age} Years", 
                      delta="Critical" if status_color=="red" and depletion_age < 80 else "Safe",
                      delta_color="inverse" if status_color=="red" else "normal")
            m3.metric("Inflation Impact", f"{inflation}%")

        # DYNAMIC CHART
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_sunita["Age"], y=df_sunita["Corpus"], fill='tozeroy', 
                               mode='lines', line=dict(color='#ef4444' if status_color=="red" else '#10b981', width=3)))
        fig.update_layout(title="Wealth Decay Curve", xaxis_title="Age", yaxis_title="Remaining Corpus (₹)", 
                          height=300, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig, use_container_width=True)

# ==========================================
# TAB 2: SHEKHAR (SOLVENCY SIMULATION)
# ==========================================
with tab_shekhar:
    st.subheader("Shekhar: Business Solvency Check")
    
    col_s_input, col_s_viz = st.columns([1, 2])
    
    with col_s_input:
        with st.container(border=True):
            st.markdown("### 🎛️ Market Scenarios")
            
            # INPUTS
            market_crash = st.slider("📉 Equity Market Drop (%)", 0, 50, 10, 5)
            house_inflation = st.slider("🏠 House Price Surge (%)", 0, 20, 5)
            
            st.info("💡 **Goal:** Keep Solvency Ratio > 2.0x to protect business loans.")

    with col_s_viz:
        # LOGIC ENGINE: SHEKHAR
        initial_corpus = 40000000 # 4 Cr
        # Asset Allocation
        equity_val = 16000000 * (1 - market_crash/100) # 40%
        arbitrage_val = 10000000 # 25% (Stable)
        bond_val = 10000000 # 25% (Stable)
        gold_val = 4000000 * (1.10 if market_crash > 15 else 1.0) # 10% (Gold hedges crash)
        
        total_liquid_assets = equity_val + arbitrage_val + bond_val + gold_val
        annual_debt_obligation = 16600000 # 1.66 Cr Business Debt EMI
        
        # Key Metric: Solvency Ratio
        solvency_ratio = total_liquid_assets / annual_debt_obligation
        
        # Goal Check (Year 4)
        house_cost = 30000000 * ((1.05 + house_inflation/100)**4)
        # Simple projection: Assets grow at ~9% for 4 years
        projected_wealth = total_liquid_assets * (1.09**4) 
        surplus = projected_wealth - house_cost

        # OUTPUT METRICS
        with st.container(border=True):
            k1, k2, k3 = st.columns(3)
            k1.metric("Market Impact", f"-{market_crash}%")
            
            # Solvency Badge logic
            delta_msg = "SAFE (>2.0x)" if solvency_ratio >= 2.0 else "RISK (<2.0x)"
            k2.metric("Solvency Ratio", f"{solvency_ratio:.2f}x", delta=delta_msg, 
                      delta_color="normal" if solvency_ratio >= 2.0 else "inverse")
            
            k3.metric("Goal Status", f"₹{surplus/100000:.1f} L Surplus" if surplus > 0 else f"₹{abs(surplus)/100000:.1f} L Shortfall",
                      delta="Funded" if surplus > 0 else "Gap",
                      delta_color="normal" if surplus > 0 else "inverse")

        # SOLVENCY GAUGE CHART
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = solvency_ratio,
            title = {'text': "Solvency Shield Strength"},
            gauge = {
                'axis': {'range': [0, 4]},
                'bar': {'color': "#10b981" if solvency_ratio >= 2.0 else "#ef4444"},
                'steps': [
                    {'range': [0, 2], 'color': "#fef2f2"},
                    {'range': [2, 4], 'color': "#ecfdf5"}],
                'threshold': {
                    'line': {'color': "black", 'width': 4},
                    'thickness': 0.75,
                    'value': 2.0}
            }
        ))
        fig_gauge.update_layout(height=250, margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_gauge, use_container_width=True)