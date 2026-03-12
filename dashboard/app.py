"""
TrafficVision AI - Streamlit Dashboard
Dynamic AI Traffic Flow Optimizer & Emergency Grid
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import time
import random
import math
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from collections import deque

# ─── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="TrafficVision AI",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Space+Grotesk:wght@300;400;600;700&display=swap');

* { font-family: 'Space Grotesk', sans-serif; }

.stApp {
    background: #0a0e1a;
    color: #e0e6f0;
}

.main .block-container {
    padding: 1rem 1.5rem;
    max-width: 1600px;
}

/* Header */
.traffic-header {
    background: linear-gradient(135deg, #0d1b2a 0%, #1a2744 50%, #0d1b2a 100%);
    border: 1px solid #1e3a5f;
    border-radius: 12px;
    padding: 1.2rem 2rem;
    margin-bottom: 1.2rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 4px 24px rgba(0,80,200,0.15);
}

.header-title {
    font-size: 1.8rem;
    font-weight: 700;
    color: #60a5fa;
    letter-spacing: -0.5px;
}

.header-subtitle {
    font-size: 0.8rem;
    color: #64748b;
    letter-spacing: 2px;
    text-transform: uppercase;
}

.live-badge {
    background: #ef4444;
    color: white;
    padding: 0.3rem 0.8rem;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 1px;
    animation: pulse 1.5s infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.6; }
}

/* Signal cards */
.signal-card {
    background: #0f1c2e;
    border: 1px solid #1e3a5f;
    border-radius: 10px;
    padding: 1rem;
    text-align: center;
    position: relative;
    overflow: hidden;
    transition: all 0.3s ease;
}

.signal-card:hover {
    border-color: #3b82f6;
    box-shadow: 0 0 20px rgba(59,130,246,0.15);
}

.signal-green {
    border-color: #22c55e !important;
    box-shadow: 0 0 20px rgba(34,197,94,0.2) !important;
}

.signal-yellow {
    border-color: #f59e0b !important;
    box-shadow: 0 0 20px rgba(245,158,11,0.2) !important;
}

.signal-emergency {
    border-color: #ef4444 !important;
    box-shadow: 0 0 30px rgba(239,68,68,0.4) !important;
    animation: emergency-pulse 0.8s infinite;
}

@keyframes emergency-pulse {
    0%, 100% { box-shadow: 0 0 20px rgba(239,68,68,0.4); }
    50% { box-shadow: 0 0 50px rgba(239,68,68,0.8); }
}

.signal-dot {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    margin: 0 auto 0.5rem;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.2rem;
}

.dot-green { background: #22c55e; box-shadow: 0 0 12px #22c55e; }
.dot-yellow { background: #f59e0b; box-shadow: 0 0 12px #f59e0b; }
.dot-red { background: #ef4444; box-shadow: 0 0 12px #ef4444; }
.dot-emergency { background: #ef4444; box-shadow: 0 0 20px #ef4444; animation: emergency-pulse 0.8s infinite; }

.lane-label { font-size: 0.9rem; color: #94a3b8; font-weight: 600; }
.signal-state { font-size: 0.75rem; font-weight: 700; letter-spacing: 1px; margin: 0.2rem 0; }
.state-green { color: #22c55e; }
.state-yellow { color: #f59e0b; }
.state-red { color: #ef4444; }
.state-emergency { color: #ff6b6b; }

.countdown { font-family: 'JetBrains Mono', monospace; font-size: 1.4rem; font-weight: 700; color: #60a5fa; }
.density-bar-bg { background: #1e3a5f; border-radius: 4px; height: 6px; margin-top: 0.5rem; }
.density-bar { border-radius: 4px; height: 6px; transition: width 0.5s ease; }
.congestion-badge {
    display: inline-block;
    padding: 0.15rem 0.5rem;
    border-radius: 4px;
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 1px;
    margin-top: 0.3rem;
}
.badge-low { background: rgba(34,197,94,0.2); color: #22c55e; }
.badge-medium { background: rgba(234,179,8,0.2); color: #eab308; }
.badge-high { background: rgba(249,115,22,0.2); color: #f97316; }
.badge-critical { background: rgba(239,68,68,0.2); color: #ef4444; }

/* Emergency banner */
.emergency-banner {
    background: linear-gradient(135deg, #450a0a, #7f1d1d);
    border: 2px solid #ef4444;
    border-radius: 10px;
    padding: 1rem 1.5rem;
    margin-bottom: 1rem;
    animation: emergency-pulse 1s infinite;
    display: flex;
    align-items: center;
    gap: 1rem;
}

.emergency-text {
    font-size: 1.1rem;
    font-weight: 700;
    color: #fca5a5;
}

.emergency-detail {
    font-size: 0.8rem;
    color: #f87171;
    margin-top: 0.2rem;
}

/* Metrics */
.metric-card {
    background: #0f1c2e;
    border: 1px solid #1e3a5f;
    border-radius: 10px;
    padding: 1rem;
    text-align: center;
}

.metric-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.8rem;
    font-weight: 700;
    color: #60a5fa;
}

.metric-label {
    font-size: 0.7rem;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-top: 0.2rem;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #0a0e1a !important;
    border-right: 1px solid #1e3a5f;
}

.sidebar-section {
    background: #0f1c2e;
    border: 1px solid #1e3a5f;
    border-radius: 8px;
    padding: 0.8rem;
    margin-bottom: 0.8rem;
}

.sidebar-title {
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: #3b82f6;
    font-weight: 700;
    margin-bottom: 0.6rem;
}

/* Timeline log */
.log-entry {
    background: #0f1c2e;
    border-left: 3px solid #1e3a5f;
    padding: 0.4rem 0.6rem;
    margin-bottom: 0.3rem;
    border-radius: 0 6px 6px 0;
    font-size: 0.75rem;
    font-family: 'JetBrains Mono', monospace;
}

.log-emergency { border-left-color: #ef4444; color: #fca5a5; }
.log-normal { border-left-color: #3b82f6; color: #93c5fd; }
.log-info { border-left-color: #22c55e; color: #86efac; }

/* Streamlit overrides */
.stButton > button {
    background: #1e3a5f;
    color: #60a5fa;
    border: 1px solid #3b82f6;
    border-radius: 8px;
    font-weight: 600;
    width: 100%;
    transition: all 0.2s;
}

.stButton > button:hover {
    background: #3b82f6;
    color: white;
    border-color: #60a5fa;
}

.stSelectbox > div > div {
    background: #0f1c2e !important;
    border-color: #1e3a5f !important;
    color: #e0e6f0 !important;
}

div[data-testid="stMetric"] {
    background: #0f1c2e;
    border: 1px solid #1e3a5f;
    border-radius: 8px;
    padding: 0.6rem 1rem;
}

div[data-testid="stMetric"] label { color: #64748b !important; }
div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    color: #60a5fa !important;
    font-family: 'JetBrains Mono', monospace !important;
}

div[data-testid="stMetric"] [data-testid="stMetricDelta"] {
    font-size: 0.75rem !important;
}

h1, h2, h3 { color: #e0e6f0 !important; }
</style>
""", unsafe_allow_html=True)


