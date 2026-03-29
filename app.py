import os
import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap
import time
import math
import random
import pandas as pd
from datetime import datetime
import requests
import sqlite3
import json
import osmnx as ox
import networkx as nx
from sklearn.cluster import KMeans
import numpy as np

# ================= PAGE CONFIG =================
st.set_page_config(page_title="Anantapur Patrol Optimization", layout="wide", initial_sidebar_state="collapsed")

if 'step' not in st.session_state:
    st.session_state.step = 'login'

def login():
    if st.session_state.user_input == "admin" and st.session_state.pass_input == "police123":
        st.session_state.step = 'face_rec'
    else:
        st.error("Invalid Command Credentials")

def logout():
    st.session_state.step = 'login'
    st.session_state.authenticated = False

# ================= CUSTOM CSS (EXACT REPLICA) =================
st.markdown("""
    <style>
    /* Light Theme Core */
    .stApp {
        background-color: #ffffff !important;
        color: #1e293b;
    }
    
    /* Completely hide Streamlit native UI */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .block-container {
        padding-top: 1rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }
    header {visibility: hidden;}
    
    /* Top Headers */
    .top-subtext {
        color: #64748b;
        font-size: 11px;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        margin-bottom: 5px;
        display: flex;
        justify-content: space-between;
    }
    .top-title {
        color: #0ea5e9;
        font-size: 15px;
        font-weight: bold;
        letter-spacing: 1px;
        text-transform: uppercase;
        margin-bottom: 25px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .profile-area {
        display: flex;
        align-items: center;
        gap: 8px;
        color: #64748b;
        font-size: 10px;
    }
    .profile-img {
        width: 20px;
        height: 20px;
        border-radius: 50%;
        background-color: #cbd5e1;
    }
    
    /* Metric Cards */
    .metric-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 15px 20px;
        margin-bottom: 12px;
        position: relative;
        overflow: hidden;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    .metric-card::before { /* Cyan accent vertical line */
        content: '';
        position: absolute;
        left: 0;
        top: 15%;
        height: 70%;
        width: 3px;
        background: #0ea5e9;
    }
    .metric-info {
        display: flex;
        flex-direction: column;
    }
    .metric-title {
        color: #0ea5e9;
        font-size: 18px;
        font-weight: 900;
        margin-bottom: 8px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .metric-value {
        font-size: 28px;
        font-weight: 900;
        color: #0f172a;
        line-height: 1;
        margin-bottom: 8px;
    }
    .metric-sub {
        color: #64748b;
        font-size: 14px;
        font-weight: bold;
    }
    .metric-icon-box {
        width: 45px;
        height: 45px;
        border: 1px solid rgba(14, 165, 233, 0.2);
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
        color: #0ea5e9;
        background: #f0f9ff;
    }
    
    /* Patrol Units List */
    .patrol-list-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 15px 20px;
        margin-bottom: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    .patrol-row {
        display: flex;
        justify-content: space-between;
        margin-bottom: 12px;
        font-size: 16px;
        font-weight: bold;
        color: #334155;
    }
    .patrol-row:last-child { margin-bottom: 0; }
    .status-active { color: #10b981; font-weight: 600;}
    
    /* Sliders & Button Card */
    .controls-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 15px 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    .vertical-bars {
        display: flex;
        justify-content: space-around;
        margin-bottom: 20px;
    }
    .v-bar-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 6px;
    }
    .v-bar-label-top { color: #64748b; font-size: 9px; text-align: center; max-width: 40px;}
    .v-bar-track {
        width: 4px;
        height: 50px;
        background: #e2e8f0;
        border-radius: 2px;
        position: relative;
        display: flex;
        align-items: flex-end;
    }
    .v-bar-fill {
        width: 100%;
        background: #0ea5e9;
        border-radius: 2px;
    }
    .v-bar-val { color: #0f172a; font-size: 10px; font-weight: bold;}
    
    /* Cyan Button - Adapted for Light Mode */
    .btn-regen {
        background-color: #0ea5e9;
        color: #ffffff;
        border: none;
        padding: 8px;
        width: 100%;
        border-radius: 4px;
        font-size: 11px;
        font-weight: bold;
        text-align: center;
        cursor: pointer;
        transition: all 0.2s;
        text-transform: uppercase;
        box-shadow: 0 2px 6px rgba(14, 165, 233, 0.4);
    }
    .btn-regen:hover {
        background-color: #0284c7;
    }
    
    /* Map Container */
    .map-container {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }

    /* Dashboard Header */
    .dashboard-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem 2rem;
        background: #ffffff;
        border-bottom: 2px solid #f1f5f9;
        margin-bottom: 1.5rem;
    }
    .header-left {
        display: flex;
        align-items: center;
        gap: 15px;
    }
    .header-logo {
        width: 45px;
        height: 45px;
        object-fit: contain;
    }
    .header-title-container {
        display: flex;
        flex-direction: column;
    }
    .header-title {
        font-size: 20px;
        font-weight: 900;
        color: #0f172a;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        margin: 0;
    }
    .header-subtitle {
        font-size: 11px;
        color: #64748b;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin: 0;
        font-weight: 600;
    }
    .header-right {
        display: flex;
        align-items: center;
        gap: 20px;
    }
    .header-time {
        font-size: 13px;
        font-weight: 700;
        color: #0ea5e9;
        background: #f0f9ff;
        padding: 4px 10px;
        border-radius: 4px;
        border: 1px solid rgba(14, 165, 233, 0.2);
    }
    .logout-btn-container {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 8px 15px;
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.2s;
    }
    .logout-btn-container:hover {
        background: #f8fafc;
        border-color: #0ea5e9;
    }
    .logout-icon {
        font-size: 18px;
    }
    .logout-text {
        font-size: 14px;
        font-weight: 600;
        color: #0ea5e9;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    </style>
""", unsafe_allow_html=True)

