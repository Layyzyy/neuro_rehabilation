import streamlit as st
import time
import base64
import json
import os
import login_component


# Check if user is logged in
if not st.session_state.get('logged_in', False):
    login_component.login_page()
    st.stop()

# ========== LOGGED IN - SHOW MAIN APP ==========

# Add logout button in sidebar
with st.sidebar:
    st.markdown(f"### 👤 Logged in as: **{st.session_state.get('username', '')}**")
    if st.button("Logout", use_container_width=True):
        login_component.logout()
    st.markdown("---")

# ========== AUDIO ASSETS LOADING (CACHED B64 FOR CLIENT PLAYBACK) ==========
@st.cache_data
def get_audio_assets():
    audio_files = {
        "press": "press.wav",
        "getready": "getready.wav",
        "hold3sec": "hold3sec.wav",
        "3": "3.wav",
        "2": "2.wav",
        "1": "1.wav",
        "release": "release.wav",
        "goodjob": "goodjob.wav",
        "ding": "ding.wav"
    }
    audio_b64 = {}
    for name, filename in audio_files.items():
        if os.path.exists(filename):
            with open(filename, "rb") as f:
                audio_b64[name] = base64.b64encode(f.read()).decode("utf-8")
    return audio_b64

# ========== MAIN APP STYLING ==========
st.markdown("""
    <style>
    /* Dark premium background for main app */
    .stApp {
        background: linear-gradient(135deg, #0a0015 0%, #1a0033 50%, #2d1b4e 100%);
    }
    
    /* Header styling */
    h1 {
        color: #ff00ff;
        font-weight: 900;
        text-align: center;
        padding: 1.5rem 0;
        letter-spacing: 2px;
        font-size: 3rem;
    }
    
    h2, h3 {
        color: #c084fc;
    }
    
    /* Card-like containers */
    .stSelectbox, .stRadio {
        background: rgba(20, 10, 40, 0.6);
        padding: 1.5rem;
        border-radius: 16px;
        border: 1px solid rgba(255, 0, 255, 0.3);
        margin-bottom: 1.5rem;
    }
    
    /* Select box and radio button text */
    .stSelectbox label, .stRadio label {
        color: #c084fc !important;
        font-weight: 600;
        font-size: 1.1rem;
    }
    
    /* Dropdown styling */
    .stSelectbox > div > div {
        background: rgba(10, 0, 30, 0.8);
        border: 2px solid rgba(255, 0, 255, 0.4);
        border-radius: 10px;
        color: #e0e0e0;
    }
    
    /* Success message */
    .stSuccess {
        background: rgba(16, 185, 129, 0.2);
        border: 1px solid #10b981;
        color: #6ee7b7;
        border-radius: 12px;
        padding: 1rem;
        font-weight: 600;
    }
    
    /* Sidebar with dark gradient */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a0033 0%, #2d1b4e 100%);
        border-right: 2px solid rgba(255, 0, 255, 0.3);
    }
    
    [data-testid="stSidebar"] * {
        color: #c084fc !important;
    }
    
    [data-testid="stSidebar"] h3 {
        color: #ff00ff !important;
    }
    
    /* Ensure Sidebar Button Text is Pure White */
    [data-testid="stSidebar"] .stButton > button {
        color: #ffffff !important;
    }
    
    [data-testid="stSidebar"] .stButton > button * {
        color: #ffffff !important;
    }
    
    [data-testid="stSidebar"] button {
        color: #ffffff !important;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #ff00ff 0%, #8b5cf6 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.8rem 2rem;
        font-weight: 700;
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
    }
    
    /* Checkbox styling */
    .stCheckbox {
        background: rgba(20, 10, 40, 0.6);
        padding: 2rem;
        border-radius: 16px;
        border: 1px solid rgba(255, 0, 255, 0.3);
    }
    
    .stCheckbox label {
        color: #ff00ff !important;
        font-weight: 700;
        font-size: 1.3rem;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: rgba(139, 92, 246, 0.2);
        border: 1px solid rgba(255, 0, 255, 0.3);
        border-radius: 12px;
        font-weight: 600;
        color: #c084fc;
    }
    
    /* Slider styling */
    .stSlider {
        background: rgba(20, 10, 40, 0.6);
        padding: 1rem;
        border-radius: 12px;
        border: 1px solid rgba(255, 0, 255, 0.2);
    }
    
    .stSlider label {
        color: #c084fc !important;
        font-weight: 600;
    }
    
    .stSlider > div > div > div > div {
        background: linear-gradient(135deg, #ff00ff 0%, #8b5cf6 100%);
    }
    
    /* Info boxes */
    .stInfo {
        background: rgba(139, 92, 246, 0.2);
        border: 1px solid rgba(255, 0, 255, 0.3);
        border-radius: 12px;
        color: #c084fc;
    }
    
    /* Horizontal rule */
    hr {
        border-color: rgba(255, 0, 255, 0.3);
        box-shadow: 0 0 10px rgba(255, 0, 255, 0.2);
    }
    
    /* General text color */
    p, span, div {
        color: #e0e0e0;
    }
    </style>
""", unsafe_allow_html=True)