# ─── State Initialization ────────────────────────────────────────────────────
def init_state():
    if "initialized" in st.session_state:
        return

    st.session_state.initialized = True
    st.session_state.frame_count = 0
    st.session_state.tick = 0
    st.session_state.start_time = time.time()

    # Signal states per lane
    st.session_state.num_lanes = 4
    st.session_state.active_green_lane = 0
    st.session_state.in_yellow = False
    st.session_state.green_remaining = 20.0
    st.session_state.yellow_remaining = 0.0
    st.session_state.signal_states = ["GREEN", "RED", "RED", "RED"]
    st.session_state.cycles_since_green = [0, 1, 1, 1]
    st.session_state.vehicles_served = [0, 0, 0, 0]

    # Traffic densities
    st.session_state.densities = [8.0, 4.0, 22.0, 12.0]
    st.session_state.vehicle_counts = [8, 4, 22, 12]
    st.session_state.congestion_levels = ["MEDIUM", "LOW", "CRITICAL", "HIGH"]

    # Emergency state
    st.session_state.emergency_active = False
    st.session_state.emergency_lane = None
    st.session_state.emergency_type = "ambulance"
    st.session_state.emergency_hold_remaining = 0.0
    st.session_state.corridor_events = []

    # History buffers
    st.session_state.density_history = {i: deque(maxlen=60) for i in range(4)}
    st.session_state.signal_history = []
    st.session_state.event_log = []

    # Settings
    st.session_state.scenario = "Normal Flow"
    st.session_state.update_interval = 1.0
    st.session_state.last_update = time.time()
    st.session_state.total_vehicles_served = 0
    st.session_state.cycle_number = 0

    # Pre-populate history
    for i in range(30):
        for lane in range(4):
            base = [8, 4, 22, 12][lane]
            st.session_state.density_history[lane].append(
                max(0, base + random.gauss(0, 2))
            )

    _add_log("✅ System initialized", "info")


def _add_log(msg: str, level: str = "normal"):
    ts = datetime.now().strftime("%H:%M:%S")
    entry = {"time": ts, "msg": msg, "level": level}
    if "event_log" in st.session_state:
        st.session_state.event_log.insert(0, entry)
        if len(st.session_state.event_log) > 50:
            st.session_state.event_log.pop()


# ─── Signal Timing Logic ─────────────────────────────────────────────────────
TIMING_TABLE = [(5, 10), (15, 20), (30, 35), (50, 45), (float("inf"), 60)]
MIN_GREEN = 8.0
MAX_GREEN = 60.0
YELLOW_DUR = 3.0
FAIRNESS_CYCLES = 3
FAIRNESS_BONUS = 8.0


def calc_green_time(density: float, cycles_waiting: int) -> float:
    base = 10.0
    for thresh, g in TIMING_TABLE:
        if density <= thresh:
            base = g
            break
    starvation = max(0, cycles_waiting - FAIRNESS_CYCLES) * FAIRNESS_BONUS
    return min(MAX_GREEN, max(MIN_GREEN, base + starvation))