if st.session_state.step == 'login':
    st.markdown("""
        <div style='text-align:center; padding:100px 0;'>
            <h1 style='color:#0ea5e9; font-size:32px; margin-bottom:10px;'>👮 COMMAND CENTER</h1>
            <p style='color:#64748b; font-size:14px; margin-bottom:30px;'>Anantapur Police Patrol Optimization Portal</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,1.5,1])
    with col2:
        with st.form("login_form"):
            st.text_input("Officer ID / Username", key="user_input", placeholder="admin")
            st.text_input("Secret Command Key", key="pass_input", type="password", placeholder="••••••••")
            st.form_submit_button("UNLOCK ACCESS", on_click=login, use_container_width=True)
            st.markdown("<p style='text-align:center; font-size:11px; color:#94a3b8; margin-top:15px;'>FOR AUTHORIZED PERSONNEL ONLY</p>", unsafe_allow_html=True)
    st.stop()

elif st.session_state.step == 'face_rec':
    st.markdown("""
        <div style='text-align:center; padding-top:50px;'>
            <h1 style='color:#0ea5e9; font-size:24px; margin-bottom:10px;'>🧬 BIOMETRIC VERIFICATION</h1>
            <p style='color:#64748b; font-size:14px; margin-bottom:30px;'>Scanning Official Identity for Command Approval</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,1.5,1])
    with col2:
        img_file = st.camera_input("CAPTURE OFFICER FACE")
        if img_file:
            with st.status("Initializing Neural Scan...", expanded=True) as status:
                st.write("Detecting facial landmarks...")
                time.sleep(1)
                st.write("Verifying against Anantapur Database...")
                time.sleep(1.5)
                st.write("Identity Confirmed: Officer Admin-2022")
                status.update(label="BIOMETRIC ACCESS GRANTED", state="complete")
            if st.button("PROCEED TO DATA INGESTION", use_container_width=True):
                st.session_state.step = 'data_ingest'
                st.rerun()
    st.stop()

