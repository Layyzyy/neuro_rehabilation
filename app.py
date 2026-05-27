# pyrefly: ignore [missing-import]
import streamlit as st
# pyrefly: ignore [missing-import]
import cv2
# pyrefly: ignore [missing-import]
import mediapipe as mp
import numpy as np
import time
import threading
import queue
try:
    import simpleaudio as sa
    HAS_AUDIO = True
except ImportError:
    HAS_AUDIO = False
from PIL import Image, ImageDraw, ImageFont
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

# ========== AUDIO QUEUE (NO OVERLAP) ==========
audio_queue = queue.Queue()

def audio_player():
    if not HAS_AUDIO:
        return
    while True:
        file = audio_queue.get()
        if file is None:
            break
        try:
            wave = sa.WaveObject.from_wave_file(file)
            wave.play().wait_done()
        except Exception as e:
            # Fallback gracefully if playing fails (e.g., on headless server)
            pass
        audio_queue.task_done()

threading.Thread(target=audio_player, daemon=True).start()

def speak(file):
    audio_queue.put(file)

# Pre-generated audio files (must exist in SAME folder as app.py)
PRESS_V   = "press.wav"
READY_V   = "getready.wav"
HOLD_V    = "hold3sec.wav"
T3_V      = "3.wav"
T2_V      = "2.wav"
T1_V      = "1.wav"
RELEASE_V = "release.wav"
GOOD_V    = "goodjob.wav"
DING_V    = "ding.wav"

def ding():
    speak(DING_V)

