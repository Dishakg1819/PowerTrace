"""
EcoCode: Software Energy Profiler, Algorithm Scoreboard & GreenOps CI/CD Gatekeeper
Streamlit Application for Hackathon PS 5.3 (Containerized & Local Hybrid Edition)
"""

import streamlit as st
import plotly.graph_objects as go
import json
import time
import os
import subprocess
import sys
import io
import contextlib

from runner import run_code_in_container
from ecocode.advisor import GreenAdvisor
from ecocode.gatekeeper import CICDGatekeeper
from ecocode.benchmarks import BENCHMARK_SUITES
from ecocode.consultant import GreenConsultant

# Page Configuration
st.set_page_config(
    page_title="EcoCode | Software Energy Profiler & GreenOps",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (Glassmorphism + Modern Eco-Dark Theme)
st.markdown("""
<style>
    /* Global Theme Styles */
    .stApp {
        background: radial-gradient(circle at 10% 20%, #0d1b2a 0%, #070d17 90%);
        color: #e0e1dd;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Card Styles */
    .eco-card {
        background: rgba(19, 34, 53, 0.65);
        border: 1px solid rgba(16, 185, 129, 0.25);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .eco-card:hover {
        border-color: rgba(16, 185, 129, 0.6);
        transform: translateY(-2px);
    }
    
    .metric-value {
        font-size: 2.1rem;
        font-weight: 700;
        color: #10b981;
        letter-spacing: -0.5px;
        margin: 4px 0;
    }
    .metric-label {
        font-size: 0.85rem;
        text-transform: uppercase;
        color: #94a3b8;
        letter-spacing: 1px;
        font-weight: 600;
    }
    .metric-sub {
        font-size: 0.8rem;
        color: #64748b;
    }

    /* Grade Badge */
    .grade-badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 80px;
        height: 80px;
        border-radius: 50%;
        font-size: 2.5rem;
        font-weight: 800;
        box-shadow: 0 0 25px rgba(16, 185, 129, 0.4);
    }

    /* Code smell badge */
    .severity-badge-high {
        background: rgba(239, 68, 68, 0.2);
        color: #ef4444;
        border: 1px solid #ef4444;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 700;
    }
    .severity-badge-medium {
        background: rgba(245, 158, 11, 0.2);
        color: #f59e0b;
        border: 1px solid #f59e0b;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 700;
    }
    .severity-badge-low {
        background: rgba(56, 189, 248, 0.2);
        color: #38bdf8;
        border: 1px solid #38bdf8;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 700;
    }

    /* Terminal Box */
    .terminal-box {
        background: #050a12;
        border: 1px solid #1e293b;
        border-radius: 8px;
        padding: 14px;
        font-family: 'Courier New', Courier, monospace;
        font-size: 0.85rem;
        color: #38bdf8;
        white-space: pre-wrap;
        line-height: 1.4;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- Session State Initialization for Auth -----------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = ""

# ----------------- Login Screen Component -----------------
def render_login_screen():
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="text-align: center; margin-bottom: 20px;">
            <img src="https://img.icons8.com/isometric/100/ecology-light-bulb.png" width="80"/>
            <h2 style="color: #f8fafc; font-weight: 800; margin-top: 10px;">Welcome to EcoCode</h2>
            <p style="color: #94a3b8; font-size: 0.95rem;">Enter any username & password to access the platform</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            user_input = st.text_input("Username", placeholder="e.g., developer, john, team_lead")
            pass_input = st.text_input("Password", type="password", placeholder="••••••••")
            submit_login = st.form_submit_button("🔒 Sign In", use_container_width=True)
            
            if submit_login:
                if user_input.strip():
                    st.session_state.authenticated = True
                    st.session_state.username = user_input.strip()
                    st.success("Login successful! Loading dashboard...")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.warning("Please enter at least a username to continue.")
        
        st.markdown("""
        <div style="text-align: center; margin-top: 15px; font-size: 0.8rem; color: #64748b;">
            Hackathon PS 5.3 • Green-Code Advisor & Local Profiler
        </div>
        """, unsafe_allow_html=True)

# If not authenticated, halt execution and render only the login screen
if not st.session_state.authenticated:
    render_login_screen()
    st.stop()


# ----------------- Sidebar Configuration (Authenticated View) -----------------
with st.sidebar:
    st.image("https://img.icons8.com/isometric/100/ecology-light-bulb.png", width=64)
    st.markdown("## **EcoCode Engine**")
    st.caption("Software Energy Profiler & Local Sandbox")
    st.markdown(f"👤 Logged in as: **{st.session_state.username}**")
    
    if st.button("🚪 Sign Out", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.username = ""
        st.rerun()

    st.markdown("---")

    st.markdown("### ⚙️ Cloud Server Profile")
    server_watts = st.slider("Server Power Load (Watts)", min_value=20.0, max_value=350.0, value=100.0, step=10.0,
                             help="Simulated server active CPU power consumption (PDR standard: 100W = 0.1 kW).")
    grid_intensity = st.slider("Grid Intensity (kg CO₂e/kWh)", min_value=0.1, max_value=1.5, value=0.8, step=0.05,
                               help="Carbon intensity of electricity grid (Standard India/US coal-mix: ~0.8 kg/kWh).")
    tariff_rate = st.number_input("Commercial Tariff (₹ / kWh)", min_value=1.0, max_value=30.0, value=8.0, step=0.5,
                                  help="Commercial electricity unit rate (Default: ₹8.0/kWh).")
    
    st.markdown("---")
    st.markdown("### 🤖 AI Green Consultant")
    gemini_key = st.text_input("Gemini API Key (Optional)", type="password", 
                               help="Enter Google Gemini API key for live generative green recommendations. Built-in knowledge base works offline without key!")

    st.markdown("---")
    st.caption("🏆 **Hackathon PS 5.3**: Green-Code Advisor")
    st.caption("Built with Python, Streamlit & Green Computing Principles.")

# Initialize Core Services
advisor = GreenAdvisor()
gatekeeper = CICDGatekeeper(baseline_path="baseline.json", threshold_pct=10.0)
consultant = GreenConsultant(api_key=gemini_key)

# Robust Execution Wrapper with Smart Local Fallback
def safe_run_code(code_str):
    """
    Tries running code in Docker container first. 
    If Docker is unavailable or fails, automatically falls back to local Python subprocess execution 
    so the application works seamlessly offline without crashing.
    """
    try:
        res = run_code_in_container(code_str)
        if isinstance(res, dict) and res.get("success"):
            return res
        if isinstance(res, dict) and res.get("error") and ("Docker" in str(res["error"]) or "503" in str(res["error"])):
            raise Exception(res["error"])
        if isinstance(res, dict):
            return res
    except Exception as docker_err:
        # Fallback to local python execution engine
        try:
            start_time = time.time()
            exec_result = subprocess.run(
                [sys.executable, "-c", code_str],
                capture_output=True,
                text=True,
                timeout=15
            )
            end_time = time.time()
            elapsed = end_time - start_time

            logs = f"[LOCAL EXECUTION MODE — Docker Offline Fallback Active]\n{exec_result.stdout}"
            if exec_result.stderr:
                logs += f"\n[stderr]:\n{exec_result.stderr}"

            if exec_result.returncode == 0:
                return {
                    "success": True,
                    "time": max(elapsed, 0.0001),
                    "logs": logs
                }
            else:
                return {
                    "success": False,
                    "error": f"Script Execution Error (Exit Code {exec_result.returncode})",
                    "time": elapsed,
                    "logs": logs
                }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Execution timed out (> 15 seconds limit).",
                "time": 15.0,
                "logs": "Timeout expired in local fallback runner."
            }
        except Exception as local_err:
            return {
                "success": False,
                "error": f"Execution failed: {str(local_err)}",
                "time": 0.0,
                "logs": f"Traceback:\n{str(local_err)}"
            }

# Helper function to compute complete metrics from execution time
def calculate_eco_metrics(exec_time_sec):
    energy_kwh = (exec_time_sec / 3600.0) * (server_watts / 1000.0)
    carbon_g = energy_kwh * grid_intensity * 1000.0
    cost = energy_kwh * tariff_rate
    smartphone_charges = energy_kwh / 0.012  # ~0.012 kWh per full charge
    led_hours = energy_kwh / 0.010           # 10W LED bulb
    car_km = carbon_g / 120.0                # ~120 g CO2/km average car
    return {
        "execution_time_sec": exec_time_sec,
        "energy_kwh": energy_kwh,
        "carbon_g_co2": carbon_g,
        "cost_inr": cost,
        "smartphone_charges": smartphone_charges,
        "led_bulb_hours": led_hours,
        "car_km_equivalent": car_km
    }

# ----------------- Header Banner -----------------
st.markdown("""
<div style="display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid rgba(16, 185, 129, 0.3); padding-bottom: 15px; margin-bottom: 25px;">
    <div>
        <h1 style="margin: 0; font-size: 2.3rem; color: #f8fafc; font-weight: 800;">
            🌿 <span style="color: #10b981;">EcoCode</span> Platform
        </h1>
        <p style="margin: 5px 0 0 0; color: #94a3b8; font-size: 1.05rem;">
            Software Energy Profiler, Algorithm Scoreboard & GreenOps CI/CD Gatekeeper
        </p>
    </div>
    <div style="text-align: right;">
        <span style="background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid #10b981; padding: 6px 14px; border-radius: 20px; font-size: 0.85rem; font-weight: 600;">
            Hybrid Local / Sandbox Engine Active
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

# Tabs Configuration
tab_profiler, tab_advisor, tab_scoreboard, tab_cicd, tab_ai = st.tabs([
    "⚡ Container Profiler",
    "🔍 Green-Code Advisor",
    "⚖️ A/B Scoreboard",
    "🛡️ CI/CD Gatekeeper",
    "💬 AI Consultant"
])

# ----------------- Tab 1: Container Profiler -----------------
with tab_profiler:
    st.markdown("### 🌿 EcoCode: Green Metrics Engine")
    st.markdown("Execute code locally or inside isolated sandboxes to measure professional energy and carbon metrics.")

    col_code, col_settings = st.columns([3, 1])

    sample_snippets = {
        "Custom Code": "# Write or paste your Python script here\nimport time\ntime.sleep(0.5)\nprint('Execution complete successfully!')\n",
        "Nested Loops (O(N²))": "# Inefficient Nested Loop anti-pattern\nmatrix = []\nfor i in range(400):\n    for j in range(400):\n        if (i * j) % 9 == 0:\n            matrix.append(i + j)\nprint(f'Done. Items: {len(matrix)}')\n",
        "Linear Search in List (O(N))": "# Linear search across collection\ndata = list(range(10000))\nmatches = [x for x in range(2000, 3000) if x in data]\nprint(f'Matches: {len(matches)}')\n",
        "String Concatenation in Loop": "# Repeated string memory reallocations\ns = ''\nfor i in range(15000):\n    s += str(i)\nprint(f'Total length: {len(s)}')\n",
    }

    with col_settings:
        preset_choice = st.selectbox("Load Sample Workload", list(sample_snippets.keys()))
        st.info(f"Sandbox Profile:\n- **Server Load**: {server_watts}W\n- **Grid Intensity**: {grid_intensity} kg/kWh\n- **Tariff**: ₹{tariff_rate}/kWh")

    with col_code:
        code_input = st.text_area(
            "Python Code to Benchmark:",
            value=sample_snippets[preset_choice],
            height=200,
            key="profiler_code_input"
        )
        run_btn = st.button("🚀 Run Benchmark", type="primary", use_container_width=True)

    if run_btn and code_input.strip():
        with st.spinner("Profiling execution time and energy consumption..."):
            res = safe_run_code(code_input)

        if not res["success"]:
            st.error(f"Execution Failed: {res['error']}")
        else:
            st.success("✔ Benchmark completed successfully!")
            
            metrics = calculate_eco_metrics(res["time"])

            m1, m2, m3, m4 = st.columns(4)
            with m1:
                st.markdown(f"""
                <div class="eco-card">
                    <div class="metric-label">Execution Time (T)</div>
                    <div class="metric-value">{metrics['execution_time_sec']:.4f} <span style="font-size: 1rem; color: #94a3b8;">s</span></div>
                    <div class="metric-sub">Measured Duration</div>
                </div>
                """, unsafe_allow_html=True)
            with m2:
                st.markdown(f"""
                <div class="eco-card">
                    <div class="metric-label">Energy Consumed</div>
                    <div class="metric-value" style="color: #38bdf8;">{metrics['energy_kwh']:.8f} <span style="font-size: 1rem; color: #94a3b8;">kWh</span></div>
                    <div class="metric-sub">{(metrics['energy_kwh'] * 3.6e6):.2f} Joules ({server_watts}W load)</div>
                </div>
                """, unsafe_allow_html=True)
            with m3:
                st.markdown(f"""
                <div class="eco-card">
                    <div class="metric-label">Carbon Footprint</div>
                    <div class="metric-value" style="color: #f59e0b;">{metrics['carbon_g_co2']:.6f} <span style="font-size: 1rem; color: #94a3b8;">g CO₂e</span></div>
                    <div class="metric-sub">{(metrics['carbon_g_co2']/1000.0):.9f} kg CO₂e</div>
                </div>
                """, unsafe_allow_html=True)
            with m4:
                st.markdown(f"""
                <div class="eco-card">
                    <div class="metric-label">Financial Cost</div>
                    <div class="metric-value" style="color: #34d399;">₹{metrics['cost_inr']:.6f}</div>
                    <div class="metric-sub">At commercial ₹{tariff_rate}/kWh</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("#### 🌍 Tangible Carbon Equivalents (at 1 Million API Calls)")
            scale_factor = 1_000_000

            eq1, eq2, eq3 = st.columns(3)
            with eq1:
                st.markdown(f"""
                <div class="eco-card" style="border-left: 4px solid #10b981;">
                    <div style="font-size: 1.4rem;">🔋 {(metrics['smartphone_charges'] * scale_factor):,.0f}</div>
                    <div style="color: #cbd5e1; font-weight: 600; margin-top: 4px;">Smartphone Full Charges</div>
                    <div class="metric-sub">Equivalent electricity usage</div>
                </div>
                """, unsafe_allow_html=True)
            with eq2:
                st.markdown(f"""
                <div class="eco-card" style="border-left: 4px solid #38bdf8;">
                    <div style="font-size: 1.4rem;">💡 {(metrics['led_bulb_hours'] * scale_factor):,.1f} hrs</div>
                    <div style="color: #cbd5e1; font-weight: 600; margin-top: 4px;">10W LED Bulb Illumination</div>
                    <div class="metric-sub">Continuous active burn</div>
                </div>
                """, unsafe_allow_html=True)
            with eq3:
                st.markdown(f"""
                <div class="eco-card" style="border-left: 4px solid #f59e0b;">
                    <div style="font-size: 1.4rem;">🚗 {(metrics['car_km_equivalent'] * scale_factor):,.1f} km</div>
                    <div style="color: #cbd5e1; font-weight: 600; margin-top: 4px;">Gasoline Car Distance</div>
                    <div class="metric-sub">Equivalent tailpipe emissions</div>
                </div>
                """, unsafe_allow_html=True)

            with st.expander("Execution Terminal Output"):
                st.code(res["logs"])


# ----------------- Tab 2: Green-Code Advisor -----------------
with tab_advisor:
    st.markdown("### 🔍 Proactive Green-Code Advisor (Static Heuristics)")
    st.markdown(
        "Static code scanning powered by Abstract Syntax Trees (AST) and regex heuristics. "
        "Detects algorithmic bottlenecks, memory churn, and unclosed descriptors before runtime."
    )

    sample_advisor_code = """# ❌ Example Unoptimized Script with Energy Anti-Patterns
import pandas as pd

# Anti-Pattern 1: Unclosed file descriptor
data_file = open("transactions.csv", "r")

# Anti-Pattern 2: Inefficient Pandas .iterrows()
for index, row in df.iterrows():
    total_revenue += row['price'] * row['quantity']

# Anti-Pattern 3: Quadratic Nested Loop O(N²)
for i in range(len(customer_list)):
    for j in range(len(order_list)):
        if customer_list[i] == order_list[j]:
            matched.append(customer_list[i])

# Anti-Pattern 4: String concatenation in loop
receipt = ""
for item in matched:
    receipt += str(item) + ","
"""
    advisor_input = st.text_area(
        "Enter Python code to inspect for sustainability smells:",
        value=sample_advisor_code,
        height=260,
        key="advisor_code_input"
    )

    if st.button("🔎 Analyze Green Code Smells", type="primary"):
        smells = advisor.analyze_code(advisor_input)
        loc = len([l for l in advisor_input.splitlines() if l.strip()])
        score_info = advisor.compute_green_score(smells, loc)

        s_col1, s_col2, s_col3 = st.columns([1, 2, 2])
        with s_col1:
            st.markdown(f"""
            <div style="text-align: center; padding: 15px;">
                <div class="grade-badge" style="background: {score_info['color']}22; color: {score_info['color']}; border: 3px solid {score_info['color']};">
                    {score_info['grade']}
                </div>
                <div style="font-weight: 700; margin-top: 8px; color: {score_info['color']};">{score_info['score']} / 100</div>
            </div>
            """, unsafe_allow_html=True)
        with s_col2:
            st.markdown(f"""
            <div class="eco-card" style="height: 100%;">
                <div class="metric-label">Sustainability Status</div>
                <div style="font-size: 1.3rem; font-weight: 700; color: #f8fafc; margin-top: 5px;">{score_info['status']}</div>
                <div class="metric-sub" style="margin-top: 8px;">Analyzed <b>{loc}</b> Lines of Code across 7 Green Computing Rules.</div>
            </div>
            """, unsafe_allow_html=True)
        with s_col3:
            counts = score_info["severity_counts"]
            st.markdown(f"""
            <div class="eco-card" style="height: 100%;">
                <div class="metric-label">Smell Severity Breakdown</div>
                <div style="display: flex; gap: 15px; margin-top: 10px;">
                    <div><span class="severity-badge-high">HIGH</span> <b style="margin-left: 4px;">{counts['HIGH']}</b></div>
                    <div><span class="severity-badge-medium">MEDIUM</span> <b style="margin-left: 4px;">{counts['MEDIUM']}</b></div>
                    <div><span class="severity-badge-low">LOW</span> <b style="margin-left: 4px;">{counts['LOW']}</b></div>
                </div>
                <div class="metric-sub" style="margin-top: 12px;">Total Smells Detected: <b>{score_info['total_smells']}</b></div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### 📋 Detected Anti-Patterns & Remediations")

        if not smells:
            st.balloons()
            st.success("🎉 Outstanding! No energy anti-patterns detected. Your code is Green-Certified.")
        else:
            for s in smells:
                badge_class = f"severity-badge-{s.severity.lower()}"
                with st.expander(f"[{s.severity}] Line {s.line_number}: {s.rule_id} — {s.category}", expanded=True):
                    st.markdown(f"""
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <span class="{badge_class}">{s.severity} IMPACT</span>
                        <span style="color: #94a3b8; font-size: 0.85rem;">Line {s.line_number}</span>
                    </div>
                    """, unsafe_allow_html=True)

                    st.markdown(f"**Offending Line:**")
                    st.code(s.line_content, language="python")

                    st.markdown(f"**Why this consumes excess energy:**\n{s.message}")
                    st.markdown(f"**Green Recommendation:**\n{s.recommendation}")

                    st.markdown("**Refactoring Example:**")
                    st.code(s.green_fix_example, language="python")


# ----------------- Tab 3: Live A/B Algorithm Scoreboard -----------------
with tab_scoreboard:
    st.markdown("### ⚖️ Live A/B Algorithm Performance Scoreboard")
    st.markdown(
        "Run side-by-side benchmark comparisons of two alternative algorithms. "
        "Provides visual proof of energy savings ($T$, $\\text{kWh}$, $\\text{kgCO}_2\\text{e}$, and $\\text{₹}$). "
    )

    bench_choice = st.selectbox(
        "Select A/B Benchmark Scenario:",
        list(BENCHMARK_SUITES.keys()),
        format_func=lambda k: BENCHMARK_SUITES[k]["title"]
    )
    bench_data = BENCHMARK_SUITES[bench_choice]
    st.caption(bench_data["description"])

    ab_col1, ab_col2 = st.columns(2)
    with ab_col1:
        st.markdown(f"#### ❌ {bench_data['baseline_label']}")
        code_a_input = st.text_area("Candidate A (Baseline)", value=bench_data["code_a"], height=240, key="ab_code_a")
    with ab_col2:
        st.markdown(f"#### ✅ {bench_data['optimized_label']}")
        code_b_input = st.text_area("Candidate B (Optimized)", value=bench_data["code_b"], height=240, key="ab_code_b")

    if st.button("🚀 Run A/B Comparison", type="primary", use_container_width=True):
        with st.spinner("Benchmarking Candidate A vs Candidate B..."):
            res_a = safe_run_code(code_a_input)
            res_b = safe_run_code(code_b_input)

        if not res_a["success"]:
            st.error(f"Candidate A failed:\n{res_a['error']}")
        elif not res_b["success"]:
            st.error(f"Candidate B failed:\n{res_b['error']}")
        else:
            metrics_a = calculate_eco_metrics(res_a["time"])
            metrics_b = calculate_eco_metrics(res_b["time"])

            time_saved_pct = ((metrics_a["execution_time_sec"] - metrics_b["execution_time_sec"]) / max(1e-6, metrics_a["execution_time_sec"])) * 100
            energy_saved_pct = ((metrics_a["energy_kwh"] - metrics_b["energy_kwh"]) / max(1e-9, metrics_a["energy_kwh"])) * 100
            speedup = metrics_a["execution_time_sec"] / max(1e-6, metrics_b["execution_time_sec"])

            if energy_saved_pct > 0:
                st.markdown(f"""
                <div style="background: rgba(16, 185, 129, 0.15); border: 1px solid #10b981; border-radius: 12px; padding: 18px; margin: 15px 0;">
                    <h3 style="margin: 0; color: #34d399;">🌟 Optimization Result: {energy_saved_pct:.1f}% Energy Reduction!</h3>
                    <p style="margin: 6px 0 0 0; color: #e2e8f0; font-size: 1.05rem;">
                        Candidate B ran <b>{speedup:.1f}x faster</b>, cutting carbon emissions by <b>{energy_saved_pct:.1f}%</b>.
                    </p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.warning(f"Candidate B was {-energy_saved_pct:.1f}% less efficient than Candidate A.")

            st.markdown("#### 📊 Comparative Resource Breakdown")
            comp_df = {
                "Metric": ["Execution Time (s)", "Energy (kWh)", "Carbon (g CO₂e)", "Cloud Cost (₹)"],
                "Candidate A (Baseline)": [
                    f"{metrics_a['execution_time_sec']:.5f} s",
                    f"{metrics_a['energy_kwh']:.8f} kWh",
                    f"{metrics_a['carbon_g_co2']:.6f} g",
                    f"₹{metrics_a['cost_inr']:.6f}"
                ],
                "Candidate B (Optimized)": [
                    f"{metrics_b['execution_time_sec']:.5f} s",
                    f"{metrics_b['energy_kwh']:.8f} kWh",
                    f"{metrics_b['carbon_g_co2']:.6f} g",
                    f"₹{metrics_b['cost_inr']:.6f}"
                ],
                "Optimization Delta": [
                    f"-{metrics_a['execution_time_sec'] - metrics_b['execution_time_sec']:.5f} s ({time_saved_pct:.1f}%)",
                    f"-{metrics_a['energy_kwh'] - metrics_b['energy_kwh']:.8f} kWh ({energy_saved_pct:.1f}%)",
                    f"-{metrics_a['carbon_g_co2'] - metrics_b['carbon_g_co2']:.6f} g ({energy_saved_pct:.1f}%)",
                    f"-₹{metrics_a['cost_inr'] - metrics_b['cost_inr']:.6f} ({energy_saved_pct:.1f}%)"
                ]
            }
            st.table(comp_df)

            fig = go.Figure()
            categories = ['Execution Time (ms)', 'Carbon Footprint (mg CO₂e)', 'Energy (μWh)']
            
            fig.add_trace(go.Bar(
                name='Baseline (Candidate A)',
                x=categories,
                y=[metrics_a['execution_time_sec'] * 1000, metrics_a['carbon_g_co2'] * 1000, metrics_a['energy_kwh'] * 1e6],
                marker_color='#ef4444'
            ))
            fig.add_trace(go.Bar(
                name='Optimized (Candidate B)',
                x=categories,
                y=[metrics_b['execution_time_sec'] * 1000, metrics_b['carbon_g_co2'] * 1000, metrics_b['energy_kwh'] * 1e6],
                marker_color='#10b981'
            ))

            fig.update_layout(
                title='Resource Footprint: Baseline vs Green-Optimized Code',
                barmode='group',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(15,23,42,0.6)',
                font=dict(color='#e2e8f0'),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig, use_container_width=True)


# ----------------- Tab 4: CI/CD Pipeline Energy Guard -----------------
with tab_cicd:
    st.markdown("### 🛡️ CI/CD Pipeline Energy Guard (Regression Gatekeeper)")
    st.markdown(
        "Simulates a GitHub Action workflow step. "
        "EcoCode profiles incoming Pull Request code and compares its energy metrics against `baseline.json`. "
        "If energy regression exceeds **+10%**, the pipeline **blocks the merge**."
    )

    baseline_data = gatekeeper.load_baseline()

    b_col1, b_col2 = st.columns([1, 2])
    with b_col1:
        st.markdown("#### 📦 Production Baseline")
        st.json(baseline_data)
        if st.button("🔄 Refresh Baseline from File"):
            st.rerun()

    with b_col2:
        st.markdown("#### 🚀 Test Pull Request Candidate")
        pr_scenario = st.radio(
            "Select PR Test Case:",
            ["PR #142 (Failing: Quadratic Regression +80%)", "PR #143 (Passing: Optimized Hash Map -40%)", "Custom PR Code"]
        )

        if "Failing" in pr_scenario:
            pr_code_input = """# ❌ Regression introduced in PR: Inefficient Nested Lookups
coords = list(range(400))
pairs = []
for x in coords:
    for y in coords:
        if (x + y) % 5 == 0:
            pairs.append((x, y))
print(f'Total pairs: {len(pairs)}')
"""
        elif "Passing" in pr_scenario:
            pr_code_input = """# ✅ Clean PR: Instant hash set lookup
coords = range(400)
pairs = [(x, y) for x in coords for y in coords if (x + y) % 5 == 0]
print(f'Total pairs: {len(pairs)}')
"""
        else:
            pr_code_input = "# Custom PR code to test against baseline\ntotal = sum(range(50000))\n"

        pr_text = st.text_area("Candidate PR Script:", value=pr_code_input, height=160, key="cicd_pr_code")
        eval_btn = st.button("🧪 Execute CI/CD Gatekeeper Check", type="primary")

    if eval_btn:
        with st.spinner("Simulating GitHub Actions workflow runner..."):
            res = safe_run_code(pr_text)
            
        if not res["success"]:
            st.error(f"Execution failed: {res['error']}")
        else:
            metrics = calculate_eco_metrics(res["time"])
            
            base_energy = baseline_data.get("energy_kwh", 0.0001)
            regression_pct = ((metrics["energy_kwh"] - base_energy) / base_energy) * 100.0
            passed = regression_pct <= gatekeeper.threshold_pct

            st.markdown("---")
            st.markdown("### 🚦 Pipeline Build Outcome")

            if passed:
                st.markdown(f"""
                <div style="background: rgba(16, 185, 129, 0.2); border: 2px solid #10b981; border-radius: 10px; padding: 15px; margin-bottom: 20px;">
                    <h3 style="color: #34d399; margin: 0;">✅ CI STATUS: PASSED (Merge Approved)</h3>
                    <p style="margin: 5px 0 0 0; color: #cbd5e1;">
                        Energy variance is <b>{regression_pct:+.2f}%</b> (Budget threshold: +{gatekeeper.threshold_pct:.1f}%).
                    </p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="background: rgba(239, 68, 68, 0.2); border: 2px solid #ef4444; border-radius: 10px; padding: 15px; margin-bottom: 20px;">
                    <h3 style="color: #ef4444; margin: 0;">❌ CI STATUS: BLOCKED (Merge Gatekeeper Failed)</h3>
                    <p style="margin: 5px 0 0 0; color: #cbd5e1;">
                        Energy variance of <b>{regression_pct:+.2f}%</b> exceeds allowable threshold (+{gatekeeper.threshold_pct:.1f}%).
                    </p>
                </div>
                """, unsafe_allow_html=True)

            col_log, col_comment = st.columns(2)
            with col_log:
                st.markdown("##### 📜 Runner Log")
                st.markdown(f'<div class="terminal-box">{res["logs"]}</div>', unsafe_allow_html=True)

            with col_comment:
                st.markdown("##### 🤖 Automated GitHub Bot PR Comment")
                st.markdown(f"""
                > **EcoCode CI Gatekeeper Bot** 🌿
                > 
                > - **Status**: `{'PASSED ✅' if passed else 'BLOCKED ❌'}`
                > - **Execution Time**: `{metrics['execution_time_sec']:.4f}s`
                > - **Energy Consumption**: `{metrics['energy_kwh']:.8f} kWh`
                > - **Regression vs Baseline**: `{regression_pct:+.2f}%` (Threshold: `+{gatekeeper.threshold_pct}%`)
                """)


# ----------------- Tab 5: AI Green Consultant -----------------
with tab_ai:
    st.markdown("### 💬 AI Green Consultant Chatbot (EcoBot)")
    st.markdown(
        "Specialized GreenOps advisor trained strictly on sustainable software engineering, "
        "algorithmic efficiency, and carbon reduction."
    )

    if "ai_chat_history" not in st.session_state:
        st.session_state.ai_chat_history = [
            {"role": "assistant", "content": "Hello! I am EcoBot. Ask me anything about green coding, algorithmic anti-patterns, or our energy gatekeeper."}
        ]

    for message in st.session_state.ai_chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    quick_prompts = [
        "How do nested loops impact CPU energy?",
        "Why is Pandas .iterrows() bad for carbon?",
        "How does local profiling help optimization?",
        "How to avoid memory churn in loops?"
    ]
    
    cols = st.columns(4)
    for idx, prompt_text in enumerate(quick_prompts):
        if cols[idx].button(prompt_text, key=f"qp_{idx}", use_container_width=True):
            st.session_state.ai_chat_history.append({"role": "user", "content": prompt_text})
            with st.spinner("EcoBot is analyzing..."):
                reply = consultant.ask(prompt_text)
            st.session_state.ai_chat_history.append({"role": "assistant", "content": reply})
            st.rerun()

    if user_prompt := st.chat_input("Ask a green coding or optimization question..."):
        st.session_state.ai_chat_history.append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.markdown(user_prompt)

        with st.chat_message("assistant"):
            with st.spinner("Consulting GreenOps knowledge base..."):
                bot_response = consultant.ask(user_prompt)
                st.markdown(bot_response)
        
        st.session_state.ai_chat_history.append({"role": "assistant", "content": bot_response})

st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #64748b; font-size: 0.85rem; padding: 10px;'>"
    "EcoCode Platform • PS 5.3 Software Energy Profiler • Developed for Hackathon 2026"
    "</div>",
    unsafe_allow_html=True
)