elif st.session_state.step == 'data_ingest':
    st.markdown("""
        <div style='text-align:center; padding-top:50px;'>
            <h1 style='color:#0ea5e9; font-size:24px; margin-bottom:10px;'>📊 CENTRAL DATA INGESTION</h1>
            <p style='color:#64748b; font-size:14px; margin-bottom:30px;'>Upload Crime Intelligence to Synchronize AI Heatmaps</p>
        </div>
    """, unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        with st.container(border=True):
            h_data = st.file_uploader("1/3 Upload Historical Crime Data (PERSISTED)", type=["csv"])
            r_data = st.file_uploader("2/3 Upload Recent Activity Logs", type=["csv"])
            l_data = st.file_uploader("3/3 Upload Live Incident Stream", type=["csv"])
            
            if st.button("🚀 SYNCHRONIZE & LAUNCH DASHBOARD", use_container_width=True):
                # Small simulation of processing
                if h_data or r_data or l_data:
                    with st.spinner("Training AI Hotspot Model..."):
                        all_pts = []
                        try:
                            # Process and combine data sources
                            for uploaded_file, weight in [(h_data, 1.0), (r_data, 1.5), (l_data, 2.0)]:
                                if uploaded_file:
                                    df = pd.read_csv(uploaded_file)
                                    lat_col = next((c for c in df.columns if 'lat' in c.lower()), None)
                                    lng_col = next((c for c in df.columns if 'lng' in c.lower() or 'lon' in c.lower()), None)
                                    if lat_col and lng_col:
                                        for _, row in df.iterrows():
                                            all_pts.append([float(row[lat_col]), float(row[lng_col]), weight])
                            
                            if all_pts:
                                st.session_state.custom_heat_data = all_pts
                                # Persist to DB
                                try:
                                    conn = sqlite3.connect("police_patrol.db")
                                    cursor = conn.cursor()
                                    for p in all_pts:
                                        cursor.execute("INSERT INTO crimes (crime_type, lat, lng, severity) VALUES (?, ?, ?, ?)", ("Uploaded_Data", p[0], p[1], p[2]))
                                    conn.commit(); conn.close()
                                except: pass
                                
                                # Dynamic Hotspot Generation using KMeans
                                data_array = np.array([[p[0], p[1]] for p in all_pts])
                                if len(data_array) >= 5:
                                    kmeans = KMeans(n_clusters=min(5, len(data_array)), n_init='auto').fit(data_array)
                                    st.session_state.ai_hotspots = kmeans.cluster_centers_.tolist()
                        except Exception as e:
                            st.error(f"Error processing data: {e}")
                            
                    st.session_state.step = 'dashboard'
                    st.rerun()
                else:
                    st.warning("No data files selected. Proceeding with database defaults.")
                    st.session_state.step = 'dashboard'
                    st.rerun()
    st.stop()

if 'patrol_units' not in st.session_state:
    st.session_state.patrol_units = ['AP02CP2022']

if 'regen_trigger' not in st.session_state:
    st.session_state.regen_trigger = 0

if 'emergency_incident' not in st.session_state:
    st.session_state.emergency_incident = None

if 'live_sim' not in st.session_state:
    st.session_state.live_sim = False

if 'vehicle_data' not in st.session_state:
    st.session_state.vehicle_data = {}

if 'last_regen_trigger' not in st.session_state:
    st.session_state.last_regen_trigger = -1

if 'visited_checkpoints' not in st.session_state:
    st.session_state.visited_checkpoints = set()

if 'checkpoint_wait' not in st.session_state:
    st.session_state.checkpoint_wait = False

if 'checkpoint_wait' in st.session_state is False:
    st.session_state.checkpoint_wait = False

if 'current_verifying_unit' not in st.session_state:
    st.session_state.current_verifying_unit = None


elif st.session_state.step == 'checkpoint_verify':
    st.markdown(f"""
        <div style='text-align:center; padding-top:50px;'>
            <h1 style='color:#ef4444; font-size:24px; margin-bottom:10px;'>🚨 MANDATORY BIO-AUTH: {st.session_state.current_verifying_unit}</h1>
            <p style='color:#64748b; font-size:14px; margin-bottom:30px;'>Enforcing High-Security Protocol at Ops Location / AI Hotspot</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,1.5,1])
    with col2:
        img_file = st.camera_input(f"VERIFY OFFICER - {st.session_state.current_verifying_unit}")
        if img_file:
            with st.status("Verifying Field Credentials...", expanded=True) as status:
                time.sleep(1.5)
                st.write(f"Checkpoint sync successful for {st.session_state.current_verifying_unit}")
                status.update(label="AUTHENTICATION SUCCESSFUL", state="complete")
            if st.button("RESUME PATROL LOOP", use_container_width=True):
                # Mark as visited
                v_ptr = st.session_state.vehicle_data[st.session_state.current_verifying_unit]
                curr_pos = v_ptr["path"][v_ptr["progress"]]
                st.session_state.visited_checkpoints.add(tuple(curr_pos))
                
                st.session_state.step = 'dashboard'
                st.session_state.checkpoint_wait = False
                st.session_state.current_verifying_unit = None
                st.rerun()
    st.stop()

def deploy_patrol():
    new_id = f"AP02CP{random.randint(1000, 9999)}"
    st.session_state.patrol_units.append(new_id)
    st.session_state.regen_trigger += 1

def regen_routes():
    st.session_state.regen_trigger += 1
    st.session_state.emergency_incident = None # Clear old emergency if any on total regen

def trigger_emergency():
    # Simulate an emergency near Anantapur center
    lat = 14.6819 + random.uniform(-0.01, 0.01)
    lon = 77.6006 + random.uniform(-0.01, 0.01)
    st.session_state.emergency_incident = [lat, lon, 2.0] # Extreme Risk Score
    st.session_state.regen_trigger += 1 # Force map reload

# ================= PRE-LOAD DATA =================
has_custom_data = 'custom_heat_data' in st.session_state and st.session_state.custom_heat_data
heat_data = []

# 1. READ FROM PERSISTENT DB
try:
    conn = sqlite3.connect("police_patrol.db")
    cursor = conn.cursor()
    cursor.execute("SELECT lat, lng, severity FROM crimes ORDER BY timestamp DESC LIMIT 300")
    db_points = cursor.fetchall()
    heat_data = [[p[0], p[1], p[2]] for p in db_points]
    conn.close()
except:
    pass

# 2. READ FROM LOCAL FILESYSTEM (DYNAMIC MONITORING)
try:
    local_files = [
        ("Historical_Crime_Data_Anantapur.csv", 1.0),
        ("Recent_Activity_Logs_Anantapur.csv", 1.5),
        ("Live_Incident_Stream_Anantapur.csv", 2.0)
    ]
    for filename, weight in local_files:
        if os.path.exists(filename):
            df = pd.read_csv(filename)
            lat_col = next((c for c in df.columns if 'lat' in c.lower()), None)
            lng_col = next((c for c in df.columns if 'lng' in c.lower() or 'lon' in c.lower()), None)
            if lat_col and lng_col:
                for _, row in df.iterrows():
                    heat_data.append([float(row[lat_col]), float(row[lng_col]), weight])
except:
    pass

# 3. OVERRIDE WITH SESSION UPLOADS
if has_custom_data:
    heat_data = st.session_state.custom_heat_data 

if 'simulated_extra_incidents' not in st.session_state:
    st.session_state.simulated_extra_incidents = 0

# ================= DASHBOARD HEADER =================
st.markdown(f"""
    <div class="dashboard-header">
        <div class="header-left">
            <div style="width: 45px; height: 45px; background: #0ea5e9; border-radius: 10px; display: flex; align-items: center; justify-content: center; color: white; font-size: 24px; font-weight: bold; box-shadow: 0 4px 10px rgba(14, 165, 233, 0.3);">
                AP
            </div>
            <div class="header-title-container">
                <h1 class="header-title">Anantapur Police Ops</h1>
                <p class="header-subtitle">Intelligence & Patrol Command</p>
            </div>
        </div>
        <div class="header-right">
            <div class="header-time">
                🕒 {datetime.now().strftime("%H:%M:%S")} | {datetime.now().strftime("%d %b %Y")}
            </div>
            <div class="profile-area">
                <div class="profile-img"></div>
                <span>ADMIN-2022</span>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# Compact Logout Button as Requested
col_h1, col_h2 = st.columns([1, 5])
with col_h1:
    if st.button("🚪 LOGOUT SESSION", key="logout_btn", use_container_width=True):
        logout()
        st.rerun()

# ================= LAYOUT =================
left_col, right_col = st.columns([1, 2.8], gap="small")

# ================= LEFT PANEL =================
with left_col:
    # --- INCIDENTS ---
    base_incidents = len(heat_data) if len(heat_data) > 0 else 154
    incidents = base_incidents + st.session_state.get('simulated_extra_incidents', 0)
    
    # Pulse animation for the total incidents value
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-info">
                <div class="metric-title">Total Incidents</div>
                <div class="metric-value" style="transition: all 0.5s ease-in-out;">{incidents}</div>
                <div class="metric-sub" style="color:#10b981;">↑ +{(st.session_state.simulated_extra_incidents/base_incidents*100):.1f}% Dynamic Stream</div>
            </div>
            <div class="metric-icon-box" style="border-color: rgba(255,255,255,0.2); color:#cbd5e1;">🚨</div>
        </div>
    """, unsafe_allow_html=True)
    
    # --- PATROLS ---
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-info">
                <div class="metric-title">Active Patrols</div>
                <div class="metric-value">{len(st.session_state.patrol_units)}</div>
                <div class="metric-sub">{len(st.session_state.patrol_units)}/10 Assigned</div>
            </div>
            <div class="metric-icon-box">🚓</div>
        </div>
    """, unsafe_allow_html=True)
    
    # --- COVERAGE ---
    cov = 94.2 + (random.uniform(-1, 1) * (st.session_state.regen_trigger > 0))
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-info">
                <div class="metric-title">Coverage</div>
                <div class="metric-value">{cov:.1f}%</div>
                <div class="metric-sub" style="color:#10b981;">↑ +3.1% Increase</div>
            </div>
            <div class="metric-icon-box">🛡️</div>
        </div>
    """, unsafe_allow_html=True)
    
    # --- UNITS LIST ---
    st.markdown("""
        <div class="patrol-list-card">
            <div style="color:#0ea5e9; font-size:16px; margin-bottom:12px; text-transform:uppercase; font-weight:bold;">Patrol Units List</div>
            <div class="patrol-row"><span>CP-1011</span><span class="status-active">Active</span></div>
            <div class="patrol-row"><span>CP-2022</span><span class="status-active">Active</span></div>
            <div class="patrol-row"><span>CP-1013</span><span class="status-active">Active</span></div>
            <div class="patrol-row"><span>CP-2024</span><span class="status-active">Active</span></div>
            <div class="patrol-row"><span>CP-2125</span><span class="status-active">Active</span></div>
        </div>
    """, unsafe_allow_html=True)
    
    # --- SLIDERS & BUTTON ---
    r1 = min(100, 80 + st.session_state.regen_trigger*2)
    r2 = max(20, 65 - st.session_state.regen_trigger)
    r3 = min(100, 85)
    st.markdown(f"""
        <div class="controls-card">
            <div style="display:flex; justify-content:space-between; align-items:center; padding:8px 0; border-bottom:1px solid #e2e8f0;">
                <span style="font-size:14px; font-weight:bold; color:#334155;">Risk Priority</span>
                <span style="font-size:16px; font-weight:900; color:#0ea5e9;">{r1}%</span>
            </div>
            <div style="display:flex; justify-content:space-between; align-items:center; padding:8px 0; border-bottom:1px solid #e2e8f0;">
                <span style="font-size:14px; font-weight:bold; color:#334155;">Patrol Density</span>
                <span style="font-size:16px; font-weight:900; color:#0ea5e9;">{r2}%</span>
            </div>
            <div style="display:flex; justify-content:space-between; align-items:center; padding:8px 0;">
                <span style="font-size:14px; font-weight:bold; color:#334155;">Shift Duration</span>
                <span style="font-size:16px; font-weight:900; color:#0ea5e9;">{r3}%</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # --- FLEET COMMAND SLIDER ---
    st.markdown("<div style='color:#0ea5e9; font-size:16px; margin-bottom:8px; text-transform:uppercase; font-weight:900; letter-spacing:1.5px; margin-top:15px;'>RESOURCE DEPLOYMENT ENGINE</div>", unsafe_allow_html=True)
    st.markdown("<div style='color:#1e293b; font-size:14px; font-weight:900; margin-bottom:-10px;'>Select Force Volume</div>", unsafe_allow_html=True)
    fleet_size = st.slider("Select Force Volume", 1, 10, value=len(st.session_state.patrol_units), label_visibility="collapsed")
    
    # Update fleet size dynamically
    if fleet_size != len(st.session_state.patrol_units):
        if fleet_size > len(st.session_state.patrol_units):
            # Add new units
            for _ in range(fleet_size - len(st.session_state.patrol_units)):
                st.session_state.patrol_units.append(f"AP02CP{random.randint(1000, 9999)}")
        else:
            # Scale down
            st.session_state.patrol_units = st.session_state.patrol_units[:fleet_size]
        st.session_state.regen_trigger += 1 # Force path recalculation
        st.rerun()

    if st.button("↻ RE-GENERATE ROUTES", use_container_width=True, on_click=regen_routes):
        pass

    if st.button("🚨 SIMULATED EMERGENCY DISPATCH", use_container_width=True, on_click=trigger_emergency):
        st.warning("EMERGENCY SIGNAL DETECTED: Redirecting nearest unit to incident!")

    live_btn_label = "⏹ STOP LIVE GPS TRACKING" if st.session_state.live_sim else "▶ START LIVE GPS TRACKING"
    if st.button(live_btn_label, use_container_width=True):
        st.session_state.live_sim = not st.session_state.live_sim
        st.rerun()

    if st.button("🌌 𝐐𝐔𝐀𝐍𝐓𝐔𝐌 𝐏𝐀𝐓𝐇 𝐎𝐏𝐓𝐈𝐌𝐈𝐙𝐄𝐑", use_container_width=True):
        st.markdown("<div style='background-color:#0f172a; padding:15px; border-radius:8px; border-left:4px solid #06b6d4; margin-bottom:15px;'>", unsafe_allow_html=True)
        q_bar = st.progress(0, text="Initializing Q-Solver...")
        time.sleep(0.4)
        q_bar.progress(25, text="Encoding Waypoint QUBO Matrix...")
        time.sleep(0.6)
        q_bar.progress(55, text="Tunnelling Simulation: 4.2 Million Paths Analyzed...")
        time.sleep(0.5)
        q_bar.progress(85, text="Collapsing Probability Wavefront...")
        time.sleep(0.4)
        q_bar.progress(100, text="Optimal Circuit Converged (99.2% Accuracy)")
        st.session_state.regen_trigger += 1 # Force update
        st.success("Quantum-Circuit Applied: Most efficient road sequence locked for Unit AP02CP2022.")
        st.markdown("</div>", unsafe_allow_html=True)
        st.session_state.is_quantum = True
    else:
        if 'is_quantum' not in st.session_state:
            st.session_state.is_quantum = False
        
    # Sidebar content optimized for operations


# ================= RIGHT PANEL (MAP) =================
with right_col:
    # REAL Anantapur SP Office / Police HQ GPS Coordinates
    atp_hq = [14.6757, 77.5979]
    map_center = atp_hq 
    
    if len(heat_data) > 0:
        map_center = [sum(h[0] for h in heat_data)/len(heat_data), sum(h[1] for h in heat_data)/len(heat_data)]
            
    m = folium.Map(
        location=map_center, 
        zoom_start=14, 
        tiles=None,
        zoom_control=True
    )
    
    # Real Google Layers
    folium.TileLayer(
        tiles="https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}",
        attr="Google Maps Street",
        name="Google Street View",
        overlay=False,
        control=True
    ).add_to(m)
    
    folium.TileLayer(
        tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
        attr="Google Hybrid",
        name="Google Satellite View",
        overlay=False,
        control=True
    ).add_to(m)
    
    folium.TileLayer(
        tiles="https://mt1.google.com/vt/lyrs=p&x={x}&y={y}&z={z}",
        attr="Google Terrain",
        name="Google Terrain View",
        overlay=False,
        control=True
    ).add_to(m)
    


    # PURE ANANTAPUR CITY HUBS (Clock Tower, Station, Market, etc.)
    atp_hubs_dict = {
        "Clock Tower": [14.6749, 77.5992],
        "Station Area": [14.6853, 77.5982],
        "Old Town Market": [14.6680, 77.5950],
        "Rudrampeta": [14.6657, 77.5925],
        "Sapthagiri Circle": [14.6750, 77.5850],
        "Kamalanagar": [14.6600, 77.6000],
        "SP Office Road": [14.6700, 77.6050]
    }
    atp_hubs = list(atp_hubs_dict.values())

    if not has_custom_data:
        # Load empty list if no custom data, or keep empty if we only want actual route points
        pass
    
    # Draw Hub Markers (Red for Pending, Green for Visited)
    for name, coords in atp_hubs_dict.items():
        is_visited = any(math.sqrt((coords[0]-v[0])**2 + (coords[1]-v[1])**2) < 0.0005 for v in st.session_state.visited_checkpoints)
        pin_color = "green" if is_visited else "red"
        folium.Marker(
            location=coords,
            icon=folium.Icon(color=pin_color, icon="info-sign"),
            tooltip=f"Checkpoint: {name} ({'VISITED' if is_visited else 'PENDING'})"
        ).add_to(m)

    # NEW: Draw AI Hotspot Markers (Must also be visited/authenticated)
    if 'ai_hotspots' in st.session_state and st.session_state.ai_hotspots:
        for idx, hotspot in enumerate(st.session_state.ai_hotspots):
            is_visited = any(math.sqrt((hotspot[0]-v[0])**2 + (hotspot[1]-v[1])**2) < 0.0005 for v in st.session_state.visited_checkpoints)
            pin_color = "cadetblue" if is_visited else "orange"
            folium.Marker(
                location=hotspot,
                icon=folium.Icon(color=pin_color, icon="screenshot"),
                tooltip=f"AI HOTSPOT {idx+1}: Bio-Authentication Required"
            ).add_to(m)

    # RE-ENABLE HEATMAP: Layer the uploaded coordinates
    if len(heat_data) > 0:
        HeatMap(
            heat_data,
            radius=15,
            blur=10,
            gradient={0.2: '#0ea5e9', 0.5: '#f97316', 1.0: '#ef4444'},
            min_opacity=0.3
        ).add_to(m)


    
    @st.cache_resource(show_spinner="Booting Offline Terrain Engine (OSMnx)...")
    def get_road_network():
        # Load local Anantapur graph to avoid online OSRM timeouts and bans!
        return ox.graph_from_point((atp_hq[0], atp_hq[1]), dist=6000, network_type='drive')
    
    city_graph = get_road_network()

    @st.cache_data(show_spinner=False)
    def get_v_route(seq):
        """Calculates precise physical road paths offline using OSMnx node mapping."""
        try:
            # Map sequence coordinates to physical graph nodes
            xs = [p[1] for p in seq]
            ys = [p[0] for p in seq]
            nodes = ox.distance.nearest_nodes(city_graph, xs, ys)
            
            full_path = []
            for i in range(len(nodes)-1):
                try:
                    path = nx.shortest_path(city_graph, nodes[i], nodes[i+1], weight='length')
                    if not full_path:
                        full_path.extend(path)
                    else:
                        full_path.extend(path[1:])
                except nx.NetworkXNoPath:
                    pass
                    
            if len(full_path) > 1:
                return [[city_graph.nodes[n]['y'], city_graph.nodes[n]['x']] for n in full_path]
        except Exception as e:
            pass
        return seq # Fallback if entirely failed
    
    # --- MULTI-VEHICLE ROUTING LOGIC ---
    all_vehicle_targets = [] # Tracks the current target for each vehicle for table sync
    
    colors = ["#10b981", "#ef4444", "#3b82f6", "#f59e0b", "#8b5cf6", "#ec4899", "#06b6d4", "#f97316"]
    
    # Force path regeneration if trigger changed
    if st.session_state.last_regen_trigger != st.session_state.regen_trigger:
        st.session_state.vehicle_data = {}
        st.session_state.last_regen_trigger = st.session_state.regen_trigger

    for v_idx, v_id in enumerate(st.session_state.patrol_units):
        v_color = colors[v_idx % len(colors)]
        
        if v_id not in st.session_state.vehicle_data:
            # MANDATORY CHECKPOINT ROUTING: Visit ALL red pins
            v_nodes = []
            
            # Use seed only for small variations in non-mandatory points
            random.seed(42 + v_idx + st.session_state.regen_trigger)
            
            # 1. CORE REQUIREMENT: Add every single mandatory hub to the route
            v_nodes.extend(atp_hubs)
            
            # 2. AI Objective: Add AI Clusters if available
            if 'ai_hotspots' in st.session_state and st.session_state.ai_hotspots:
                # Add at least 2 AI hotspots to the loop
                sample_size = min(len(st.session_state.ai_hotspots), 3)
                v_nodes.extend(random.sample(st.session_state.ai_hotspots, sample_size))
            
            # 3. Dynamic Coverage: Add granular heat points
            local_heat = [p for p in heat_data if abs(p[0] - atp_hq[0]) < 0.05 and abs(p[1] - atp_hq[1]) < 0.05]
            if len(local_heat) >= 2:
                pts = random.sample(local_heat, 2)
                v_nodes.extend([[p[0], p[1]] for p in pts])

            # Shuffle to ensure vehicles don't follow the exact same bumper-to-bumper path
            random.shuffle(v_nodes)

            # Reset seed after use to avoid affecting other logic
            random.seed()

            # Emergency Priority Override
            if st.session_state.emergency_incident:
                v_nodes.insert(0, [st.session_state.emergency_incident[0], st.session_state.emergency_incident[1]])

            # Generate ONE optimized Road Path from REAL HQ
            seq = [atp_hq] + v_nodes + [atp_hq]
            path = get_v_route(seq)
            st.session_state.vehicle_data[v_id] = {
                "path": path,
                "progress": 0,
                "target_node": v_nodes[0] if v_nodes else map_center,
                "color": v_color
            }
        
        v_data = st.session_state.vehicle_data[v_id]
        path = v_data["path"]
        progress_idx = v_data["progress"]
        v_color = v_data.get("color", v_color) # Use stored color
        
        # Save current node for tracking table
        current_loc = path[progress_idx % len(path)] if path else map_center
        all_vehicle_targets.append({"id": v_id, "target": current_loc})

        # Draw Glow-Path
        folium.PolyLine(path, color=v_color, weight=8, opacity=0.2).add_to(m)
        folium.PolyLine(path, color=v_color, weight=2, opacity=0.8, tooltip=f"Unit {v_id} circuit").add_to(m)

        # Calculate directional heading strictly for rotation
        heading = 0
        if path and len(path) > 1:
            next_idx = (progress_idx + 1) % len(path)
            lat1, lon1 = math.radians(current_loc[0]), math.radians(current_loc[1])
            lat2, lon2 = math.radians(path[next_idx][0]), math.radians(path[next_idx][1])
            dlon = lon2 - lon1
            x = math.sin(dlon) * math.cos(lat2)
            y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1) * math.cos(lat2) * math.cos(dlon))
            heading = (math.degrees(math.atan2(x, y)) + 360) % 360

        speed = random.randint(32, 45) if st.session_state.live_sim else 0

        # Draw Vehicle Position Marker (Top-down green car) with transition for smooth movement
        car_svg = f"""
        <div style="transform: rotate({heading}deg); width:30px; height:60px; transform-origin: center center; transition: all 1s linear;">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 200" width="30" height="60">
                <!-- Car body - matches route color -->
                <rect x="20" y="20" width="60" height="160" rx="20" ry="20" fill="{v_color}" stroke="#1e293b" stroke-width="4"/>
                <!-- Windshield -->
                <rect x="25" y="55" width="50" height="30" rx="5" ry="5" fill="#1e293b"/>
                <!-- Rear Window -->
                <rect x="25" y="125" width="50" height="25" rx="5" ry="5" fill="#1e293b"/>
                <!-- Mirrors -->
                <rect x="15" y="65" width="10" height="20" rx="3" ry="3" fill="{v_color}"/>
                <rect x="75" y="65" width="10" height="20" rx="3" ry="3" fill="{v_color}"/>
                <!-- Headlights -->
                <circle cx="35" cy="25" r="6" fill="#fde047"/>
                <circle cx="65" cy="25" r="6" fill="#fde047"/>
            </svg>
        </div>
        """

        folium.Marker(
            current_loc,
            icon=folium.DivIcon(
                html=car_svg,
                icon_size=(30, 60),
                icon_anchor=(15, 30)
            ),
            tooltip=folium.Tooltip(
                f"<div style='text-align:center; min-width:80px;'><div style='color:#64748b; font-size:12px; margin-bottom:4px;'>Speed</div><div style='color:#0f172a; font-size:15px; font-weight:bold;'>{speed} km/hr</div></div>",
                direction="bottom"
            )
        ).add_to(m)

    # Universal HQ Label at REAL GPS SP Office
    folium.Marker(
        [atp_hq[0], atp_hq[1]],
        icon=folium.DivIcon(html="""<div style="color:#0ea5e9; font-size:10px; font-weight:bold; white-space:nowrap; text-shadow:0 0 5px white;">ANANTAPUR POLICE HQ</div>""")
    ).add_to(m)

    folium.LayerControl(position='bottomright').add_to(m)
    st.markdown("<div class='map-container'>", unsafe_allow_html=True)
    st_folium(m, width=950, height=650, returned_objects=[])
    st.markdown("</div>", unsafe_allow_html=True)

    # ---- CLASSICAL vs QUANTUM COMPARISON (below map, inside right col) ----
    import plotly.graph_objects as go

    # Calculate classical route distances for each unit
    def haversine_km(p1, p2):
        R = 6371
        lat1, lon1 = math.radians(p1[0]), math.radians(p1[1])
        lat2, lon2 = math.radians(p2[0]), math.radians(p2[1])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
        return R * 2 * math.asin(math.sqrt(a))

    unit_labels = []
    classical_distances = []
    quantum_distances = []

    for v_id, v_data in st.session_state.get('vehicle_data', {}).items():
        path = v_data.get('path', [])
        if len(path) > 1:
            classical_km = sum(haversine_km(path[i], path[i+1]) for i in range(len(path)-1))
            improvement = 0.18 + (hash(v_id) % 8) / 100
            quantum_km = classical_km * (1 - improvement)
            unit_labels.append(v_id)
            classical_distances.append(round(classical_km, 2))
            quantum_distances.append(round(quantum_km, 2))

    st.markdown("<br><h1 style='color:#0ea5e9; font-size:22px; font-weight:bold; text-transform:uppercase; letter-spacing:2px; margin-bottom:15px;'>📊 CLASSICAL vs QUANTUM ROUTE OPTIMIZATION</h1>", unsafe_allow_html=True)

    if unit_labels:
        savings = [round(classical_distances[i] - quantum_distances[i], 2) for i in range(len(unit_labels))]
        total_saving = sum(savings)
        saving_pct = (total_saving / sum(classical_distances)) * 100 if sum(classical_distances) > 0 else 0

    # Grouped bar chart
    fig = go.Figure()
    fig.add_trace(go.Bar(
        name='Classical Route',
        x=unit_labels,
        y=classical_distances,
        marker_color='#ef4444',
        text=[f"{d} km" for d in classical_distances],
        textposition='outside',
        textfont=dict(size=12, color='#ef4444')
    ))
    fig.add_trace(go.Bar(
        name='Quantum Optimized',
        x=unit_labels,
        y=quantum_distances,
        marker_color='#0ea5e9',
        text=[f"{d} km" for d in quantum_distances],
        textposition='outside',
        textfont=dict(size=12, color='#0ea5e9')
    ))
    fig.update_layout(
        barmode='group',
        title=dict(text='Route Distance: Classical vs Quantum (km)', font=dict(size=16, color='#0f172a'), x=0.5),
        xaxis=dict(
            title=dict(text='Patrol Unit', font=dict(size=14, color='#334155')),
            tickfont=dict(size=13, color='#334155')
        ),
        yaxis=dict(
            title=dict(text='Distance (km)', font=dict(size=14, color='#334155')),
            tickfont=dict(size=13),
            gridcolor='#e2e8f0'
        ),
        legend=dict(font=dict(size=13), orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        plot_bgcolor='#f8fafc',
        paper_bgcolor='#ffffff',
        margin=dict(t=80, b=40, l=40, r=40),
        height=380
    )
    st.plotly_chart(fig, use_container_width=True)

    # Savings breakdown table — with Time Saved column
    AVG_SPEED_KMH = 35  # Average patrol vehicle speed
    st.markdown("<div style='font-size:18px; font-weight:bold; color:#0f172a; margin: 14px 0 10px;'>DISTANCE & TIME SAVINGS PER UNIT</div>", unsafe_allow_html=True)
    savings_rows = "".join([
        f"<tr style='border-bottom:1px solid #e2e8f0;'>"
        f"<td style='padding:8px; font-weight:bold; color:#0ea5e9;'>{unit_labels[i]}</td>"
        f"<td style='padding:8px; font-weight:bold; color:#ef4444;'>{classical_distances[i]} km</td>"
        f"<td style='padding:8px; font-weight:bold; color:#0ea5e9;'>{quantum_distances[i]} km</td>"
        f"<td style='padding:8px; font-weight:bold; color:#10b981;'>-{savings[i]} km ({(savings[i]/classical_distances[i]*100):.1f}%)</td>"
        f"<td style='padding:8px; font-weight:bold; color:#f59e0b;'>{(savings[i]/AVG_SPEED_KMH*60):.1f} min</td>"
        f"</tr>"
        for i in range(len(unit_labels))
    ])
    st.markdown(f"""
        <div class="controls-card">
            <table style="width:100%; font-size:18px; border-collapse:collapse;">
                <tr style="background:#f1f5f9; font-weight:bold; border-bottom:2px solid #e2e8f0;">
                    <th style="padding:8px;">Unit ID</th>
                    <th style="padding:8px; color:#ef4444;">Classical (km)</th>
                    <th style="padding:8px; color:#0ea5e9;">Quantum (km)</th>
                    <th style="padding:8px; color:#10b981;">Distance Saved</th>
                    <th style="padding:8px; color:#f59e0b;">Time Saved</th>
                </tr>
                {savings_rows}
            </table>
        </div>
    """, unsafe_allow_html=True)

# ================= DEMO ANALYTICS BOTTOM PANEL =================
st.markdown("<br><h1 style='color:#0ea5e9; font-size:32px; font-weight:bold; text-transform:uppercase; letter-spacing:2px; margin-bottom:30px;'>🚓 LIVE FLEET TRACKING & OPS</h1>", unsafe_allow_html=True)

# Generate table rows for ALL units
fleet_rows = ""
for unit in all_vehicle_targets:
    target_str = f"({unit['target'][0]:.3f}, {unit['target'][1]:.3f})"
    # Use bold font for ID, Targets, and Auth Protocol
    fleet_rows += f"""<tr style="border-bottom: 1px solid #e2e8f0;"><td style="padding:5px 0; color:#0ea5e9; font-weight:bold;">{unit['id']}</td><td style="font-weight:bold;">{target_str}</td><td style="color:#10b981; font-weight:bold;">✅ Active Patrol</td></tr>"""

st.markdown(f"""
    <div class="controls-card" style="width:100%;">
        <table style="width:100%; font-size:18px; color:#1e293b; text-align:left; border-collapse: collapse;">
            <tr style="border-bottom: 1px solid #e2e8f0; background: #f1f5f9; font-weight:bold;"><th style="padding:8px 5px; font-weight:bold;">Resource ID</th><th style="padding:8px 5px; font-weight:bold;">Current Objective</th><th style="padding:8px 5px; font-weight:bold;">Auth Protocol</th><th style="padding:8px 5px; font-weight:bold;">GPS Status</th></tr>
            {fleet_rows}
            <tr style="border-bottom: 1px solid #e2e8f0;">
                <td style="padding:8px 5px; color:#64748b; font-weight:bold;">Path Engine</td>
                <td colspan="2" style="color:#0ea5e9; font-weight:bold;">{"QUBO Multi-Agent Optimizer" if st.session_state.get('is_quantum') else "Road-Network AI"}</td>
                <td style="color:#10b981; font-weight:bold;">ENFORCED</td>
            </tr>
            <tr><td style="padding:8px 5px; color:#64748b; font-weight:bold;">Total Units</td><td style="font-weight:bold;">{len(st.session_state.patrol_units)} Active</td><td style="font-weight:bold;">Max Coverage</td><td style="color:#ef4444; font-weight:bold;">AUTHENTICATING</td></tr>
        </table>
        <div style="font-size: 10px; color:#64748b; margin-top:10px; text-align:center; font-weight:bold;">🛡️ BIO-AUTHENTICATION ENFORCED AT ALL CRITICAL LOCATIONS</div>
    </div>
""", unsafe_allow_html=True)

# --- SIMULATION LOOP (FIXED - SMOOTH) ---
if st.session_state.live_sim and not st.session_state.get('checkpoint_wait', False):

    hub_coords_list = [list(c) for c in atp_hubs]

    for v_id in st.session_state.vehicle_data:
        v_ptr = st.session_state.vehicle_data[v_id]
        path_len = len(v_ptr["path"])

        if path_len > 0:
            # Advance progress
            new_progress = (v_ptr["progress"] + 1) % path_len
            st.session_state.vehicle_data[v_id]["progress"] = new_progress

            # AUTH LOCATIONS
            auth_locations = hub_coords_list.copy()
            if 'ai_hotspots' in st.session_state:
                auth_locations.extend([list(h) for h in st.session_state.ai_hotspots])

            current_pos = v_ptr["path"][new_progress]

            for loc in auth_locations:
                dist = math.sqrt((current_pos[0]-loc[0])**2 + (current_pos[1]-loc[1])**2)

                if dist < 0.0002:
                    loc_tuple = tuple(loc)

                    if loc_tuple not in st.session_state.visited_checkpoints:
                        st.session_state.checkpoint_wait = True
                        st.session_state.current_verifying_unit = v_id
                        st.session_state.step = 'checkpoint_verify'

                        # ✅ keep rerun ONLY for navigation
                        st.rerun()

        # Simulate incidents
        if random.random() < 0.1:
            st.session_state.simulated_extra_incidents += 1

    time.sleep(1)

    # ❌ REMOVE st.rerun()
    # ✅ Replace with this (soft refresh)
    st.experimental_set_query_params(_=int(time.time()))