def get_congestion(density: float) -> str:
    if density < 5:
        return "LOW"
    elif density < 15:
        return "MEDIUM"
    elif density < 30:
        return "HIGH"
    return "CRITICAL"


def select_next_lane(current_lane: int, densities: list, cycles: list, num_lanes: int) -> int:
    best_lane = (current_lane + 1) % num_lanes
    best_score = -1
    for i in range(num_lanes):
        if i == current_lane:
            continue
        score = densities[i] + cycles[i] * 5.0
        if score > best_score:
            best_score = score
            best_lane = i
    return best_lane


def update_simulation():
    """Core simulation tick — update densities, signals, emergency."""
    now = time.time()
    dt = now - st.session_state.last_update
    if dt < st.session_state.update_interval:
        return False

    st.session_state.last_update = now
    st.session_state.tick += 1
    st.session_state.frame_count += 1

    # Update densities based on scenario
    scenario = st.session_state.scenario
    for i in range(4):
        if scenario == "Morning Rush Hour":
            target = 28.0 if i in (0, 1) else 8.0
        elif scenario == "Evening Rush Hour":
            target = 26.0 if i in (2, 3) else 7.0
        elif scenario == "Light Traffic":
            target = random.uniform(2, 6)
        elif scenario == "Traffic Incident":
            target = 38.0 if i == 1 else 10.0
        elif scenario == "Emergency Vehicle":
            target = [15, 5, 20, 10][i]
        else:
            target = [10, 5, 18, 12][i]

        delta = random.gauss(0, 1.2)
        d = st.session_state.densities[i]
        d += (target - d) * 0.1 + delta
        d = max(0.0, min(50.0, d))
        st.session_state.densities[i] = round(d, 1)
        st.session_state.vehicle_counts[i] = max(0, int(d * random.uniform(0.8, 1.2)))
        st.session_state.congestion_levels[i] = get_congestion(d)
        st.session_state.density_history[i].append(d)

    # Signal timing
    if st.session_state.emergency_active:
        # Keep emergency lane green
        for i in range(4):
            if i == st.session_state.emergency_lane:
                st.session_state.signal_states[i] = "EMERGENCY"
            else:
                st.session_state.signal_states[i] = "RED"
        st.session_state.emergency_hold_remaining = max(0, st.session_state.emergency_hold_remaining - dt)
        if st.session_state.emergency_hold_remaining <= 0:
            _clear_emergency()
    else:
        if st.session_state.in_yellow:
            st.session_state.yellow_remaining = max(0, st.session_state.yellow_remaining - dt)
            if st.session_state.yellow_remaining <= 0:
                st.session_state.in_yellow = False
                _advance_signal()
        else:
            st.session_state.green_remaining = max(0, st.session_state.green_remaining - dt)
            if st.session_state.green_remaining <= 0:
                st.session_state.in_yellow = True
                st.session_state.yellow_remaining = YELLOW_DUR
                lane = st.session_state.active_green_lane
                st.session_state.signal_states[lane] = "YELLOW"

    # Random emergency in Emergency scenario
    if scenario == "Emergency Vehicle" and not st.session_state.emergency_active:
        if random.random() < 0.02:
            _trigger_emergency(random.randint(0, 3), "ambulance")

    return True


def _advance_signal():
    """Move to next optimal lane."""
    prev = st.session_state.active_green_lane
    st.session_state.signal_states[prev] = "RED"
    st.session_state.vehicles_served[prev] += int(st.session_state.densities[prev])
    st.session_state.total_vehicles_served += int(st.session_state.densities[prev])
    st.session_state.cycle_number += 1

    for i in range(4):
        if i != prev:
            st.session_state.cycles_since_green[i] += 1

    next_lane = select_next_lane(
        prev,
        st.session_state.densities,
        st.session_state.cycles_since_green,
        4
    )

    density = st.session_state.densities[next_lane]
    green_t = calc_green_time(density, st.session_state.cycles_since_green[next_lane])
    st.session_state.active_green_lane = next_lane
    st.session_state.signal_states[next_lane] = "GREEN"
    st.session_state.green_remaining = green_t
    st.session_state.cycles_since_green[next_lane] = 0

    _add_log(f"→ Lane {next_lane + 1} GREEN ({green_t:.0f}s) | density={density:.1f}", "normal")


def _trigger_emergency(lane: int, etype: str = "ambulance"):
    st.session_state.emergency_active = True
    st.session_state.emergency_lane = lane
    st.session_state.emergency_type = etype
    st.session_state.emergency_hold_remaining = 20.0
    for i in range(4):
        st.session_state.signal_states[i] = "EMERGENCY" if i == lane else "RED"
    event = {
        "id": f"EMG-{len(st.session_state.corridor_events) + 1:04d}",
        "type": etype,
        "lane": lane + 1,
        "time": datetime.now().strftime("%H:%M:%S"),
        "duration": 20.0,
    }
    st.session_state.corridor_events.insert(0, event)
    _add_log(f"🚨 EMERGENCY: {etype.upper()} detected on Lane {lane + 1}", "emergency")


