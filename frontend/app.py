import streamlit as st
import requests


# =========================
# CONFIG
# =========================

BACKEND_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="AudioFlow",
    page_icon="🎧",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# =========================
# SESSION
# =========================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user" not in st.session_state:
    st.session_state.user = None

if "token" not in st.session_state:
    st.session_state.token = None

if "page" not in st.session_state:
    st.session_state.page = "login"

if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"


# =========================
# PREMIUM CSS
# =========================

st.markdown(
"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

* {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    box-sizing: border-box;
}

#MainMenu { display: none; }
footer { display: none; }
header { display: none; }

.stApp {
    background: #0a0a0f;
    background-image: 
        radial-gradient(ellipse at 10% 20%, rgba(120, 80, 240, 0.15) 0%, transparent 50%),
        radial-gradient(ellipse at 90% 80%, rgba(6, 182, 212, 0.10) 0%, transparent 50%),
        radial-gradient(ellipse at 50% 50%, rgba(15, 15, 25, 0.8) 0%, transparent 100%);
    min-height: 100vh;
}

/* ===== ANIMATIONS ===== */
@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(30px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

@keyframes slideIn {
    from {
        opacity: 0;
        transform: translateX(-20px);
    }
    to {
        opacity: 1;
        transform: translateX(0);
    }
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.6; }
}

@keyframes glow {
    0%, 100% { box-shadow: 0 0 20px rgba(139, 92, 246, 0.3); }
    50% { box-shadow: 0 0 40px rgba(139, 92, 246, 0.6); }
}

@keyframes shimmer {
    0% { background-position: -200% 0; }
    100% { background-position: 200% 0; }
}

/* ===== PAGE CONTAINER ===== */
.main-container {
    animation: fadeIn 0.6s cubic-bezier(0.4, 0, 0.2, 1);
    padding: 20px;
    max-width: 1400px;
    margin: 0 auto;
}

/* ===== GLASS CARD ===== */
.glass-card {
    background: rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 24px;
    padding: 32px;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
}

.glass-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, transparent 50%);
    pointer-events: none;
}

.glass-card:hover {
    transform: translateY(-4px) scale(1.01);
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.4);
    border-color: rgba(255, 255, 255, 0.15);
}

.glass-card-auth {
    background: rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 32px;
    padding: 48px;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
}

.glass-card-auth::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle at 30% 20%, rgba(139, 92, 246, 0.05) 0%, transparent 60%);
    pointer-events: none;
}

/* ===== TYPOGRAPHY ===== */
h1, h2, h3, p, label, span, div {
    color: #ffffff !important;
}

.gradient-text {
    background: linear-gradient(135deg, #a78bfa, #06b6d4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.text-muted {
    color: rgba(255, 255, 255, 0.5) !important;
    font-weight: 400;
}

.text-white {
    color: #ffffff !important;
}

/* ===== BUTTONS ===== */
.stButton button {
    width: 100%;
    height: 48px;
    border-radius: 14px;
    background: linear-gradient(135deg, #8b5cf6, #06b6d4);
    color: white;
    font-weight: 600;
    font-size: 15px;
    border: none;
    letter-spacing: 0.3px;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 4px 20px rgba(139, 92, 246, 0.3);
    position: relative;
    overflow: hidden;
    cursor: pointer;
}

.stButton button::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.15), transparent);
    transition: left 0.6s;
}

.stButton button:hover {
    transform: translateY(-2px) scale(1.02);
    box-shadow: 0 8px 30px rgba(139, 92, 246, 0.5);
}

.stButton button:hover::before {
    left: 100%;
}

.stButton button:active {
    transform: scale(0.96);
}

.stButton button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: none !important;
}

/* Secondary button style */
.btn-secondary {
    background: rgba(255, 255, 255, 0.08) !important;
    box-shadow: none !important;
}

.btn-secondary:hover {
    background: rgba(255, 255, 255, 0.15) !important;
    box-shadow: 0 4px 20px rgba(255, 255, 255, 0.1) !important;
}

/* ===== INPUTS ===== */
.stTextInput > div > div > input {
    background: rgba(255, 255, 255, 0.05) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 12px !important;
    padding: 12px 16px !important;
    color: white !important;
    font-size: 14px !important;
    transition: all 0.3s ease !important;
    height: 48px !important;
}