# ========== UI HEADER ==========
st.markdown("# NEUROREHAB AI SYSTEM")
st.markdown('<h3 style="text-align: center;">Spinal Reflex Palm Therapy • Press • Hold • Release</h3>', unsafe_allow_html=True)
st.markdown("---")

# ---- Condition → Spinal Region Mapping (C1 to Coccyx) ----
condition = st.selectbox(
    "Select your spinal condition:",
    [
        "Cervical Spondylitis (C1–C7)",
        "Thoracic Postural Pain (T1–T12)",
        "Lumbar Slip Disc (L1–L5)",
        "Sciatica / Sacral Nerve Pain",
        "Coccyx Tailbone Pain",
        "General Muscle Tightness",
    ],
)

exercise_plan = {
    "Cervical Spondylitis (C1–C7)": {
        "region": "Cervical (C1–C7)",
        "reps": 12,
    },
    "Thoracic Postural Pain (T1–T12)": {
        "region": "Thoracic (T1–T12)",
        "reps": 15,
    },
    "Lumbar Slip Disc (L1–L5)": {
        "region": "Lumbar (L1–L5)",
        "reps": 10,
    },
    "Sciatica / Sacral Nerve Pain": {
        "region": "Sacrum",
        "reps": 15,
    },
    "Coccyx Tailbone Pain": {
        "region": "Coccyx",
        "reps": 8,
    },
    "General Muscle Tightness": {
        "region": "Cervical (C1–C7)",
        "reps": 8,
    },
}

plan = exercise_plan[condition]
spinal_region = plan["region"]          # e.g. "Cervical (C1–C7)"
default_reps = plan["reps"]

# ---- Customizable Reps Per Region ----
with st.expander("Customize Reps for Each Pressure Point (Optional)", expanded=False):
    st.markdown("**Adjust the number of repetitions for each spinal region according to patient needs:**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        cervical_reps = st.slider(
            "Cervical (C1-C7) Reps",
            min_value=1,
            max_value=20,
            value=7,
            help="Number of reps for cervical spine reflex points"
        )
        
        thoracic_reps = st.slider(
            "Thoracic (T1-T12) Reps",
            min_value=1,
            max_value=25,
            value=12,
            help="Number of reps for thoracic spine reflex points"
        )
        
        lumbar_reps = st.slider(
            "Lumbar (L1-L5) Reps",
            min_value=1,
            max_value=20,
            value=5,
            help="Number of reps for lumbar spine reflex points"
        )
    
    with col2:
        sacrum_reps = st.slider(
            "Sacrum (S1-S5) Reps",
            min_value=1,
            max_value=20,
            value=5,
            help="Number of reps for sacral reflex points"
        )
        
        coccyx_reps = st.slider(
            "Coccyx (Co1-Co4) Reps",
            min_value=1,
            max_value=15,
            value=4,
            help="Number of reps for coccyx reflex points"
        )
    
    st.info("💡 These custom reps are applied automatically based on your selected spinal region.")

# Map custom reps to each region
custom_reps_map = {
    "Cervical (C1–C7)": cervical_reps,
    "Thoracic (T1–T12)": thoracic_reps,
    "Lumbar (L1–L5)": lumbar_reps,
    "Sacrum": sacrum_reps,
    "Coccyx": coccyx_reps,
}

# Use custom reps for the selected spinal region
target_reps = custom_reps_map.get(spinal_region, default_reps)

hand_choice = st.radio(
    "Select reflex therapy hand (the palm where reflex point is highlighted):",
    ["Right Hand", "Left Hand"],
)

st.success(
    f"Spinal Region: {spinal_region} | Target Reps: {target_reps} | Reflex Hand: {hand_choice}"
)

# ========== SENSITIVITY SLIDERS ==========
st.sidebar.title("Sensitivity Calibration")
PRESS_TH = st.sidebar.slider(
    "Press Sensitivity (lower = must press closer)",
    0.010,
    0.060,
    0.028,
    step=0.002,
)
RELEASE_TH = st.sidebar.slider(
    "Release Sensitivity (higher = must move farther away)",
    0.040,
    0.120,
    0.060,
    step=0.002,
)
HOLD_TIME = st.sidebar.slider(
    "Hold duration (for countdown)",
    1.0,
    4.0,
    2.5,
    step=0.1,
)
STABILITY_TIME = 0.25  # seconds of stable press required before starting countdown

# ==# ========== CAMERA / THERAPY INTERFACE SECTION ==========

# If camera is not started, show the hand map reference guide
run_camera = st.checkbox("Start Therapy Interface", help="Enables camera feedback and active reflex tracking.")

if not run_camera:
    st.markdown("### 🖐️ Spinal Reflex Palm Mapping Guide")
    st.markdown(
        "Before beginning, please refer to the palm diagram below to locate the spinal reflex points. "
        "When you start the therapy interface, you will hold up your hand and use your other index finger "
        "to press and hold on the pulsing points."
    )
    if os.path.exists("hand_map.png"):
        st.image("hand_map.png", caption="Spinal Reflex Points Mapping on Palm", use_container_width=True)
    else:
        st.info("Visual mapping guide (hand_map.png) not found.")