def _clear_emergency():
    st.session_state.emergency_active = False
    lane = st.session_state.emergency_lane
    st.session_state.emergency_lane = None
    _add_log(f"✅ Emergency corridor cleared (Lane {lane + 1 if lane is not None else '?'})", "info")
    # Resume normal
    st.session_state.signal_states = ["RED"] * 4
    density = st.session_state.densities[0]
    green_t = calc_green_time(density, 0)
    st.session_state.active_green_lane = 0
    st.session_state.signal_states[0] = "GREEN"
    st.session_state.green_remaining = green_t


# ─── Render Helpers ──────────────────────────────────────────────────────────
LANE_NAMES = ["Lane 1 (North)", "Lane 2 (South)", "Lane 3 (East)", "Lane 4 (West)"]
LANE_ICONS = ["⬆️", "⬇️", "➡️", "⬅️"]

CONGESTION_COLORS = {
    "LOW":      ("#22c55e", "#166534", "badge-low"),
    "MEDIUM":   ("#eab308", "#713f12", "badge-medium"),
    "HIGH":     ("#f97316", "#7c2d12", "badge-high"),
    "CRITICAL": ("#ef4444", "#7f1d1d", "badge-critical"),
}

def density_pct(d): return min(100, int(d / 50 * 100))
def density_color(d):
    if d < 5: return "#22c55e"
    if d < 15: return "#eab308"
    if d < 30: return "#f97316"
    return "#ef4444"