# ========== PROGRESS CIRCLE UI ==========
def create_progress_circle(progress):
    size = 200
    img = Image.new("RGB", (size, size), (30, 30, 30))
    draw = ImageDraw.Draw(img)
    center = size // 2
    radius = 85

    draw.ellipse(
        (center-radius, center-radius, center+radius, center+radius),
        outline=(80, 80, 80),
        width=10,
    )

    angle = int(360 * (progress / 100))
    draw.arc(
        (center-radius, center-radius, center+radius, center+radius),
        start=-90,
        end=angle-90,
        fill=(0, 255, 0),
        width=14,
    )

    text = f"{int(progress)}%"
    font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), text, font=font)
    draw.text(
        (center - (bbox[2]-bbox[0])//2, center - (bbox[3]-bbox[1])//2),
        text,
        fill=(255, 255, 255),
        font=font,
    )
    return img

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

# ========== PULSE ANIMATION STATE ==========
if "pulse_radius" not in st.session_state:
    st.session_state.pulse_radius = 22
if "pulse_direction" not in st.session_state:
    st.session_state.pulse_direction = 1

# ========== SPINE PATH HELPERS / VIRTUAL POINTS ==========

def interpolate_segment(points, count):
    """Interpolate 'count' evenly spaced points along a path."""
    pts = np.array(points, dtype=float)
    if len(pts) == 1:
        return [tuple(pts[0])] * count

    dists = np.sqrt(((pts[1:] - pts[:-1]) ** 2).sum(axis=1))
    cumdist = np.insert(np.cumsum(dists), 0, 0.0)
    total = cumdist[-1]
    if total == 0:
        return [tuple(pts[0])] * count

    samples = np.linspace(0, total, count)
    out = []
    for s in samples:
        j = np.searchsorted(cumdist, s)
        if j == 0:
            out.append(tuple(pts[0]))
        else:
            if j >= len(pts):
                j = len(pts) - 1
            d0, d1 = cumdist[j-1], cumdist[j]
            if d1 == d0:
                t = 0.0
            else:
                t = (s - d0) / (d1 - d0)
            p = (1 - t) * pts[j-1] + t * pts[j]
            out.append(tuple(p))
    return out

def compute_spine_points_for_region(hand, img):
    """
    Build virtual spinal reflex points for each region:
    - Cervical: 7 virtual points along thumb (C1–C7)
    - Thoracic: 12 virtual points under thumb towards wrist (T1–T12)
    - Lumbar: placeholder (L1–L5, overridden dynamically)
    - Sacrum: 5 virtual points at extreme right palm base under pinky (S1–S5)
    - Coccyx: 4 virtual points just below sacrum (Co1–Co4)
    """
    h, w, _ = img.shape

    def LM_vec(i):
        lm = hand.landmark[i]
        return np.array([lm.x * w, lm.y * h], dtype=float)

    thumb_tip  = LM_vec(4)
    thumb_mid  = LM_vec(3)
    thumb_base = LM_vec(2)
    mid_base   = LM_vec(9)
    ring_base  = LM_vec(13)
    pinky_base = LM_vec(17)
    wrist      = LM_vec(0)

    # ----- Cervical: along thumb (7 virtual vertebra points: C1–C7)
    cervical_path = [thumb_tip, thumb_mid, thumb_base]
    cervical_pts = interpolate_segment(cervical_path, 7)

        # ----- Thoracic: band under thumb toward wrist (12 virtual points: T1–T12)
    t1 = thumb_base
    t2 = 0.7 * thumb_base + 0.3 * wrist
    t3 = 0.4 * thumb_base + 0.6 * wrist
    thoracic_path = [t1, t2, t3]
    thoracic_pts = interpolate_segment(thoracic_path, 12)

    # LAST thoracic point = lumbar start base
    thoracic_end = np.array(thoracic_pts[-1], dtype=float)

    # ----- Lumbar: starts deeper and extends to right edge below pinky at wrist (L1–L5)
    # Start from deep position near center of wrist
    lumbar_start = mid_base + 0.85 * (wrist - mid_base)
    
    # End point: right edge of palm below pinky finger at wrist level
    # Move toward pinky base and then down to wrist level, then extend to edge
    pinky_to_wrist_direction = wrist - pinky_base
    lumbar_end = pinky_base + 0.95 * pinky_to_wrist_direction  # very close to wrist on pinky side
    # Shift slightly outward toward palm edge (away from center)
    outward_shift = (pinky_base - mid_base) * 0.2  # shift toward edge
    lumbar_end = lumbar_end + outward_shift

    lumbar_path = [lumbar_start, lumbar_end]
    lumbar_pts = interpolate_segment(lumbar_path, 5)

    # LAST lumbar point = sacrum start
    lumbar_end_final = np.array(lumbar_pts[-1], dtype=float)

    # ----- Sacrum: endpoint is where S2 appears (S1–S5)
    sacrum_start = lumbar_end_final  # continue from where lumbar ends (this is S1)
    
    # Calculate endpoint so that when interpolated into 5 points,
    # the second point (S2) is at the endpoint position
    # We need a very small distance - the endpoint should be close to start
    # Direction: slightly down and toward edge
    edge_direction = wrist - pinky_base
    # Very small movement - just enough for S2 to be visible
    sacrum_end = sacrum_start + 0.015 * edge_direction  # tiny movement down
    
    sacrum_path = [sacrum_start, sacrum_end]
    sacrum_pts = interpolate_segment(sacrum_path, 5)

    # LAST sacrum point = coccyx start
    sacrum_end_final = np.array(sacrum_pts[-1], dtype=float)

    # ----- Coccyx: continues from sacrum endpoint (Co1–Co4)
    coccyx_start = sacrum_end_final
    
    # End point: continue with similar small distance
    edge_direction = wrist - pinky_base
    coccyx_end = coccyx_start + 0.015 * edge_direction  # similar tiny movement

    coccyx_path = [coccyx_start, coccyx_end]
    coccyx_pts = interpolate_segment(coccyx_path, 4)


    to_int = lambda arr: [(int(x), int(y)) for (x, y) in arr]

    return {
        "Cervical (C1–C7)": to_int(cervical_pts),
        "Thoracic (T1–T12)": to_int(thoracic_pts),
        "Lumbar (L1–L5)": to_int(lumbar_pts),   # overridden dynamically
        "Sacrum": to_int(sacrum_pts),
        "Coccyx": to_int(coccyx_pts),
    }

def draw_spine_reflex_point(img, spinal_region, hand, rep_index):
    """
    Draw reflex point for selected region using virtual points:
    - Cervical, Thoracic, Sacrum, Coccyx → from compute_spine_points_for_region
    - Lumbar → dynamic virtual path based on reps (below ring finger → toward pinky)
    """
    h, w, _ = img.shape

    def LM_vec_abs(i):
        lm = hand.landmark[i]
        return np.array([lm.x * w, lm.y * h], dtype=float)

    if spinal_region == "Lumbar (L1–L5)":
        # Get landmarks
        wrist      = LM_vec_abs(0)
        mid_base   = LM_vec_abs(9)
        pinky_base = LM_vec_abs(17)
        
        # Lumbar starts from deep position near center of wrist
        lumbar_start = mid_base + 0.85 * (wrist - mid_base)
        
        # End point: right edge of palm below pinky finger at wrist level
        pinky_to_wrist_direction = wrist - pinky_base
        lumbar_end = pinky_base + 0.95 * pinky_to_wrist_direction  # very close to wrist on pinky side
        # Shift slightly outward toward palm edge
        outward_shift = (pinky_base - mid_base) * 0.2
        lumbar_end = lumbar_end + outward_shift

        lumbar_pts = interpolate_segment([lumbar_start, lumbar_end], 5)
        points = [(int(x), int(y)) for (x, y) in lumbar_pts]
    else:
        region_points_map = compute_spine_points_for_region(hand, img)
        points = region_points_map[spinal_region]

    if not points:
        return None, None

    # clamp index
    rep_index = max(0, min(rep_index, len(points) - 1))
    cx, cy = points[rep_index]

    cv2.circle(
        img,
        (cx, cy),
        int(st.session_state.pulse_radius),
        (0, 255, 0),
        3,
    )

    # Animate pulse
    st.session_state.pulse_radius += st.session_state.pulse_direction * 1.4
    if st.session_state.pulse_radius >= 40 or st.session_state.pulse_radius <= 20:
        st.session_state.pulse_direction *= -1

    return cx, cy

# ========== COUNTDOWN THREAD ==========
def run_countdown():
    # Voice sequence: Hold, 3, 2, 1, Release
    speak(HOLD_V)
    time.sleep(0.4)
    speak(T3_V)
    time.sleep(0.8)
    speak(T2_V)
    time.sleep(0.8)
    speak(T1_V)
    time.sleep(0.3)
    speak(RELEASE_V)

# ========== CAMERA SECTION ==========
FRAME = st.image([])
progress_box = st.empty()
counter_box = st.empty()

run_camera = st.checkbox("Start Camera")

if run_camera:
    speak(READY_V)
    time.sleep(0.4)
    speak(PRESS_V)

    # Download hand_landmarker.task model file if not exists
    import urllib.request
    import os
    MODEL_PATH = "hand_landmarker.task"
    if not os.path.exists(MODEL_PATH):
        try:
            url = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
            urllib.request.urlretrieve(url, MODEL_PATH)
        except Exception as e:
            MODEL_PATH = "/tmp/hand_landmarker.task"
            if not os.path.exists(MODEL_PATH):
                url = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
                urllib.request.urlretrieve(url, MODEL_PATH)

    from mediapipe.tasks import python
    from mediapipe.tasks.python import vision

    base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
    options = vision.HandLandmarkerOptions(
        base_options=base_options,
        num_hands=2,
        min_hand_detection_confidence=0.88,
        min_hand_presence_confidence=0.88,
        min_tracking_confidence=0.88
    )
    detector = vision.HandLandmarker.create_from_options(options)

    class HandWrapper:
        def __init__(self, landmarks):
            self.landmark = landmarks

    HAND_CONNECTIONS = [
        (0, 1), (1, 2), (2, 3), (3, 4),        # Thumb
        (0, 5), (5, 6), (6, 7), (7, 8),        # Index
        (5, 9), (9, 10), (10, 11), (11, 12),   # Middle
        (9, 13), (13, 14), (14, 15), (15, 16), # Ring
        (13, 17), (17, 18), (18, 19), (19, 20),# Pinky
        (0, 17)                                # Palm base
    ]

    def custom_draw_landmarks(image, hand_wrap):
        h_dim, w_dim, _ = image.shape
        # Draw connection lines with violet color matching the premium theme
        for p1, p2 in HAND_CONNECTIONS:
            lm1 = hand_wrap.landmark[p1]
            lm2 = hand_wrap.landmark[p2]
            pt1 = (int(lm1.x * w_dim), int(lm1.y * h_dim))
            pt2 = (int(lm2.x * w_dim), int(lm2.y * h_dim))
            cv2.line(image, pt1, pt2, (246, 92, 139), 2)
        # Draw joints with pink/magenta color
        for lm in hand_wrap.landmark:
            pt = (int(lm.x * w_dim), int(lm.y * h_dim))
            cv2.circle(image, pt, 4, (255, 0, 255), -1)

    cap = cv2.VideoCapture(0)

    count = 0
    stage = "waiting_press"
    distances = []
    SMOOTH = 5
    press_timer = None

    while count < target_reps:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Detect using Tasks API
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img)
        results = detector.detect(mp_image)

        if results.hand_landmarks and len(results.hand_landmarks) == 2:
            h1 = HandWrapper(results.hand_landmarks[0])
            h2 = HandWrapper(results.hand_landmarks[1])

            # Identify left and right by x-coordinate
            if h1.landmark[0].x < h2.landmark[0].x:
                left = h1
                right = h2
            else:
                left = h2
                right = h1

            target_hand = right if hand_choice == "Right Hand" else left
            pressing_hand = left if target_hand == right else right

            # Draw landmarks
            custom_draw_landmarks(img, target_hand)
            custom_draw_landmarks(img, pressing_hand)

            # ---- Draw correct vertebra reflex point for this region & rep ----
            cx, cy = draw_spine_reflex_point(img, spinal_region, target_hand, count)

            if cx is not None:
                # Compute distance between pressing index fingertip and reflex point
                h_img, w_img, _ = img.shape
                rx, ry = cx / w_img, cy / h_img  # normalized reflex point
                press_tip = pressing_hand.landmark[8]
                px, py = press_tip.x, press_tip.y

                dist = ((rx - px) ** 2 + (ry - py) ** 2) ** 0.5

                distances.append(dist)
                if len(distances) > SMOOTH:
                    distances.pop(0)
                smooth = sum(distances) / len(distances)
                now = time.time()

                # -------- STABLE PRESS DETECTION --------
                if stage == "waiting_press":
                    if smooth < PRESS_TH:
                        if press_timer is None:
                            press_timer = now
                        elif now - press_timer >= STABILITY_TIME:
                            # Start countdown in background
                            threading.Thread(target=run_countdown, daemon=True).start()
                            stage = "countdown_running"
                    else:
                        press_timer = None  # lost press, reset

                # -------- RELEASE DETECTION AFTER COUNTDOWN --------
                if stage == "countdown_running" and smooth > RELEASE_TH:
                    ding()
                    speak(GOOD_V)
                    count += 1
                    counter_box.success(f"Reps Completed: {count}/{target_reps}")
                    stage = "waiting_press"
                    press_timer = None
                    speak(PRESS_V)

        FRAME.image(img)
        progress_box.image(create_progress_circle((count / target_reps) * 100))

    cap.release()
    speak(GOOD_V)
    st.success("🎉 Session Completed for selected spinal reflex region")