else:
    # Load audio assets
    audio_data = get_audio_assets()
    
    # Build HTML/JS/CSS source code
    html_template = """<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>NeuroRehab AI Interface</title>
  <style>
    body {
      margin: 0;
      padding: 0;
      background-color: #0c021b;
      color: #e0e0e0;
      font-family: 'Inter', system-ui, -apple-system, sans-serif;
      overflow: hidden;
    }
    
    /* Premium dark high-tech design */
    .dashboard {
      display: grid;
      grid-template-columns: 1.2fr 1fr;
      gap: 1.5rem;
      padding: 1rem;
      box-sizing: border-box;
      height: 100vh;
      max-height: 590px;
    }
    
    @media (max-width: 768px) {
      .dashboard {
        grid-template-columns: 1fr;
        height: auto;
        max-height: none;
        overflow-y: auto;
      }
    }
    
    /* Viewport Panel */
    .viewport-panel {
      position: relative;
      background: rgba(20, 10, 40, 0.4);
      border-radius: 20px;
      border: 1px solid rgba(255, 0, 255, 0.15);
      box-shadow: inset 0 0 20px rgba(139, 92, 246, 0.1);
      display: flex;
      justify-content: center;
      align-items: center;
      overflow: hidden;
      aspect-ratio: 4/3;
    }
    
    video {
      display: none;
    }
    
    canvas {
      width: 100%;
      height: 100%;
      object-fit: cover;
      border-radius: 20px;
    }
    
    /* Splash / Initialize Overlay */
    .overlay {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: rgba(12, 2, 27, 0.9);
      backdrop-filter: blur(12px);
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      z-index: 100;
      transition: opacity 0.5s ease;
      text-align: center;
      padding: 2rem;
      box-sizing: border-box;
    }
    
    .overlay-title {
      font-size: 1.8rem;
      font-weight: 800;
      color: #ffffff;
      margin-bottom: 0.5rem;
      letter-spacing: 1px;
      text-shadow: 0 0 15px rgba(255, 0, 255, 0.5);
    }
    
    .overlay-subtitle {
      font-size: 0.95rem;
      color: #a0e7e5;
      margin-bottom: 2rem;
      max-width: 400px;
      line-height: 1.5;
    }
    
    .activate-btn {
      background: linear-gradient(135deg, #ff00ff 0%, #8b5cf6 100%);
      color: white;
      border: none;
      border-radius: 12px;
      padding: 1rem 2.5rem;
      font-weight: bold;
      font-size: 1.1rem;
      cursor: pointer;
      text-transform: uppercase;
      letter-spacing: 1px;
      box-shadow: 0 0 25px rgba(255, 0, 255, 0.4);
      transition: all 0.3s ease;
    }
    
    .activate-btn:hover {
      transform: translateY(-3px);
      box-shadow: 0 0 35px rgba(255, 0, 255, 0.7);
    }
    
    /* Metrics Panel */
    .metrics-panel {
      background: rgba(18, 5, 36, 0.65);
      backdrop-filter: blur(16px);
      border-radius: 20px;
      border: 1px solid rgba(255, 0, 255, 0.2);
      padding: 1.5rem;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      box-sizing: border-box;
    }
    
    .panel-header {
      border-bottom: 1px solid rgba(255, 0, 255, 0.2);
      padding-bottom: 0.8rem;
      margin-bottom: 0.8rem;
    }
    
    .panel-title {
      font-size: 1.3rem;
      font-weight: 700;
      color: #ff00ff;
      margin: 0;
      text-transform: uppercase;
      letter-spacing: 1px;
    }
    
    .panel-subtitle {
      font-size: 0.85rem;
      color: #a0e7e5;
      margin-top: 0.25rem;
    }
    
    .progress-section {
      display: flex;
      align-items: center;
      gap: 1.5rem;
      margin: 1rem 0;
    }
    
    /* Progress Circle */
    .progress-container {
      position: relative;
      width: 100px;
      height: 100px;
      flex-shrink: 0;
    }
    .progress-ring__circle {
      transition: stroke-dashoffset 0.35s;
      transform: rotate(-90deg);
      transform-origin: 50% 50%;
    }
    .progress-text {
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      font-size: 1.3rem;
      font-weight: bold;
      color: white;
      text-shadow: 0 0 10px rgba(0, 255, 0, 0.5);
    }
    
    .counter-details {
      display: flex;
      flex-direction: column;
      justify-content: center;
    }
    
    .counter-label {
      font-size: 0.8rem;
      color: #7dd3c0;
      text-transform: uppercase;
    }
    
    .counter-value {
      font-size: 2.2rem;
      font-weight: 900;
      color: #ffffff;
      line-height: 1;
      margin-top: 0.25rem;
    }
    
    /* Status Badge */
    .status-badge {
      display: block;
      padding: 0.5rem 1rem;
      border-radius: 10px;
      font-weight: bold;
      font-size: 0.85rem;
      text-transform: uppercase;
      letter-spacing: 1px;
      text-align: center;
      margin-bottom: 1rem;
    }
    
    .neon-magenta {
      background: rgba(255, 0, 255, 0.15);
      border: 1px solid #ff00ff;
      color: #ff80ff;
      box-shadow: 0 0 10px rgba(255, 0, 255, 0.2);
    }
    
    .neon-yellow {
      background: rgba(234, 179, 8, 0.15);
      border: 1px solid #eab308;
      color: #fef08a;
      box-shadow: 0 0 10px rgba(234, 179, 8, 0.2);
    }
    
    .neon-cyan {
      background: rgba(6, 182, 212, 0.15);
      border: 1px solid #06b6d4;
      color: #99f6e4;
      box-shadow: 0 0 10px rgba(6, 182, 212, 0.2);
    }
    
    .neon-red {
      background: rgba(239, 68, 68, 0.15);
      border: 1px solid #ef4444;
      color: #fca5a5;
      box-shadow: 0 0 10px rgba(239, 68, 68, 0.2);
    }
    
    .neon-green {
      background: rgba(16, 185, 129, 0.15);
      border: 1px solid #10b981;
      color: #a7f3d0;
      box-shadow: 0 0 10px rgba(16, 185, 129, 0.3);
    }
    
    /* Distance Slider/Indicator */
    .distance-bar-container {
      background: rgba(255, 255, 255, 0.03);
      padding: 0.8rem;
      border-radius: 12px;
      border: 1px solid rgba(255, 255, 255, 0.05);
      margin-bottom: 1rem;
    }
    .distance-bar-label {
      font-size: 0.75rem;
      color: #a0e7e5;
      margin-bottom: 0.4rem;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }
    .distance-bar-track {
      width: 100%;
      height: 12px;
      background: rgba(255, 255, 255, 0.1);
      border-radius: 6px;
      position: relative;
      overflow: hidden;
      border: 1px solid rgba(255, 255, 255, 0.2);
    }
    .distance-bar-fill {
      height: 100%;
      background: linear-gradient(90deg, #ef4444, #eab308, #00ff00);
      width: 0%;
      transition: width 0.1s ease;
    }
    .distance-bar-target {
      position: absolute;
      top: 0;
      bottom: 0;
      width: 2px;
      background: #ffffff;
      box-shadow: 0 0 5px #ffffff;
    }
    .distance-value {
      text-align: right;
      font-size: 0.7rem;
      color: #7dd3c0;
      margin-top: 0.25rem;
    }
    
    /* Instructions */
    .instructions {
      font-size: 0.8rem;
      line-height: 1.4;
      color: #ccc;
      background: rgba(255, 255, 255, 0.03);
      padding: 0.8rem;
      border-radius: 10px;
      border-left: 3px solid #ff00ff;
    }
    
    /* Loading state */
    .loading-spinner {
      border: 4px solid rgba(255, 255, 255, 0.1);
      width: 40px;
      height: 40px;
      border-radius: 50%;
      border-left-color: #ff00ff;
      animation: spin 1s linear infinite;
      margin-bottom: 1.5rem;
    }
    
    @keyframes spin {
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }
  </style>
</head>
<body>

  <div class="dashboard">
    <!-- Viewport Panel -->
    <div class="viewport-panel">
      <!-- Media Access Blocked Overlay -->
      <div id="initOverlay" class="overlay">
        <div id="spinner" class="loading-spinner" style="display:none;"></div>
        <div class="overlay-title" id="overlayTitle">NEUROREHAB SYSTEM</div>
        <div class="overlay-subtitle" id="overlaySubtitle">
          Unlock the interactive palm therapy session. Runs hand landmark tracking on client side & plays audio guidance.
        </div>
        <button class="activate-btn" id="startBtn" onclick="activateTherapy()">Activate Interface</button>
      </div>
      
      <video id="webcam" autoplay playsinline></video>
      <canvas id="canvas"></canvas>
    </div>
    
    <!-- Metrics Panel -->
    <div class="metrics-panel">
      <div class="panel-header">
        <div class="panel-title" id="panelTitle">Reflex Session</div>
        <div class="panel-subtitle" id="panelRegion">Spinal Region</div>
      </div>
      
      <div class="status-badge neon-magenta" id="statusBadge">Initializing...</div>
      
      <div class="progress-section">
        <div class="progress-container">
          <svg class="progress-ring" width="100" height="100">
            <circle class="progress-ring__circle-bg" stroke="rgba(255, 255, 255, 0.05)" stroke-width="5" fill="transparent" r="42" cx="50" cy="50"/>
            <circle class="progress-ring__circle" id="progressCircle" stroke="#00ff00" stroke-width="6" fill="transparent" r="42" cx="50" cy="50"/>
          </svg>
          <div class="progress-text" id="progressPercent">0%</div>
        </div>
        
        <div class="counter-details">
          <div class="counter-label">Reps Completed</div>
          <div class="counter-value" id="repsCounter">0 / --</div>
        </div>
      </div>
      
      <div class="distance-bar-container">
        <div class="distance-bar-label">Alignment Distance Indicator</div>
        <div class="distance-bar-track">
          <div class="distance-bar-fill" id="distanceFill"></div>
          <div class="distance-bar-target" id="distanceTarget"></div>
        </div>
        <div class="distance-value" id="distanceValue">Waiting...</div>
      </div>
      
      <div class="instructions" id="instructionsText">
        Press active green pulsing reflex point on your target palm to begin.
      </div>
    </div>
  </div>

  <script>
    // Configuration from Streamlit
    window.CONFIG = {
        spinal_region: "__SPINAL_REGION__",
        target_reps: __TARGET_REPS__,
        hand_choice: "__HAND_CHOICE__",
        PRESS_TH: __PRESS_TH__,
        RELEASE_TH: __RELEASE_TH__,
        HOLD_TIME: __HOLD_TIME__,
        audio_data: __AUDIO_DATA__
    };
  </script>

  <script type="module">
    import { FilesetResolver, HandLandmarker } from "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.8/vision_bundle.mjs";

    let handLandmarker;
    let video = document.getElementById("webcam");
    let canvas = document.getElementById("canvas");
    let ctx = canvas.getContext("2d");
    let progressCircle = document.getElementById("progressCircle");
    
    let radius = progressCircle.r.baseVal.value;
    let circumference = radius * 2 * Math.PI;
    
    progressCircle.style.strokeDasharray = `${circumference} ${circumference}`;
    progressCircle.style.strokeDashoffset = `${circumference}`;

    // App state
    let count = 0;
    let stage = "waiting_press";
    let pressTimer = null;
    let smoothDistance = 1.0;
    const SMOOTH_FACTOR = 0.4;
    let pulseRadius = 22;
    let pulseDirection = 1;
    let activeTimers = [];
    
    const config = window.CONFIG;
    const targetReps = config.target_reps;
    const handChoice = config.hand_choice;
    const spinalRegion = config.spinal_region;
    const PRESS_TH = config.PRESS_TH;
    const RELEASE_TH = config.RELEASE_TH;
    const STABILITY_TIME = 0.25;

    // Load Audio Files
    const audio = {};
    for (const [key, base64] of Object.entries(config.audio_data)) {
      audio[key] = new Audio("data:audio/wav;base64," + base64);
    }
    
    function playAudio(name) {
      if (audio[name]) {
        audio[name].currentTime = 0;
        audio[name].play().catch(e => console.log("Audio playback failed:", e));
      }
    }

    // Set labels
    document.getElementById("panelRegion").innerText = `Spinal Region: ${spinalRegion}`;
    document.getElementById("repsCounter").innerText = `${count} / ${targetReps}`;

    window.activateTherapy = async function() {
      const btn = document.getElementById("startBtn");
      const spinner = document.getElementById("spinner");
      const title = document.getElementById("overlayTitle");
      const subtitle = document.getElementById("overlaySubtitle");
      
      btn.style.display = "none";
      spinner.style.display = "block";
      title.innerText = "LOADING AI MODELS...";
      subtitle.innerText = "Fetching MediaPipe Hand Tracking WebAssembly packages from CDN...";
      
      try {
        playAudio("getready");
        
        const vision = await FilesetResolver.forVisionTasks(
          "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.8/wasm"
        );
        
        handLandmarker = await HandLandmarker.createFromOptions(vision, {
          baseOptions: {
            modelAssetPath: "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
          },
          runningMode: "video",
          numHands: 2
        });
        
        title.innerText = "REQUESTING WEBCAM ACCESS...";
        subtitle.innerText = "Please click 'Allow' on your browser's webcam permission dialog.";
        
        const stream = await navigator.mediaDevices.getUserMedia({
          video: { width: 640, height: 480 }
        });
        
        video.srcObject = stream;
        video.onloadeddata = () => {
          document.getElementById("initOverlay").style.opacity = 0;
          setTimeout(() => {
            document.getElementById("initOverlay").style.display = "none";
          }, 500);
          
          playAudio("press");
          predictLoop();
        };
      } catch (err) {
        console.error(err);
        spinner.style.display = "none";
        btn.style.display = "block";
        btn.innerText = "TRY AGAIN";
        title.innerText = "ACTIVATION FAILED";
        subtitle.innerText = "Error initializing camera or audio. Please ensure webcam permissions are enabled and try again.\n\nDetail: " + err.message;
      }
    };

    let lastVideoTime = -1;
    function predictLoop() {
      if (video.currentTime !== lastVideoTime) {
        lastVideoTime = video.currentTime;
        
        const tempCanvas = document.createElement('canvas');
        tempCanvas.width = video.videoWidth;
        tempCanvas.height = video.videoHeight;
        const tempCtx = tempCanvas.getContext('2d');
        tempCtx.translate(tempCanvas.width, 0);
        tempCtx.scale(-1, 1);
        tempCtx.drawImage(video, 0, 0, tempCanvas.width, tempCanvas.height);
        
        const results = handLandmarker.detectForVideo(tempCanvas, performance.now());
        
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        ctx.drawImage(tempCanvas, 0, 0, canvas.width, canvas.height);
        
        processFrame(results);
      }
      requestAnimationFrame(predictLoop);
    }

    function setProgress(percent) {
      const offset = circumference - (percent / 100) * circumference;
      progressCircle.style.strokeDashoffset = offset;
      document.getElementById("progressPercent").innerText = `${Math.round(percent)}%`;
    }

    function updateRepsCount(val) {
      document.getElementById("repsCounter").innerText = `${val} / ${targetReps}`;
      setProgress((val / targetReps) * 100);
    }

    function updateStatusBadge(text, className) {
      const badge = document.getElementById("statusBadge");
      badge.innerText = text;
      badge.className = `status-badge ${className}`;
    }

    function updateDistanceUI(dist) {
      const maxDist = 0.2;
      const percentage = Math.min(100, (dist / maxDist) * 100);
      const fill = document.getElementById("distanceFill");
      
      fill.style.width = `${100 - percentage}%`;
      
      if (dist < PRESS_TH) {
        fill.style.background = '#00ff00';
      } else if (dist < RELEASE_TH) {
        fill.style.background = '#eab308';
      } else {
        fill.style.background = '#ef4444';
      }
      
      const targetMarker = document.getElementById("distanceTarget");
      targetMarker.style.left = `${(1 - PRESS_TH / maxDist) * 100}%`;
      
      document.getElementById("distanceValue").innerText = `Alignment dist: ${dist.toFixed(3)} (Min: ${PRESS_TH.toFixed(3)})`;
    }

    function drawSuccessMessage() {
      ctx.fillStyle = "rgba(12, 2, 27, 0.8)";
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      
      ctx.fillStyle = "#ffffff";
      ctx.font = "bold 26px 'Inter', sans-serif";
      ctx.textAlign = "center";
      ctx.fillText("SESSION COMPLETED!", canvas.width / 2, canvas.height / 2 - 10);
      
      ctx.fillStyle = "#00ff00";
      ctx.font = "16px 'Inter', sans-serif";
      ctx.fillText("🎉 Great job completing your spinal reflex routine!", canvas.width / 2, canvas.height / 2 + 25);
    }

    function runCountdownJS() {
      activeTimers = [];
      updateStatusBadge("HOLD STILL...", "neon-yellow");
      document.getElementById("instructionsText").innerText = "Keep your pressing finger steady at the reflex point.";
      
      playAudio("hold3sec");
      
      activeTimers.push(setTimeout(() => {
        playAudio("3");
        updateStatusBadge("COUNTDOWN: 3", "neon-yellow");
      }, 400));
      
      activeTimers.push(setTimeout(() => {
        playAudio("2");
        updateStatusBadge("COUNTDOWN: 2", "neon-yellow");
      }, 1200));
      
      activeTimers.push(setTimeout(() => {
        playAudio("1");
        updateStatusBadge("COUNTDOWN: 1", "neon-yellow");
      }, 2000));
      
      activeTimers.push(setTimeout(() => {
        playAudio("release");
        stage = "waiting_release";
        updateStatusBadge("RELEASE NOW!", "neon-cyan");
        document.getElementById("instructionsText").innerText = "Now release your finger from the palm reflex point.";
      }, 2300));
    }

    function cancelCountdownJS() {
      for (const timer of activeTimers) {
        clearTimeout(timer);
      }
      activeTimers = [];
    }

    function interpolateSegment(points, count) {
      if (points.length === 1) {
        return Array(count).fill(points[0]);
      }
      let dists = [];
      for (let i = 0; i < points.length - 1; i++) {
        let dx = points[i+1].x - points[i].x;
        let dy = points[i+1].y - points[i].y;
        dists.push(Math.sqrt(dx*dx + dy*dy));
      }
      let cumdist = [0];
      for (let i = 0; i < dists.length; i++) {
        cumdist.push(cumdist[cumdist.length - 1] + dists[i]);
      }
      let total = cumdist[cumdist.length - 1];
      if (total === 0) {
        return Array(count).fill(points[0]);
      }
      
      let out = [];
      for (let i = 0; i < count; i++) {
        let s = (i / (count - 1)) * total;
        let j = 0;
        while (j < cumdist.length && cumdist[j] < s) {
          j++;
        }
        if (j === 0) {
          out.push(points[0]);
        } else {
          if (j >= points.length) j = points.length - 1;
          let d0 = cumdist[j-1];
          let d1 = cumdist[j];
          let t = (d1 === d0) ? 0 : (s - d0) / (d1 - d0);
          let p0 = points[j-1];
          let p1 = points[j];
          out.push({
            x: (1 - t) * p0.x + t * p1.x,
            y: (1 - t) * p0.y + t * p1.y
          });
        }
      }
      return out;
    }

    function getSpinePoints(hand, region) {
      const thumb_tip  = hand[4];
      const thumb_mid  = hand[3];
      const thumb_base = hand[2];
      const mid_base   = hand[9];
      const ring_base  = hand[13];
      const pinky_base = hand[17];
      const wrist      = hand[0];
      
      if (region === "Cervical (C1–C7)") {
        return interpolateSegment([thumb_tip, thumb_mid, thumb_base], 7);
      }
      
      if (region === "Thoracic (T1–T12)") {
        const t1 = thumb_base;
        const t2 = { x: 0.7 * thumb_base.x + 0.3 * wrist.x, y: 0.7 * thumb_base.y + 0.3 * wrist.y };
        const t3 = { x: 0.4 * thumb_base.x + 0.6 * wrist.x, y: 0.4 * thumb_base.y + 0.6 * wrist.y };
        return interpolateSegment([t1, t2, t3], 12);
      }
      
      if (region === "Lumbar (L1–L5)") {
        const lumbar_start = {
          x: mid_base.x + 0.85 * (wrist.x - mid_base.x),
          y: mid_base.y + 0.85 * (wrist.y - mid_base.y)
        };
        const pinky_to_wrist_x = wrist.x - pinky_base.x;
        const pinky_to_wrist_y = wrist.y - pinky_base.y;
        let lumbar_end = {
          x: pinky_base.x + 0.95 * pinky_to_wrist_x,
          y: pinky_base.y + 0.95 * pinky_to_wrist_y
        };
        const outward_shift_x = (pinky_base.x - mid_base.x) * 0.2;
        const outward_shift_y = (pinky_base.y - mid_base.y) * 0.2;
        lumbar_end.x += outward_shift_x;
        lumbar_end.y += outward_shift_y;
        
        return interpolateSegment([lumbar_start, lumbar_end], 5);
      }
      
      if (region === "Sacrum") {
        const lumbar_start = {
          x: mid_base.x + 0.85 * (wrist.x - mid_base.x),
          y: mid_base.y + 0.85 * (wrist.y - mid_base.y)
        };
        const pinky_to_wrist_x = wrist.x - pinky_base.x;
        const pinky_to_wrist_y = wrist.y - pinky_base.y;
        let lumbar_end = {
          x: pinky_base.x + 0.95 * pinky_to_wrist_x,
          y: pinky_base.y + 0.95 * pinky_to_wrist_y
        };
        const outward_shift_x = (pinky_base.x - mid_base.x) * 0.2;
        const outward_shift_y = (pinky_base.y - mid_base.y) * 0.2;
        lumbar_end.x += outward_shift_x;
        lumbar_end.y += outward_shift_y;
        
        const sacrum_start = lumbar_end;
        const sacrum_end = {
          x: sacrum_start.x + 0.015 * pinky_to_wrist_x,
          y: sacrum_start.y + 0.015 * pinky_to_wrist_y
        };
        return interpolateSegment([sacrum_start, sacrum_end], 5);
      }
      
      if (region === "Coccyx") {
        const lumbar_start = {
          x: mid_base.x + 0.85 * (wrist.x - mid_base.x),
          y: mid_base.y + 0.85 * (wrist.y - mid_base.y)
        };
        const pinky_to_wrist_x = wrist.x - pinky_base.x;
        const pinky_to_wrist_y = wrist.y - pinky_base.y;
        let lumbar_end = {
          x: pinky_base.x + 0.95 * pinky_to_wrist_x,
          y: pinky_base.y + 0.95 * pinky_to_wrist_y
        };
        const outward_shift_x = (pinky_base.x - mid_base.x) * 0.2;
        const outward_shift_y = (pinky_base.y - mid_base.y) * 0.2;
        lumbar_end.x += outward_shift_x;
        lumbar_end.y += outward_shift_y;
        
        const sacrum_start = lumbar_end;
        const sacrum_end = {
          x: sacrum_start.x + 0.015 * pinky_to_wrist_x,
          y: sacrum_start.y + 0.015 * pinky_to_wrist_y
        };
        
        const coccyx_start = sacrum_end;
        const coccyx_end = {
          x: coccyx_start.x + 0.015 * pinky_to_wrist_x,
          y: coccyx_start.y + 0.015 * pinky_to_wrist_y
        };
        return interpolateSegment([coccyx_start, coccyx_end], 4);
      }
      
      return [];
    }

    const HAND_CONNECTIONS = [
      [0, 1], [1, 2], [2, 3], [3, 4],
      [0, 5], [5, 6], [6, 7], [7, 8],
      [5, 9], [9, 10], [10, 11], [11, 12],
      [9, 13], [13, 14], [14, 15], [15, 16],
      [13, 17], [17, 18], [18, 19], [19, 20],
      [0, 17]
    ];

    function drawHandLandmarks(landmarks) {
      ctx.strokeStyle = "#8b5cf6";
      ctx.lineWidth = 3;
      for (const [p1, p2] of HAND_CONNECTIONS) {
        const pt1 = landmarks[p1];
        const pt2 = landmarks[p2];
        if (pt1 && pt2) {
          ctx.beginPath();
          ctx.moveTo(pt1.x * canvas.width, pt1.y * canvas.height);
          ctx.lineTo(pt2.x * canvas.width, pt2.y * canvas.height);
          ctx.stroke();
        }
      }
      
      ctx.fillStyle = "#ff00ff";
      for (const lm of landmarks) {
        ctx.beginPath();
        ctx.arc(lm.x * canvas.width, lm.y * canvas.height, 4, 0, 2 * Math.PI);
        ctx.fill();
      }
    }

    function drawActiveReflexPoint(point) {
      const cx = point.x * canvas.width;
      const cy = point.y * canvas.height;
      
      ctx.strokeStyle = "#00ff00";
      ctx.lineWidth = 3;
      ctx.beginPath();
      ctx.arc(cx, cy, pulseRadius, 0, 2 * Math.PI);
      ctx.stroke();
      
      pulseRadius += pulseDirection * 0.8;
      if (pulseRadius >= 35 || pulseRadius <= 15) {
        pulseDirection *= -1;
      }
    }

    function processFrame(results) {
      if (stage === "completed") {
        drawSuccessMessage();
        return;
      }

      if (results.landmarks) {
        for (const landmarks of results.landmarks) {
          drawHandLandmarks(landmarks);
        }
      }

      if (results.landmarks && results.landmarks.length === 2) {
        let h1 = results.landmarks[0];
        let h2 = results.landmarks[1];
        
        let leftHand = null;
        let rightHand = null;
        if (h1[0].x < h2[0].x) {
          leftHand = h1;
          rightHand = h2;
        } else {
          leftHand = h2;
          rightHand = h1;
        }
        
        const targetHand = (handChoice === "Right Hand") ? rightHand : leftHand;
        const pressingHand = (targetHand === rightHand) ? leftHand : rightHand;
        
        const points = getSpinePoints(targetHand, spinalRegion);
        
        if (points && points.length > 0) {
          const activeIdx = Math.min(count, points.length - 1);
          const activeReflexPoint = points[activeIdx];
          
          drawActiveReflexPoint(activeReflexPoint);
          
          const pressTip = pressingHand[8];
          
          const dist = Math.sqrt(
            (activeReflexPoint.x - pressTip.x) ** 2 +
            (activeReflexPoint.y - pressTip.y) ** 2
          );
          
          smoothDistance = smoothDistance * (1 - SMOOTH_FACTOR) + dist * SMOOTH_FACTOR;
          updateDistanceUI(smoothDistance);
          
          const now = performance.now() / 1000;
          
          if (stage === "waiting_press") {
            if (smoothDistance < PRESS_TH) {
              if (pressTimer === null) {
                pressTimer = now;
                updateStatusBadge("STABILIZING...", "neon-yellow");
              } else if (now - pressTimer >= STABILITY_TIME) {
                stage = "countdown_running";
                runCountdownJS();
              }
            } else {
              pressTimer = null;
              updateStatusBadge("WAITING FOR PRESS", "neon-magenta");
              document.getElementById("instructionsText").innerText = "Press your index finger to the pulsing green reflex point on your " + handChoice + ".";
            }
          } else if (stage === "countdown_running") {
            if (smoothDistance > RELEASE_TH) {
              cancelCountdownJS();
              stage = "waiting_press";
              pressTimer = null;
              playAudio("press");
              updateStatusBadge("RELEASED EARLY! PRESS AGAIN", "neon-red");
            }
          } else if (stage === "waiting_release") {
            if (smoothDistance > RELEASE_TH) {
              playAudio("ding");
              playAudio("goodjob");
              count++;
              updateRepsCount(count);
              
              if (count >= targetReps) {
                stage = "completed";
                updateStatusBadge("COMPLETED!", "neon-green");
                document.getElementById("instructionsText").innerText = "Routine completed successfully! Excellent rehabilitation effort.";
              } else {
                stage = "waiting_press";
                pressTimer = null;
                playAudio("press");
                updateStatusBadge("WAITING FOR PRESS", "neon-magenta");
              }
            }
          }
        }
      } else {
        updateStatusBadge("SHOW BOTH PALMS", "neon-yellow");
        document.getElementById("instructionsText").innerText = "Hold up both hands in the camera view: one target palm (fully flat) and one pressing hand.";
        pressTimer = null;
        if (stage === "countdown_running") {
          cancelCountdownJS();
          stage = "waiting_press";
          playAudio("press");
        }
      }
    }
  </script>
</body>
</html>
"""
    
    # Replace parameters
    html_src = html_template
    html_src = html_src.replace("__SPINAL_REGION__", spinal_region)
    html_src = html_src.replace("__TARGET_REPS__", str(target_reps))
    html_src = html_src.replace("__HAND_CHOICE__", hand_choice)
    html_src = html_src.replace("__PRESS_TH__", f"{PRESS_TH:.4f}")
    html_src = html_src.replace("__RELEASE_TH__", f"{RELEASE_TH:.4f}")
    html_src = html_src.replace("__HOLD_TIME__", f"{HOLD_TIME:.1f}")
    html_src = html_src.replace("__AUDIO_DATA__", json.dumps(audio_data))
    
    # Render component with camera permission enabled
    st.components.v1.html(html_src, height=620, scrolling=False)