.stTextInput > div > div > input:focus {
    border-color: #8b5cf6 !important;
    box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.2) !important;
    background: rgba(255, 255, 255, 0.08) !important;
}

.stTextInput > div > div > input::placeholder {
    color: rgba(255, 255, 255, 0.3) !important;
}

/* ===== FILE UPLOADER ===== */
.stFileUploader > div > div {
    background: rgba(255, 255, 255, 0.03) !important;
    border: 2px dashed rgba(255, 255, 255, 0.1) !important;
    border-radius: 16px !important;
    padding: 40px !important;
    transition: all 0.3s ease !important;
    text-align: center !important;
}

.stFileUploader > div > div:hover {
    border-color: #8b5cf6 !important;
    background: rgba(139, 92, 246, 0.05) !important;
    transform: translateY(-2px);
}

.stFileUploader > div > div > div {
    color: rgba(255, 255, 255, 0.6) !important;
}

/* ===== METRICS ===== */
[data-testid="stMetric"] {
    background: rgba(255, 255, 255, 0.03);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 16px;
    padding: 20px;
    transition: all 0.3s ease;
}

[data-testid="stMetric"]:hover {
    transform: translateY(-2px);
    border-color: rgba(139, 92, 246, 0.3);
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3);
}

[data-testid="stMetric"] label {
    color: rgba(255, 255, 255, 0.6) !important;
    font-weight: 500 !important;
}

[data-testid="stMetric"] [data-testid="stMetricValue"] {
    color: white !important;
    font-weight: 700 !important;
}

/* ===== SIDEBAR ===== */
[data-testid="stSidebar"] {
    background: rgba(10, 10, 15, 0.95) !important;
    backdrop-filter: blur(20px);
    border-right: 1px solid rgba(255, 255, 255, 0.05);
}

[data-testid="stSidebar"] .stButton button {
    background: rgba(255, 255, 255, 0.05);
    box-shadow: none;
    height: 42px;
}

[data-testid="stSidebar"] .stButton button:hover {
    background: rgba(139, 92, 246, 0.2);
    box-shadow: 0 4px 20px rgba(139, 92, 246, 0.2);
}

/* ===== DIVIDERS ===== */
hr {
    border: none !important;
    height: 1px !important;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent) !important;
    margin: 20px 0 !important;
}

/* ===== ALERTS ===== */
.stAlert {
    border-radius: 12px !important;
    border: none !important;
    background: rgba(255, 255, 255, 0.05) !important;
    backdrop-filter: blur(10px);
    padding: 16px !important;
}

.stAlert > div {
    color: white !important;
}

.stAlert svg {
    fill: white !important;
}

/* Success */
.stAlert[data-baseweb="notification"]:first-child {
    border-left: 3px solid #10b981 !important;
}

/* Error */
.stAlert[data-baseweb="notification"]:nth-child(2) {
    border-left: 3px solid #ef4444 !important;
}

/* Info */
.stAlert[data-baseweb="notification"]:nth-child(3) {
    border-left: 3px solid #3b82f6 !important;
}

/* ===== SPINNER ===== */
.stSpinner > div {
    border-color: #8b5cf6 !important;
}

/* ===== TABS ===== */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: rgba(255, 255, 255, 0.03);
    border-radius: 16px;
    padding: 6px;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 12px;
    padding: 10px 24px;
    font-weight: 500;
    color: rgba(255, 255, 255, 0.5);
    transition: all 0.3s ease;
}

.stTabs [data-baseweb="tab"]:hover {
    color: white;
    background: rgba(255, 255, 255, 0.05);
}

.stTabs [data-baseweb="tab"][aria-selected="true"] {
    background: rgba(139, 92, 246, 0.2);
    color: white;
    border-bottom: 2px solid #8b5cf6;
}

/* ===== RESPONSIVE ===== */
@media (max-width: 768px) {
    .glass-card, .glass-card-auth {
        padding: 20px;
        border-radius: 16px;
    }
    
    .stButton button {
        height: 42px;
        font-size: 14px;
    }
    
    .main-container {
        padding: 12px;
    }
}