def render_signal_card(i: int):
    state = st.session_state.signal_states[i]
    density = st.session_state.densities[i]
    congestion = st.session_state.congestion_levels[i]
    is_active = (state in ("GREEN", "YELLOW", "EMERGENCY"))
    is_emg = (state == "EMERGENCY")
    count = st.session_state.vehicle_counts[i]

    if is_emg:
        card_class = "signal-card signal-emergency"
        dot_class = "signal-dot dot-emergency"
        state_class = "signal-state state-emergency"
        state_display = "🚨 EMERGENCY"
        dot_icon = "🚑"
    elif state == "GREEN":
        card_class = "signal-card signal-green"
        dot_class = "signal-dot dot-green"
        state_class = "signal-state state-green"
        state_display = "● GREEN"
        dot_icon = "🟢"
    elif state == "YELLOW":
        card_class = "signal-card signal-yellow"
        dot_class = "signal-dot dot-yellow"
        state_class = "signal-state state-yellow"
        state_display = "● YELLOW"
        dot_icon = "🟡"
    else:
        card_class = "signal-card"
        dot_class = "signal-dot dot-red"
        state_class = "signal-state state-red"
        state_display = "● RED"
        dot_icon = "🔴"

    # Countdown
    if is_emg:
        remaining = st.session_state.emergency_hold_remaining
        countdown_html = f'<div class="countdown">{remaining:.0f}s</div>'
    elif state == "GREEN":
        remaining = st.session_state.green_remaining
        countdown_html = f'<div class="countdown">{remaining:.0f}s</div>'
    elif state == "YELLOW":
        remaining = st.session_state.yellow_remaining
        countdown_html = f'<div class="countdown" style="color:#f59e0b">{remaining:.1f}s</div>'
    else:
        countdown_html = '<div class="countdown" style="color:#475569">—</div>'

    # Density bar
    pct = density_pct(density)
    bar_color = density_color(density)
    color_info = CONGESTION_COLORS.get(congestion, CONGESTION_COLORS["LOW"])
    badge_class = color_info[2]
    badge_color = color_info[0]

    # Recommended green time
    rec_green = calc_green_time(density, st.session_state.cycles_since_green[i])

    html = f"""
    <div class="{card_class}">
        <div class="lane-label">{LANE_ICONS[i]} {LANE_NAMES[i]}</div>
        <div class="{dot_class}">{dot_icon}</div>
        <div class="{state_class}">{state_display}</div>
        {countdown_html}
        <div style="margin: 0.4rem 0; font-size: 0.75rem; color: #94a3b8;">
            🚗 {count} vehicles
        </div>
        <div class="density-bar-bg">
            <div class="density-bar" style="width:{pct}%; background:{bar_color};"></div>
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 0.4rem;">
            <span class="congestion-badge {badge_class}">{congestion}</span>
            <span style="font-size: 0.7rem; color: #475569; font-family: 'JetBrains Mono', monospace;">
                AI: {rec_green:.0f}s
            </span>
        </div>
        <div style="font-size: 0.65rem; color: #334155; margin-top: 0.3rem; font-family: 'JetBrains Mono', monospace;">
            density: {density:.1f} | wait: {st.session_state.cycles_since_green[i]} cycles
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_intersection_viz():
    """Render an SVG intersection diagram via st.components for reliable rendering."""
    import streamlit.components.v1 as components

    states = st.session_state.signal_states
    emg_active = st.session_state.emergency_active

    def sig_color(i):
        s = states[i]
        if s == "EMERGENCY": return "#ef4444"
        if s == "GREEN": return "#22c55e"
        if s == "YELLOW": return "#f59e0b"
        return "#2d3f55"

    def sig_glow(i):
        s = states[i]
        if s == "EMERGENCY": return "drop-shadow(0 0 10px #ef4444)"
        if s == "GREEN": return "drop-shadow(0 0 10px #22c55e)"
        if s == "YELLOW": return "drop-shadow(0 0 10px #f59e0b)"
        return "none"

    def sig_label(i):
        s = states[i]
        if s == "GREEN": return "GO"
        if s == "YELLOW": return "YLW"
        if s == "EMERGENCY": return "EMG"
        return "STOP"

    densities = st.session_state.densities

    def road_opacity(d): return min(0.85, 0.15 + d / 50 * 0.7)
    def road_color(d):
        if d < 5:   return "#22c55e"
        if d < 15:  return "#eab308"
        if d < 30:  return "#f97316"
        return "#ef4444"

    emg_html = ""
    if emg_active:
        emg_html = '<text x="200" y="205" text-anchor="middle" font-size="28">🚑</text>'

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
      body {{ margin: 0; padding: 0; background: #0a0e1a; display: flex; justify-content: center; }}
      svg {{ display: block; width: 100%; max-width: 380px; }}
    </style>
    </head>
    <body>
    <svg viewBox="0 0 400 400" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
          <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#1e3a5f" stroke-width="0.5"/>
        </pattern>
        <filter id="glow0"><feDropShadow dx="0" dy="0" stdDeviation="4" flood-color="{sig_color(0)}" flood-opacity="0.9"/></filter>
        <filter id="glow1"><feDropShadow dx="0" dy="0" stdDeviation="4" flood-color="{sig_color(1)}" flood-opacity="0.9"/></filter>
        <filter id="glow2"><feDropShadow dx="0" dy="0" stdDeviation="4" flood-color="{sig_color(2)}" flood-opacity="0.9"/></filter>
        <filter id="glow3"><feDropShadow dx="0" dy="0" stdDeviation="4" flood-color="{sig_color(3)}" flood-opacity="0.9"/></filter>
      </defs>

      <!-- Background -->
      <rect width="400" height="400" fill="#0a0e1a"/>
      <rect width="400" height="400" fill="url(#grid)" opacity="0.5"/>

      <!-- Road bodies -->
      <!-- East arm -->
      <rect x="0" y="150" width="155" height="100" fill="{road_color(densities[2])}" opacity="{road_opacity(densities[2])}"/>
      <!-- West arm -->
      <rect x="245" y="150" width="155" height="100" fill="{road_color(densities[3])}" opacity="{road_opacity(densities[3])}"/>
      <!-- North arm -->
      <rect x="150" y="0" width="100" height="155" fill="{road_color(densities[0])}" opacity="{road_opacity(densities[0])}"/>
      <!-- South arm -->
      <rect x="150" y="245" width="100" height="155" fill="{road_color(densities[1])}" opacity="{road_opacity(densities[1])}"/>

      <!-- Road edges -->
      <rect x="0" y="150" width="155" height="100" fill="none" stroke="#1e3a5f" stroke-width="1"/>
      <rect x="245" y="150" width="155" height="100" fill="none" stroke="#1e3a5f" stroke-width="1"/>
      <rect x="150" y="0" width="100" height="155" fill="none" stroke="#1e3a5f" stroke-width="1"/>
      <rect x="150" y="245" width="100" height="155" fill="none" stroke="#1e3a5f" stroke-width="1"/>

      <!-- Intersection box -->
      <rect x="150" y="150" width="100" height="100" fill="#111827" stroke="#2d4a7a" stroke-width="1.5"/>
      <line x1="150" y1="150" x2="250" y2="250" stroke="#1e3a5f" stroke-width="1" stroke-dasharray="5,5"/>
      <line x1="250" y1="150" x2="150" y2="250" stroke="#1e3a5f" stroke-width="1" stroke-dasharray="5,5"/>

      <!-- Center lane markings -->
      <line x1="0" y1="200" x2="150" y2="200" stroke="#475569" stroke-width="1.5" stroke-dasharray="14,10"/>
      <line x1="250" y1="200" x2="400" y2="200" stroke="#475569" stroke-width="1.5" stroke-dasharray="14,10"/>
      <line x1="200" y1="0" x2="200" y2="150" stroke="#475569" stroke-width="1.5" stroke-dasharray="14,10"/>
      <line x1="200" y1="250" x2="200" y2="400" stroke="#475569" stroke-width="1.5" stroke-dasharray="14,10"/>

      <!-- Direction arrows -->
      <!-- East → right -->
      <polygon points="130,196 118,190 118,202" fill="#475569" opacity="0.7"/>
      <!-- West ← left -->
      <polygon points="270,204 282,198 282,210" fill="#475569" opacity="0.7"/>
      <!-- North ↑ up -->
      <polygon points="196,130 190,142 202,142" fill="#475569" opacity="0.7"/>
      <!-- South ↓ down -->
      <polygon points="204,270 198,258 210,258" fill="#475569" opacity="0.7"/>

      <!-- Signal boxes (traffic light housings) -->
      <!-- North signal -->
      <rect x="162" y="124" width="30" height="22" rx="4" fill="#0f1c2e" stroke="{sig_color(0)}" stroke-width="1.5"/>
      <circle cx="177" cy="135" r="7" fill="{sig_color(0)}" filter="url(#glow0)"/>
      <text x="177" y="139" text-anchor="middle" fill="white" font-size="5" font-weight="bold" font-family="monospace">{sig_label(0)}</text>
      <text x="177" y="118" text-anchor="middle" fill="#64748b" font-size="9" font-family="sans-serif">N ⬆</text>

      <!-- South signal -->
      <rect x="208" y="254" width="30" height="22" rx="4" fill="#0f1c2e" stroke="{sig_color(1)}" stroke-width="1.5"/>
      <circle cx="223" cy="265" r="7" fill="{sig_color(1)}" filter="url(#glow1)"/>
      <text x="223" y="269" text-anchor="middle" fill="white" font-size="5" font-weight="bold" font-family="monospace">{sig_label(1)}</text>
      <text x="223" y="288" text-anchor="middle" fill="#64748b" font-size="9" font-family="sans-serif">⬇ S</text>

      <!-- East signal -->
      <rect x="122" y="163" width="22" height="30" rx="4" fill="#0f1c2e" stroke="{sig_color(2)}" stroke-width="1.5"/>
      <circle cx="133" cy="178" r="7" fill="{sig_color(2)}" filter="url(#glow2)"/>
      <text x="133" y="182" text-anchor="middle" fill="white" font-size="5" font-weight="bold" font-family="monospace">{sig_label(2)}</text>
      <text x="108" y="182" text-anchor="middle" fill="#64748b" font-size="9" font-family="sans-serif">E➡</text>

      <!-- West signal -->
      <rect x="256" y="207" width="22" height="30" rx="4" fill="#0f1c2e" stroke="{sig_color(3)}" stroke-width="1.5"/>
      <circle cx="267" cy="222" r="7" fill="{sig_color(3)}" filter="url(#glow3)"/>
      <text x="267" y="226" text-anchor="middle" fill="white" font-size="5" font-weight="bold" font-family="monospace">{sig_label(3)}</text>
      <text x="292" y="226" text-anchor="middle" fill="#64748b" font-size="9" font-family="sans-serif">⬅W</text>

      <!-- Density labels on roads -->
      <text x="77" y="190" text-anchor="middle" fill="#60a5fa" font-size="11" font-family="monospace" font-weight="bold">{densities[2]:.0f}</text>
      <text x="77" y="204" text-anchor="middle" fill="#60a5fa" font-size="8" font-family="monospace" opacity="0.6">density</text>
      <text x="323" y="194" text-anchor="middle" fill="#60a5fa" font-size="11" font-family="monospace" font-weight="bold">{densities[3]:.0f}</text>
      <text x="323" y="208" text-anchor="middle" fill="#60a5fa" font-size="8" font-family="monospace" opacity="0.6">density</text>
      <text x="200" y="70" text-anchor="middle" fill="#60a5fa" font-size="11" font-family="monospace" font-weight="bold">{densities[0]:.0f}</text>
      <text x="200" y="84" text-anchor="middle" fill="#60a5fa" font-size="8" font-family="monospace" opacity="0.6">density</text>
      <text x="200" y="334" text-anchor="middle" fill="#60a5fa" font-size="11" font-family="monospace" font-weight="bold">{densities[1]:.0f}</text>
      <text x="200" y="348" text-anchor="middle" fill="#60a5fa" font-size="8" font-family="monospace" opacity="0.6">density</text>

      {emg_html}

      <!-- Center label -->
      <text x="200" y="202" text-anchor="middle" fill="#1e3a5f" font-size="7" font-family="monospace" letter-spacing="2">INTERSECTION</text>

      <!-- Outer border -->
      <rect x="1" y="1" width="398" height="398" fill="none" stroke="#1e3a5f" stroke-width="1.5" rx="6"/>
    </svg>
    </body>
    </html>
    """
    components.html(html, height=390, scrolling=False)


