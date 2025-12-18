import streamlit as st
import time
import hashlib
import login_assets

# ========== LOGIN SYSTEM ==========
# Initialize session state for login
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""

# User credentials (in production, use a database)
# Password is hashed using SHA-256
USERS = {
    "user1": hashlib.sha256("password1".encode()).hexdigest(),
    "user2": hashlib.sha256("password2".encode()).hexdigest(),
    "user3": hashlib.sha256("password3".encode()).hexdigest(),
}

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_login(username, password):
    """Verify username and password"""
    if username in USERS:
        return USERS[username] == hash_password(password)
    return False

def login_page():
    """Display futuristic AI healthcare login page"""
    # Force wide mode for this page if possible, but usually must be first command.
    # We will just assume standard layout but use custom CSS to make it look full.
    
    st.markdown(f"""
        <style>
        /* Import Inter Font */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
        
        /* Global Styles */
        .stApp {{
            background-image: url("{login_assets.LOGIN_BG_B64}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
            font-family: 'Inter', sans-serif !important;
        }}
        /* Global - Hide scrollbars specifically for this immersive view */
        .stApp {{
            overflow: hidden;
        }}
        
        /* Remove default top padding to make it full screen-ish */
        .block-container {{
            padding: 4rem 3rem !important;
            max-width: 1200px;
            background-image: url("{login_assets.CONTAINER_BG_B64}");
            background-size: cover;
            background-position: center;
            border-radius: 30px;
            
            /* Fixed positioning relative to viewport to prevent scroll */
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -45%); /* Center vertically and horizontally */
            width: 90%;
            height: 80vh; /* Fixed height relative to viewport */
            
            box-shadow: 0 20px 50px rgba(0,0,0,0.5);
            border: 1px solid rgba(0, 200, 200, 0.2);
            
            /* Center internal content */
            display: flex;
            flex-direction: column;
            justify-content: center;
        }}
        
        /* Glassmorphism Container */
        .glass-container {{
            background: rgba(18, 40, 45, 0.65);
            backdrop-filter: blur(24px);
            -webkit-backdrop-filter: blur(24px);
            border-radius: 24px;
            border: 1px solid rgba(0, 200, 200, 0.15);
            padding: 3rem;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        }}
        
        /* Brand Section (Left) */
        .brand-title {{
            font-size: 3.5rem;
            font-weight: 800;
            background: linear-gradient(135deg, #fff 0%, #00d4d4 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
            letter-spacing: -1px;
        }}
        
        .brand-subtitle {{
            color: #a0e7e5;
            font-size: 1.25rem;
            font-weight: 400;
            margin-bottom: 2rem;
            opacity: 0.9;
        }}
        
        .brand-tagline {{
            color: #7dd3c0;
            font-size: 1rem;
            line-height: 1.6;
            opacity: 0.8;
            max-width: 90%;
        }}
        
        /* Login Card (Right) */
        /* Login Form Container - Replaces the separate card div */
        /* Login Form Container - Replaces the separate card div */
        [data-testid="stForm"] {{
            background: rgba(20, 45, 50, 0.5);
            backdrop-filter: blur(20px);
            border-radius: 24px;
            padding: 2.5rem 2rem;
            border: 1px solid rgba(0, 200, 200, 0.3);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }}

        .login-header {{
            color: #fff;
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 2rem;
            text-align: center;
        }}
        
        /* Input Fields - Solid White style */
        .stTextInput > div > div > input {{
            background: #ffffff !important;
            backdrop-filter: none !important;
            border: 1px solid rgba(255, 255, 255, 0.5) !important;
            color: #000 !important; /* Black text for solid white background */
            border-radius: 12px !important;
            padding: 1rem !important;
            font-size: 1rem !important;
            transition: all 0.3s ease;
        }}
        
        .stTextInput > div > div > input:focus {{
            border-color: #00d4d4 !important;
            background: #ffffff !important;
            box-shadow: 0 0 0 2px rgba(0, 212, 212, 0.3);
        }}
        
        .stTextInput > div > div > input::placeholder {{
            color: #666 !important;
            opacity: 1;
        }}
        
        /* Input Labels */
        .stTextInput > label {{
            color: #a0e7e5 !important;
            font-weight: 500 !important;
            margin-bottom: 0.5rem !important;
        }}
        
        /* Primary Button - Black like reference */
        .stButton > button {{
            background: linear-gradient(135deg, #1a1a1a 0%, #0a0a0a 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 0.9rem 2rem !important;
            font-weight: 600 !important;
            font-size: 1rem !important;
            width: 100% !important;
            transition: transform 0.2s ease, box-shadow 0.2s ease !important;
            margin-top: 1rem;
        }}
        
        .stButton > button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.6);
            background: linear-gradient(135deg, #2a2a2a 0%, #1a1a1a 100%) !important;
        }}
        
        /* Demo Creds Box */
        .demo-box {{
            margin-top: 2rem;
            padding: 1rem;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            font-size: 0.85rem;
            color: #ccc;
        }}
        
        /* Hide Streamlit elements */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        </style>
    """, unsafe_allow_html=True)
    
    # Split screen layout matching reference
    col_left, col_right = st.columns([1.3, 1], gap="large")
    
    with col_left:
        st.markdown('<div style="padding: 2rem 1rem;">', unsafe_allow_html=True)
        
        # Logo and brand
        st.markdown("""
            <div style="margin-bottom: 2rem;">
                <div style="font-size: 1.2rem; color: #a0e7e5; margin-bottom: 0.5rem;">🧠 NeuroRehab AI</div>
            </div>
        """, unsafe_allow_html=True)
        
        # Main heading
        st.markdown("""
            <h1 style="
                font-size: 3rem; 
                font-weight: 800; 
                color: white; 
                line-height: 1.2; 
                margin-bottom: 2rem;
            ">
                NeuroRehab AI: Revolutionizing<br>Spine Rehabilitation.
            </h1>
        """, unsafe_allow_html=True)
        
        # Description text
        st.markdown("""
            <p style="
                color: #7dd3c0; 
                font-size: 1rem; 
                line-height: 1.8; 
                max-width: 500px;
            ">
                HANDIFY AI transforms movement into meaning. <br>
                Where hand therapy meets intelligence. <br>
                Recovery, reimagined.
            </p>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_right:
        st.markdown('<div style="padding: 2rem 1rem;">', unsafe_allow_html=True)
        
        # Login Form
        with st.form("login_form"):
            st.markdown("""
                <div style="text-align: center;">
                    <p style="
                        color: white; 
                        font-size: 1.3rem; 
                        font-weight: 600; 
                        margin-bottom: 0.5rem;
                    ">
                        WELCOME BACK NEUROREHAB EXCLUSIVE MEMBER
                    </p>
                    <p style="
                        color: #7dd3c0; 
                        font-size: 0.85rem; 
                        margin-bottom: 2rem;
                    ">
                        LOG IN TO CONTINUE
                    </p>
                </div>
            """, unsafe_allow_html=True)
            
            # Input fields
            username = st.text_input("📧 Email", placeholder="binxeolazy2004@anas.com", key="login_username")
            password = st.text_input("🔒 Password", type="password", placeholder="••••••••", key="login_password")
            
            st.markdown('<div style="margin-top: 1rem;"></div>', unsafe_allow_html=True)
            
            # Login button
            submitted = st.form_submit_button("Proceed to my Account →", use_container_width=True)
            
            if submitted:
                if username and password:
                    if verify_login(username, password):
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.success("Welcome back!")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error("Invalid credentials")
                else:
                    st.warning("Please enter both fields")
        
        # Footer link
        st.markdown("""
            <p style="
                text-align: center; 
                color: #7dd3c0; 
                font-size: 0.85rem; 
                margin-top: 1rem;
            ">
                Having Issues with your Password?
            </p>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

def logout():
    """Logout function"""
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.rerun()
