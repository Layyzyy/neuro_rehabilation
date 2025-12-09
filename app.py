import streamlit as st
import cv2
import mediapipe as mp
import numpy as np
import time
import threading
import queue
import simpleaudio as sa
from PIL import Image, ImageDraw, ImageFont

# ========== AUDIO QUEUE (NO OVERLAP) ==========
audio_queue = queue.Queue()

def audio_player():
    while True:
        file = audio_queue.get()
        if file is None:
            break
        wave = sa.WaveObject.from_wave_file(file)
        wave.play().wait_done()
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

# ========== UI HEADER ==========
st.title("AI Assisted Neuro-Rehabilitation System")
st.subheader("Spinal Reflex Palm Therapy – Press • Hold • Release")

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
target_reps = plan["reps"]

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

    # ----- Lumbar: placeholder center path (L1–L5) – real path computed dynamically
    lumbar_anchor = 0.7 * ring_base + 0.3 * wrist
    lumbar_pts = interpolate_segment([lumbar_anchor, lumbar_anchor], 5)

    # ----- Sacrum: extreme right palm base under pinky, near wrist (S1–S5)
    # Inside palm, not outside.
    sacrum_start = 0.85 * wrist + 0.15 * pinky_base  # near wrist, slightly toward pinky
    sacrum_end = sacrum_start + 0.10 * (wrist - pinky_base)  # small drop
    sacrum_path = [sacrum_start, sacrum_end]
    sacrum_pts = interpolate_segment(sacrum_path, 5)

    # ----- Coccyx: below sacrum (Co1–Co4), still within palm area
    coccyx_start = sacrum_end + 0.08 * (wrist - pinky_base)
    coccyx_end   = sacrum_end + 0.18 * (wrist - pinky_base)
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
        ring_base  = LM_vec_abs(13)
        wrist      = LM_vec_abs(0)
        pinky_base = LM_vec_abs(17)

        # Starting lumbar: below ring finger, near wrist (on palm)
        lumbar_start = ring_base + 0.9 * (wrist - ring_base)

        # Target external anchor toward pinky side (virtual end point)
        external_anchor = pinky_base + 0.25 * (pinky_base - wrist)

        # Gradual progression in first 3 reps
        shift_factor = min(rep_index / 3.0, 1.0)
        lumbar_end = lumbar_start + shift_factor * (external_anchor - lumbar_start)

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

    cap = cv2.VideoCapture(0)
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        max_num_hands=2,
        min_detection_confidence=0.88,
        min_tracking_confidence=0.88,
    )
    mp_draw = mp.solutions.drawing_utils

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
        results = hands.process(img)

        if results.multi_hand_landmarks and len(results.multi_hand_landmarks) == 2:
            h1, h2 = results.multi_hand_landmarks

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
            mp_draw.draw_landmarks(img, target_hand, mp_hands.HAND_CONNECTIONS)
            mp_draw.draw_landmarks(img, pressing_hand, mp_hands.HAND_CONNECTIONS)

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