def render_density_chart():
    """Real-time density chart for all lanes."""
    fig = go.Figure()

    colors = ["#22c55e", "#3b82f6", "#f97316", "#a855f7"]
    fill_colors = ["rgba(34,197,94,0.06)", "rgba(59,130,246,0.06)", "rgba(249,115,22,0.06)", "rgba(168,85,247,0.06)"]
    names = ["Lane 1 (N)", "Lane 2 (S)", "Lane 3 (E)", "Lane 4 (W)"]

    for i in range(4):
        data = list(st.session_state.density_history[i])
        if data:
            x = list(range(len(data)))
            fig.add_trace(go.Scatter(
                x=x, y=data,
                mode="lines",
                name=names[i],
                line=dict(color=colors[i], width=2),
                fill="tozeroy",
                fillcolor=fill_colors[i],
            ))

    # Threshold lines
    fig.add_hline(y=5, line_dash="dot", line_color="#334155", annotation_text="LOW→MED", annotation_font_size=9)
    fig.add_hline(y=15, line_dash="dot", line_color="#4a5568", annotation_text="MED→HIGH", annotation_font_size=9)
    fig.add_hline(y=30, line_dash="dot", line_color="#64748b", annotation_text="HIGH→CRIT", annotation_font_size=9)

    fig.update_layout(
        plot_bgcolor="#0a0e1a",
        paper_bgcolor="#0a0e1a",
        font=dict(color="#94a3b8", size=10),
        margin=dict(l=30, r=10, t=10, b=30),
        height=200,
        legend=dict(
            orientation="h", x=0, y=1.1,
            font=dict(size=9),
            bgcolor="rgba(0,0,0,0)",
        ),
        xaxis=dict(
            showgrid=False,
            tickfont=dict(size=8),
            color="#475569",
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="#1e3a5f",
            tickfont=dict(size=8),
            color="#475569",
            range=[0, 55],
            title="Density",
            title_font=dict(size=9),
        ),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def render_optimization_table():
    """Show AI timing optimization per lane."""
    rows = []
    for i in range(4):
        d = st.session_state.densities[i]
        csw = st.session_state.cycles_since_green[i]
        rec_green = calc_green_time(d, csw)
        fairness = max(0, (csw - FAIRNESS_CYCLES)) * FAIRNESS_BONUS
        congestion = st.session_state.congestion_levels[i]
        state = st.session_state.signal_states[i]
        rows.append({
            "Lane": LANE_NAMES[i],
            "State": state,
            "Density": f"{d:.1f}",
            "Vehicles": st.session_state.vehicle_counts[i],
            "Congestion": congestion,
            "AI Green Time": f"{rec_green:.0f}s",
            "Fairness +": f"+{fairness:.0f}s" if fairness > 0 else "—",
            "Wait Cycles": csw,
        })

    df = pd.DataFrame(rows)

    def style_row(row):
        state = row["State"]
        if state == "GREEN": bg = "rgba(34,197,94,0.08)"
        elif state == "YELLOW": bg = "rgba(245,158,11,0.08)"
        elif state == "EMERGENCY": bg = "rgba(239,68,68,0.12)"
        else: bg = "transparent"
        return [f"background: {bg}" for _ in row]

    st.dataframe(
        df.style.apply(style_row, axis=1),
        use_container_width=True,
        height=190,
        hide_index=True,
    )


# ─── Main App ────────────────────────────────────────────────────────────────
def main():
    init_state()
    update_simulation()

    # ── Header ──
    elapsed = int(time.time() - st.session_state.start_time)
    h, m, s = elapsed // 3600, (elapsed % 3600) // 60, elapsed % 60
    emg_badge = ' <span style="background:#ef4444;color:white;padding:0.2rem 0.6rem;border-radius:4px;font-size:0.75rem;font-weight:700;margin-left:1rem;animation:pulse 0.8s infinite;">🚨 EMERGENCY ACTIVE</span>' if st.session_state.emergency_active else ""

    st.markdown(f"""
    <div class="traffic-header">
        <div>
            <div class="header-title">🚦 TrafficVision AI {emg_badge}</div>
            <div class="header-subtitle">Dynamic AI Traffic Flow Optimizer & Emergency Grid</div>
        </div>
        <div style="text-align:right">
            <div class="live-badge">● LIVE</div>
            <div style="font-size:0.75rem;color:#475569;margin-top:0.3rem;font-family:'JetBrains Mono',monospace;">
                {h:02d}:{m:02d}:{s:02d} | Frame #{st.session_state.frame_count} | Cycle #{st.session_state.cycle_number}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Emergency Banner ──
    if st.session_state.emergency_active:
        lane = st.session_state.emergency_lane
        etype = st.session_state.emergency_type.upper()
        remaining = st.session_state.emergency_hold_remaining
        st.markdown(f"""
        <div class="emergency-banner">
            <span style="font-size:2rem">🚑</span>
            <div>
                <div class="emergency-text">🚨 EMERGENCY GREEN CORRIDOR ACTIVE</div>
                <div class="emergency-detail">
                    {etype} detected on {LANE_NAMES[lane] if lane is not None else "Unknown"} •
                    All other lanes held RED •
                    Clearing in {remaining:.0f}s
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Sidebar ──
    with st.sidebar:
        st.markdown('<div class="sidebar-title">⚙️ SYSTEM CONTROL</div>', unsafe_allow_html=True)

        scenario = st.selectbox(
            "Traffic Scenario",
            ["Normal Flow", "Morning Rush Hour", "Evening Rush Hour",
             "Light Traffic", "Traffic Incident", "Emergency Vehicle"],
            index=["Normal Flow", "Morning Rush Hour", "Evening Rush Hour",
                   "Light Traffic", "Traffic Incident", "Emergency Vehicle"].index(
                       st.session_state.scenario),
        )
        st.session_state.scenario = scenario

        st.markdown('<div class="sidebar-title" style="margin-top:1rem">🚨 EMERGENCY CONTROL</div>',
                    unsafe_allow_html=True)

        emg_type = st.selectbox("Emergency Vehicle Type",
                                ["ambulance", "fire_truck", "police_car"])
        emg_lane = st.selectbox("Target Lane",
                                [f"Lane {i+1} – {LANE_NAMES[i]}" for i in range(4)])
        emg_lane_id = int(emg_lane.split(" ")[1]) - 1

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🚨 Activate Corridor", disabled=st.session_state.emergency_active):
                _trigger_emergency(emg_lane_id, emg_type)
        with col2:
            if st.button("✅ Clear Corridor", disabled=not st.session_state.emergency_active):
                _clear_emergency()

        st.markdown('<div class="sidebar-title" style="margin-top:1rem">📊 LIVE STATS</div>',
                    unsafe_allow_html=True)
        st.metric("Total Vehicles Served", st.session_state.total_vehicles_served)
        st.metric("Signal Cycles", st.session_state.cycle_number)
        st.metric("Corridor Activations", len(st.session_state.corridor_events))

        # Lane density sliders (manual override)
        st.markdown('<div class="sidebar-title" style="margin-top:1rem">🎛️ MANUAL DENSITY</div>',
                    unsafe_allow_html=True)
        for i in range(4):
            val = st.slider(f"Lane {i+1}", 0.0, 50.0,
                            float(st.session_state.densities[i]), 0.5,
                            key=f"slider_{i}")
            st.session_state.densities[i] = val

        st.markdown('<div class="sidebar-title" style="margin-top:1rem">📋 EVENT LOG</div>',
                    unsafe_allow_html=True)
        for entry in st.session_state.event_log[:8]:
            css = {"emergency": "log-emergency", "info": "log-info", "normal": "log-normal"}.get(
                entry["level"], "log-normal")
            st.markdown(
                f'<div class="log-entry {css}">[{entry["time"]}] {entry["msg"]}</div>',
                unsafe_allow_html=True
            )

    # ── Main Layout ──
    # Row 1: Signal cards
    st.markdown("#### 🚦 Live Signal States")
    cols = st.columns(4)
    for i, col in enumerate(cols):
        with col:
            render_signal_card(i)

    st.markdown("---")

    # Row 2: Intersection viz + Density chart
    col_left, col_right = st.columns([1, 2])

    with col_left:
        st.markdown("#### 🗺️ Intersection Grid")
        render_intersection_viz()

    with col_right:
        st.markdown("#### 📈 Real-Time Density (60s window)")
        render_density_chart()

    st.markdown("---")

    # Row 3: AI Optimization table + Metrics
    col_a, col_b = st.columns([3, 1])

    with col_a:
        st.markdown("#### 🤖 AI Signal Optimization Engine")
        render_optimization_table()

    with col_b:
        st.markdown("#### 📊 System Metrics")
        total_density = sum(st.session_state.densities)
        avg_density = total_density / 4
        most_congested = max(range(4), key=lambda i: st.session_state.densities[i])
        least_congested = min(range(4), key=lambda i: st.session_state.densities[i])

        st.metric("Avg Density", f"{avg_density:.1f}", delta=f"±{random.uniform(-1, 1):.1f}")
        st.metric("Total Flow", f"{sum(st.session_state.vehicle_counts)}", delta="+active")
        st.metric("Most Congested", f"Lane {most_congested + 1}",
                  delta=f"{st.session_state.congestion_levels[most_congested]}")
        st.metric("Least Congested", f"Lane {least_congested + 1}",
                  delta=f"{st.session_state.congestion_levels[least_congested]}")

    st.markdown("---")

    # Row 4: Emergency history + Signal timing explanation
    col_x, col_y = st.columns([1, 1])

    with col_x:
        st.markdown("#### 🚑 Emergency Corridor History")
        if st.session_state.corridor_events:
            df_emg = pd.DataFrame(st.session_state.corridor_events[:10])
            st.dataframe(df_emg, use_container_width=True, height=180, hide_index=True)
        else:
            st.markdown(
                '<div style="color:#475569;font-size:0.8rem;padding:1rem;background:#0f1c2e;border-radius:8px;border:1px solid #1e3a5f;">'
                'No emergency events recorded yet.<br>Activate a corridor or wait for auto-trigger.</div>',
                unsafe_allow_html=True
            )

    with col_y:
        st.markdown("#### ⏱️ Signal Timing Algorithm")
        timing_data = {
            "Density Range": ["0–5", "5–15", "15–30", "30–50", "50+"],
            "Base Green (s)": [10, 20, 35, 45, 60],
            "Congestion Level": ["LOW", "MEDIUM", "HIGH", "CRITICAL", "CRITICAL"],
        }
        df_timing = pd.DataFrame(timing_data)
        st.dataframe(df_timing, use_container_width=True, height=215, hide_index=True)

    # Auto-refresh
    st.markdown(
        f'<div style="text-align:center;font-size:0.65rem;color:#334155;margin-top:1rem;font-family:JetBrains Mono,monospace;">'
        f'TrafficVision AI • Frame {st.session_state.frame_count} • '
        f'Scenario: {st.session_state.scenario} • '
        f'{"🚨 EMERGENCY" if st.session_state.emergency_active else "✅ NORMAL OPERATION"}'
        f'</div>',
        unsafe_allow_html=True,
    )

    # Auto-rerun
    time.sleep(0.05)
    st.rerun()


if __name__ == "__main__":
    main()