/* ===== CUSTOM COMPONENTS ===== */
.upload-zone {
    background: rgba(255, 255, 255, 0.02);
    border-radius: 16px;
    padding: 24px;
    border: 1px solid rgba(255, 255, 255, 0.05);
}

.upload-zone:hover {
    border-color: rgba(139, 92, 246, 0.3);
    background: rgba(139, 92, 246, 0.03);
}

.track-item {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 12px;
    transition: all 0.3s ease;
}

.track-item:hover {
    background: rgba(255, 255, 255, 0.06);
    border-color: rgba(139, 92, 246, 0.2);
    transform: translateX(4px);
}

.auth-header {
    text-align: center;
    margin-bottom: 40px;
    animation: fadeInUp 0.8s cubic-bezier(0.4, 0, 0.2, 1);
}

.auth-header .logo-icon {
    font-size: 56px;
    margin-bottom: 8px;
    display: inline-block;
    animation: pulse 2s ease-in-out infinite;
}

.auth-header .logo-text {
    font-size: 38px;
    font-weight: 800;
    background: linear-gradient(135deg, #a78bfa, #06b6d4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.auth-header .subtitle {
    color: rgba(255, 255, 255, 0.4);
    font-size: 14px;
    margin-top: 4px;
}
</style>
""",
unsafe_allow_html=True
)


# =========================
# SIDEBAR COMPONENT
# =========================

def render_sidebar():
    if st.session_state.logged_in and st.session_state.user:
        with st.sidebar:
            st.markdown(
                f"""
                <div style="padding: 24px 0; text-align: center; border-bottom: 1px solid rgba(255,255,255,0.05); margin-bottom: 20px;">
                    <div style="width: 72px; height: 72px; border-radius: 50%; background: linear-gradient(135deg, #8b5cf6, #06b6d4); margin: 0 auto 12px; display: flex; align-items: center; justify-content: center; font-size: 32px; box-shadow: 0 8px 30px rgba(139, 92, 246, 0.3); transition: all 0.3s ease;">
                        {st.session_state.user['name'][0].upper()}
                    </div>
                    <div style="font-weight: 600; font-size: 17px; color: white;">{st.session_state.user['name']}</div>
                    <div style="color: rgba(255,255,255,0.4); font-size: 13px;">{st.session_state.user.get('email', '')}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Navigation buttons with icons
            nav_buttons = [
                ("🎧", "Dashboard", "dashboard"),
                ("📤", "Upload Audio", "upload"),
                ("📚", "Library", "library")
            ]
            
            for icon, label, page in nav_buttons:
                is_active = st.session_state.get("page") == page
                btn_class = "active" if is_active else ""
                
                if st.button(f"{icon} {label}", key=f"nav_{page}", use_container_width=True):
                    st.session_state.page = page
                    st.rerun()
            
            st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
            
            # Logout button
            if st.button("🚪 Logout", key="logout_sidebar", use_container_width=True):
                st.session_state.logged_in = False
                st.session_state.user = None
                st.session_state.token = None
                st.session_state.page = "login"
                st.rerun()


# =========================
# AUTH PAGE
# =========================

def auth_page():
    # Render centered auth container
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Logo / Brand
        st.markdown(
            """
            <div class="auth-header">
                <div class="logo-icon">🎧</div>
                <div class="logo-text">AudioFlow</div>
                <div class="subtitle">Premium Audio Cloud Platform</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Auth Card
        st.markdown(
            """
            <div class="glass-card-auth" style="animation: fadeInUp 0.6s cubic-bezier(0.4, 0, 0.2, 1);">
            """,
            unsafe_allow_html=True
        )
        
        # Toggle between Login/Register
        auth_tabs = st.tabs(["🔐 Login", "📝 Register"])
        
        # ========== LOGIN TAB ==========
        with auth_tabs[0]:
            st.markdown(
                """
                <div style="margin-bottom: 28px;">
                    <div style="font-size: 22px; font-weight: 700; color: white; margin-bottom: 4px;">Welcome Back</div>
                    <div style="color: rgba(255,255,255,0.4); font-size: 14px;">Sign in to continue to your workspace</div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            email = st.text_input(
                "Email Address",
                key="login_email",
                placeholder="you@example.com"
            )
            
            password = st.text_input(
                "Password",
                type="password",
                key="login_password",
                placeholder="Enter your password"
            )
            
            if st.button("Sign In", key="login_btn"):
                if not email or not password:
                    st.error("Please fill in all fields")
                else:
                    try:
                        response = requests.post(
                            f"{BACKEND_URL}/login",
                            json={"email": email, "password": password}
                        )
                        result = response.json()
                        
                        if result.get("success"):
                            st.session_state.logged_in = True
                            st.session_state.user = result["user"]
                            st.session_state.token = result["access_token"]
                            st.session_state.page = "dashboard"
                            st.success("🎉 Welcome back!")
                            st.rerun()
                        else:
                            st.error(result.get("message", "Login failed"))
                    except Exception as e:
                        st.error(f"Connection error: {e}")
        
        # ========== REGISTER TAB ==========
        with auth_tabs[1]:
            st.markdown(
                """
                <div style="margin-bottom: 28px;">
                    <div style="font-size: 22px; font-weight: 700; color: white; margin-bottom: 4px;">Create Account</div>
                    <div style="color: rgba(255,255,255,0.4); font-size: 14px;">Start your free trial today</div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            name = st.text_input(
                "Full Name",
                key="reg_name",
                placeholder="John Doe"
            )
            
            email = st.text_input(
                "Email Address",
                key="reg_email",
                placeholder="you@example.com"
            )
            
            password = st.text_input(
                "Password",
                type="password",
                key="reg_password",
                placeholder="Create a strong password"
            )
            
            if st.button("Create Account", key="register_btn"):
                if not name or not email or not password:
                    st.error("Please fill in all fields")
                else:
                    try:
                        response = requests.post(
                            f"{BACKEND_URL}/register",
                            json={"name": name, "email": email, "password": password}
                        )
                        result = response.json()
                        
                        if result.get("success"):
                            st.success("🎉 Account created! Please login.")
                            st.balloons()
                        else:
                            st.error(result.get("message", "Registration failed"))
                    except Exception as e:
                        st.error(f"Connection error: {e}")
        
        st.markdown("</div>", unsafe_allow_html=True)


# =========================
# WELCOME HERO
# =========================

def render_welcome_hero():
    user = st.session_state.user
    st.markdown(
        f"""
        <div style="animation: fadeInUp 0.6s cubic-bezier(0.4, 0, 0.2, 1); margin-bottom: 32px;">
            <div class="glass-card" style="padding: 40px; background: rgba(139, 92, 246, 0.08); border-color: rgba(139, 92, 246, 0.2);">
                <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 16px; flex-wrap: wrap;">
                    <span style="background: rgba(139, 92, 246, 0.2); padding: 6px 16px; border-radius: 100px; font-size: 12px; font-weight: 600; color: #a78bfa; border: 1px solid rgba(139, 92, 246, 0.2); display: inline-flex; align-items: center; gap: 6px;">
                        ✨ PRO
                    </span>
                    <span style="color: rgba(255,255,255,0.2); font-size: 12px;">•</span>
                    <span style="color: rgba(255,255,255,0.3); font-size: 13px; background: rgba(255,255,255,0.05); padding: 4px 12px; border-radius: 100px;">v2.0</span>
                    <span style="color: rgba(255,255,255,0.2); font-size: 12px;">•</span>
                    <span style="color: rgba(255,255,255,0.3); font-size: 13px; background: rgba(6, 182, 212, 0.1); padding: 4px 12px; border-radius: 100px; border: 1px solid rgba(6, 182, 212, 0.1);">⚡ Active</span>
                </div>
                <div style="font-size: 38px; font-weight: 800; margin-bottom: 8px; line-height: 1.2;">
                    Welcome back, <span class="gradient-text">{user['name']}</span>
                </div>
                <div style="font-size: 18px; color: rgba(255,255,255,0.5); margin-bottom: 24px; font-weight: 400;">
                    Your intelligent audio workspace is ready.
                </div>
                <div style="display: flex; gap: 12px; flex-wrap: wrap;">
                    <span style="background: rgba(255,255,255,0.05); padding: 8px 20px; border-radius: 100px; font-size: 13px; border: 1px solid rgba(255,255,255,0.05); display: inline-flex; align-items: center; gap: 8px;">
                        🎵 <span style="color: rgba(255,255,255,0.6);">0 tracks uploaded</span>
                    </span>
                    <span style="background: rgba(255,255,255,0.05); padding: 8px 20px; border-radius: 100px; font-size: 13px; border: 1px solid rgba(255,255,255,0.05); display: inline-flex; align-items: center; gap: 8px;">
                        📊 <span style="color: rgba(255,255,255,0.6);">0% storage used</span>
                    </span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


# =========================
# DASHBOARD
# =========================

def dashboard():
    if not st.session_state.user:
        st.session_state.logged_in = False
        st.rerun()
    
    # Render sidebar
    render_sidebar()
    
    # Main content
    st.markdown("<div class='main-container'>", unsafe_allow_html=True)
    
    # Welcome hero
    render_welcome_hero()
    
    # Quick Stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🎵 Total Tracks", "0", "+0")
    with col2:
        st.metric("💾 Storage Used", "0 MB", "0%")
    with col3:
        st.metric("📤 Uploads", "0", "+0")
    with col4:
        st.metric("⚡ Status", "Active", "Online")
    
    st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)
    
    # Main action cards
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(
            """
            <div class="glass-card" style="text-align: center; padding: 40px 32px; cursor: pointer;">
                <div style="font-size: 48px; margin-bottom: 12px;">☁️</div>
                <div style="font-size: 20px; font-weight: 700; margin-bottom: 6px; color: white;">Upload Audio</div>
                <div style="color: rgba(255,255,255,0.4); font-size: 14px; margin-bottom: 16px;">Upload your audio files to the cloud securely</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("📤 Upload Now", key="dashboard_upload", use_container_width=True):
            st.session_state.page = "upload"
            st.rerun()
    
    with col2:
        st.markdown(
            """
            <div class="glass-card" style="text-align: center; padding: 40px 32px; cursor: pointer;">
                <div style="font-size: 48px; margin-bottom: 12px;">🎶</div>
                <div style="font-size: 20px; font-weight: 700; margin-bottom: 6px; color: white;">My Library</div>
                <div style="color: rgba(255,255,255,0.4); font-size: 14px; margin-bottom: 16px;">Browse and manage your audio collection</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("📚 Open Library", key="dashboard_library", use_container_width=True):
            st.session_state.page = "library"
            st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)


# =========================
# UPLOAD PAGE
# =========================

def upload_page():
    if not st.session_state.user:
        st.session_state.logged_in = False
        st.rerun()
    
    render_sidebar()
    
    st.markdown("<div class='main-container'>", unsafe_allow_html=True)
    
    # Back button
    col_back, col_title = st.columns([1, 5])
    with col_back:
        if st.button("← Back", key="back_upload", use_container_width=True):
            st.session_state.page = "dashboard"
            st.rerun()
    
    st.markdown(
        """
        <div style="animation: fadeInUp 0.6s cubic-bezier(0.4, 0, 0.2, 1); margin-top: 12px;">
            <div class="glass-card">
                <div style="font-size: 28px; font-weight: 700; margin-bottom: 4px; color: white;">☁ Upload Audio</div>
                <div style="color: rgba(255,255,255,0.4); font-size: 15px; margin-bottom: 28px;">Upload your audio files securely to the cloud</div>
                
                
        """,
        unsafe_allow_html=True
    )
    
    audio = st.file_uploader(
        "Choose Audio File",
        type=["mp3", "wav", "m4a", "ogg"],
        help="Supported formats: MP3, WAV, M4A, OGG"
    )
    
    if audio:
        st.markdown(
            f"""
            <div style="background: rgba(6, 182, 212, 0.1); border: 1px solid rgba(6, 182, 212, 0.2); border-radius: 12px; padding: 16px 20px; margin: 16px 0; animation: slideIn 0.3s ease;">
                <div style="display: flex; align-items: center; gap: 16px;">
                    <span style="font-size: 28px;">🎵</span>
                    <div style="flex: 1;">
                        <div style="font-weight: 600; color: white; font-size: 15px;">{audio.name}</div>
                        <div style="color: rgba(255,255,255,0.4); font-size: 13px;">{audio.size / 1024:.1f} KB • Ready to upload</div>
                    </div>
                    <span style="background: rgba(6, 182, 212, 0.2); padding: 4px 12px; border-radius: 100px; font-size: 12px; color: #06b6d4;">Ready</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    if st.button("⬆ Upload Audio", key="upload_btn"):
        if audio is None:
            st.warning("Please select an audio file first")
        else:
            headers = {"Authorization": f"Bearer {st.session_state.token}"}
            try:
                with st.spinner("Uploading..."):
                    response = requests.post(
                        f"{BACKEND_URL}/receive",
                        headers=headers,
                        files={"file": (audio.name, audio, audio.type)}
                    )
                result = response.json()
                if result.get("success"):
                    st.success("🎵 Audio uploaded successfully!")
                    st.balloons()
                else:
                    st.error(result.get("message", "Upload failed"))
            except Exception as e:
                st.error(f"Error: {e}")
    
    st.markdown(
        """
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown("</div>", unsafe_allow_html=True)


# =========================
# LIBRARY PAGE
# =========================

def library_page():
    if not st.session_state.user:
        st.session_state.logged_in = False
        st.rerun()
    
    render_sidebar()
    
    st.markdown("<div class='main-container'>", unsafe_allow_html=True)
    
    # Back button
    col_back, col_title = st.columns([1, 5])
    with col_back:
        if st.button("← Back", key="back_library", use_container_width=True):
            st.session_state.page = "dashboard"
            st.rerun()
    
    st.markdown(
        """
        <div style="animation: fadeInUp 0.6s cubic-bezier(0.4, 0, 0.2, 1); margin-top: 12px;">
            <div class="glass-card">
                <div style="font-size: 28px; font-weight: 700; margin-bottom: 4px; color: white;">🎶 My Library</div>
                <div style="color: rgba(255,255,255,0.4); font-size: 15px; margin-bottom: 28px;">Browse and manage your audio collection</div>
        """,
        unsafe_allow_html=True
    )
    
    if st.button("🔄 Load My Audios", key="library_btn", use_container_width=True):
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        try:
            response = requests.get(f"{BACKEND_URL}/audios", headers=headers)
            result = response.json()
            
            if result.get("count", 0) == 0:
                st.info("📭 No audio uploaded yet. Upload your first track!")
            else:
                st.success(f"🎵 Found {result['count']} tracks")
                
                for idx, audio in enumerate(result["audios"]):
                    st.markdown(
                        f"""
                        <div class="track-item">
                            <div style="display: flex; align-items: center; gap: 16px; flex-wrap: wrap;">
                                <span style="font-size: 28px;">🎵</span>
                                <div style="flex: 1; min-width: 150px;">
                                    <div style="font-weight: 600; color: white; font-size: 15px;">{audio['filename']}</div>
                                    <div style="color: rgba(255,255,255,0.3); font-size: 13px;">Track #{idx + 1}</div>
                                </div>
                                <a href="{audio['url']}" download style="background: rgba(139, 92, 246, 0.15); color: #a78bfa; text-decoration: none; padding: 8px 20px; border-radius: 10px; font-size: 14px; font-weight: 500; transition: all 0.3s ease; border: 1px solid rgba(139, 92, 246, 0.2);">
                                    ⬇ Download
                                </a>
                            </div>
                            <div style="margin-top: 14px;">
                                <audio controls style="width: 100%; border-radius: 8px; background: rgba(0,0,0,0.3);">
                                    <source src="{audio['url']}" type="audio/mpeg">
                                    Your browser does not support the audio element.
                                </audio>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
        except Exception as e:
            st.error(f"Error: {e}")
    
    st.markdown(
        """
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown("</div>", unsafe_allow_html=True)


# =========================
# ROUTER
# =========================

if st.session_state.logged_in:
    page = st.session_state.get("page", "dashboard")
    
    if page == "dashboard":
        dashboard()
    elif page == "upload":
        upload_page()
    elif page == "library":
        library_page()
    else:
        dashboard()
else:
    auth_page()