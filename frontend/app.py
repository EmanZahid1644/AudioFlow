import streamlit as st
import requests
import textwrap


# ============================================================
# CONFIGURATION
# ============================================================

BACKEND_URL = "https://audioflow-backend-worx.onrender.com"

st.set_page_config(
    page_title="AudioFlow — AI Voice Studio",
    page_icon="🎧",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# SESSION STATE
# ============================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user" not in st.session_state:
    st.session_state.user = None

if "token" not in st.session_state:
    st.session_state.token = None

if "page" not in st.session_state:
    st.session_state.page = "dashboard"

if "generated_audio" not in st.session_state:
    st.session_state.generated_audio = None


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def auth_headers():
    return {
        "Authorization": f"Bearer {st.session_state.token}"
    }


def logout():
    st.session_state.logged_in = False
    st.session_state.user = None
    st.session_state.token = None
    st.session_state.page = "login"
    st.session_state.generated_audio = None
    st.rerun()


# ============================================================
# PREMIUM SAAS CSS (LINEAR / VERCEL / ELEVENLABS INSPIRED)
# ============================================================

st.markdown(
    textwrap.dedent("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        box-sizing: border-box;
    }

    /* Hide default footer and burger menu, but KEEP header transparent so sidebar expand/collapse button works */
    #MainMenu, footer {
        visibility: hidden;
    }

    [data-testid="stHeader"] {
        background: transparent !important;
        z-index: 100 !important;
    }

    [data-testid="stHeader"] button, [data-testid="stHeader"] a {
        color: #FFFFFF !important;
    }

    .stApp {
        background-color: #08090D;
        color: #FFFFFF;
    }

    /* Layout & Spacing */
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 3rem !important;
        max-width: 1200px !important;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #0E1016 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
        padding-top: 0.5rem;
    }

    [data-testid="stSidebar"] .stButton button {
        background: transparent;
        border: 1px solid transparent;
        color: #8B91A1;
        font-weight: 500;
        font-size: 14px;
        text-align: left;
        justify-content: flex-start;
        padding: 10px 14px;
        border-radius: 8px;
        transition: all 0.2s ease;
        box-shadow: none;
    }

    [data-testid="stSidebar"] .stButton button:hover {
        background: #181B26;
        color: #FFFFFF;
        border-color: rgba(255, 255, 255, 0.05);
        transform: none;
        box-shadow: none;
    }

    .nav-active button {
        background: rgba(139, 92, 246, 0.15) !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(139, 92, 246, 0.3) !important;
        font-weight: 600 !important;
    }

    /* SaaS Cards */
    .saas-card {
        background: #131620;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        transition: border-color 0.2s ease;
    }

    .saas-card:hover {
        border-color: rgba(255, 255, 255, 0.15);
    }

    .saas-card-subtle {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 12px;
        padding: 18px;
    }

    /* Buttons */
    .stButton button {
        background: linear-gradient(135deg, #8B5CF6, #06B6D4);
        color: #FFFFFF;
        font-weight: 600;
        font-size: 14px;
        border-radius: 10px;
        border: none;
        padding: 12px 20px;
        transition: all 0.2s ease;
        box-shadow: 0 4px 16px rgba(139, 92, 246, 0.25);
    }

    .stButton button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 20px rgba(139, 92, 246, 0.4);
    }

    /* Secondary Button Override */
    .sec-btn button {
        background: #181B26 !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: #FFFFFF !important;
        box-shadow: none !important;
    }
    .sec-btn button:hover {
        background: #202433 !important;
        border-color: rgba(255, 255, 255, 0.2) !important;
    }

    /* Form Controls */
    .stTextInput input, .stTextArea textarea {
        background-color: #131620 !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 10px !important;
        color: #FFFFFF !important;
        font-size: 14px !important;
    }

    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #8B5CF6 !important;
        box-shadow: 0 0 0 2px rgba(139, 92, 246, 0.2) !important;
    }

    [data-baseweb="select"] > div {
        background-color: #131620 !important;
        border-color: rgba(255, 255, 255, 0.08) !important;
        border-radius: 10px !important;
    }

    /* File Uploader */
    .stFileUploader > div > div {
        background: #131620 !important;
        border: 2px dashed rgba(255, 255, 255, 0.12) !important;
        border-radius: 12px !important;
        padding: 24px !important;
    }

    /* Slider */
    .stSlider > div > div > div > div {
        background-color: #8B5CF6 !important;
    }

    /* Metrics */
    [data-testid="stMetric"] {
        background: #131620;
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 12px;
        padding: 16px;
    }

    [data-testid="stMetricLabel"] {
        color: #8B91A1 !important;
        font-size: 13px !important;
    }

    [data-testid="stMetricValue"] {
        color: #FFFFFF !important;
        font-weight: 700 !important;
    }

    /* Gradient Text */
    .gradient-brand {
        background: linear-gradient(135deg, #A78BFA, #06B6D4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* Tabs Container (Auth Card) */
    [data-testid="stTabs"] {
        background-color: #131620;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 20px;
        margin-top: 4px;
    }

    [data-testid="stTab"] {
        color: #8B91A1 !important;
        font-weight: 500 !important;
    }

    [aria-selected="true"] {
        color: #FFFFFF !important;
        font-weight: 700 !important;
    }

    /* Audio Player */
    audio {
        width: 100%;
        border-radius: 8px;
        margin-top: 10px;
    }
    </style>
    """),
    unsafe_allow_html=True
)


# ============================================================
# COMPONENT: SIDEBAR
# ============================================================

def render_sidebar():
    if not st.session_state.logged_in or not st.session_state.user:
        return

    user = st.session_state.user
    name = user.get("name", "User")
    email = user.get("email", "")
    initial = name[0].upper() if name else "U"
    current_page = st.session_state.get("page", "dashboard")

    with st.sidebar:
        # Brand Logo Header
        st.markdown(
            textwrap.dedent("""
            <div style="padding: 4px 0 16px; border-bottom: 1px solid rgba(255,255,255,0.06); margin-bottom: 16px;">
                <div style="display:flex; align-items:center; gap:10px;">
                    <div style="
                        width:36px; height:36px; border-radius:10px;
                        background:linear-gradient(135deg, #8b5cf6, #06b6d4);
                        display:flex; align-items:center; justify-content:center;
                        font-size:18px; color:white; font-weight:bold; flex-shrink:0;
                    ">🎧</div>
                    <div>
                        <div style="font-weight:700; font-size:16px; color:#FFFFFF !important; line-height:1.2;">AudioFlow</div>
                        <div style="font-size:11px; color:#8B91A1 !important; margin-top:2px;">AI Voice Studio</div>
                    </div>
                </div>
            </div>
            """),
            unsafe_allow_html=True
        )

        st.markdown('<div style="font-size:11px; font-weight:600; color:#8B91A1; letter-spacing:0.5px; margin-bottom:8px; padding-left:4px;">WORKSPACE</div>', unsafe_allow_html=True)

        navigation = [
            ("🏠", "Dashboard", "dashboard"),
            ("✨", "Voice Generation", "generate"),
            ("🪄", "Voice Cloning", "clone"),
            ("🎛️", "Voice Mixing", "mixer"),
        ]

        for icon, label, page in navigation:
            is_active = (current_page == page)
            btn_label = f"{icon}   {label}"
            
            if is_active:
                st.markdown('<div class="nav-active">', unsafe_allow_html=True)

            if st.button(btn_label, key=f"nav_{page}", use_container_width=True):
                st.session_state.page = page
                st.rerun()

            if is_active:
                st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<hr style='border:none; border-top:1px solid rgba(255,255,255,0.06); margin: 24px 0 16px 0;'>", unsafe_allow_html=True)

        # Profile Section
        st.markdown(
            textwrap.dedent(f"""
            <div style="
                padding: 10px 12px; border-radius: 12px;
                background: #131620; border: 1px solid rgba(255,255,255,0.06);
                display: flex; align-items: center; gap: 10px; margin-bottom: 12px;
            ">
                <div style="
                    width:34px; height:34px; border-radius:50%; flex-shrink:0;
                    background: linear-gradient(135deg,#8b5cf6,#06b6d4);
                    display:flex; align-items:center; justify-content:center;
                    font-weight:700; font-size:14px; color:white;
                ">{initial}</div>
                <div style="flex:1; min-width:0;">
                    <div style="font-size:13px; font-weight:600; color:#FFFFFF !important; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">{name}</div>
                    <div style="font-size:11px; color:#8B91A1 !important; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">{email}</div>
                </div>
            </div>
            """),
            unsafe_allow_html=True
        )

        if st.button("🚪   Logout", key="logout_btn", use_container_width=True):
            logout()


# ============================================================
# COMPONENT: PAGE HEADER
# ============================================================

def render_page_header(title: str, subtitle: str, icon: str = ""):
    header_html = f"""
    <div style="margin-bottom: 24px;">
        <div style="display:flex; align-items:center; gap:10px;">
            {f'<span style="font-size:28px;">{icon}</span>' if icon else ''}
            <h1 style="font-size:26px; font-weight:800; color:#FFFFFF !important; margin:0;">{title}</h1>
        </div>
        <p style="font-size:14px; color:#8B91A1 !important; margin-top:4px;">{subtitle}</p>
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)


# ============================================================
# COMPONENT: AUDIO RESULT DISPLAY
# ============================================================

def render_audio_result(title: str, subtitle: str, audio_url: str, filename: str = ""):
    st.markdown(
        textwrap.dedent(f"""
        <div class="saas-card" style="border-color: rgba(16, 185, 129, 0.3); background: rgba(16, 185, 129, 0.04);">
            <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:8px;">
                <div style="font-weight:700; font-size:15px; color:#10B981 !important;">{title}</div>
                <div style="font-size:12px; color:#8B91A1 !important;">Powered by Cloudinary</div>
            </div>
            <div style="font-size:13px; color:#8B91A1 !important; margin-bottom:12px;">{subtitle}</div>
        </div>
        """),
        unsafe_allow_html=True
    )
    if audio_url:
        st.audio(audio_url, format="audio/wav")
        st.markdown(
            textwrap.dedent(f"""
            <div style="margin-top:10px; display:flex; justify-content:space-between; align-items:center;">
                <span style="font-size:12px; color:#8B91A1 !important;">File: {filename or 'audio.wav'}</span>
                <a href="{audio_url}" target="_blank" style="font-size:13px; color:#A78BFA; text-decoration:none; font-weight:600;">
                    🔗 Open / Download Audio ↗
                </a>
            </div>
            """),
            unsafe_allow_html=True
        )


# ============================================================
# PAGE: AUTHENTICATION (LOGIN / REGISTER)
# ============================================================

def auth_page():
    col1, col2, col3 = st.columns([1, 2.2, 1])
    with col2:
        st.markdown(
            textwrap.dedent("""
            <div style="text-align:center; padding: 10px 0 16px;">
                <div style="font-size:44px; line-height:1; margin-bottom:8px;">🎧</div>
                <div style="font-size:28px; font-weight:800; background:linear-gradient(135deg, #a78bfa, #06b6d4); -webkit-background-clip:text; -webkit-text-fill-color:transparent; display:inline-block;">AudioFlow</div>
                <div style="font-size:13px; color:#8B91A1 !important; margin-top:4px;">Premium AI Voice Studio</div>
            </div>
            """),
            unsafe_allow_html=True
        )

        login_tab, register_tab = st.tabs(["🔐 Sign In", "📝 Create Account"])

        # Login
        with login_tab:
            st.markdown("<br>", unsafe_allow_html=True)
            email = st.text_input("Email Address", key="login_email", placeholder="you@example.com")
            password = st.text_input("Password", type="password", key="login_password", placeholder="••••••••")
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Sign In ➔", key="login_btn", use_container_width=True):
                if not email or not password:
                    st.error("Please fill in all fields.")
                else:
                    try:
                        res = requests.post(f"{BACKEND_URL}/login", json={"email": email, "password": password}, timeout=30)
                        data = res.json() if res.status_code == 200 else {}
                        if res.status_code == 200 and data.get("success"):
                            st.session_state.logged_in = True
                            st.session_state.user = data.get("user")
                            st.session_state.token = data.get("access_token")
                            st.session_state.page = "dashboard"
                            st.success("🎉 Sign in successful!")
                            st.rerun()
                        else:
                            st.error(data.get("message", data.get("detail", "Invalid email or password.")))
                    except Exception as e:
                        st.error(f"Connection error: {e}")

        # Register
        with register_tab:
            st.markdown("<br>", unsafe_allow_html=True)
            name = st.text_input("Full Name", key="reg_name", placeholder="Eman")
            email = st.text_input("Email Address", key="reg_email", placeholder="you@example.com")
            password = st.text_input("Password", type="password", key="reg_password", placeholder="Create password")

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Create Account ➔", key="reg_btn", use_container_width=True):
                if not name or not email or not password:
                    st.error("Please fill in all fields.")
                else:
                    try:
                        res = requests.post(f"{BACKEND_URL}/register", json={"name": name, "email": email, "password": password}, timeout=30)
                        data = res.json() if res.status_code == 200 else {}
                        if res.status_code == 200 and data.get("success"):
                            st.success("🎉 Account created successfully! Please sign in.")
                        else:
                            st.error(data.get("message", data.get("detail", "Registration failed.")))
                    except Exception as e:
                        st.error(f"Connection error: {e}")



# ============================================================
# PAGE: DASHBOARD
# ============================================================

def dashboard():
    if not st.session_state.user:
        logout()
        return

    render_sidebar()
    name = st.session_state.user.get("name", "User")

    # Hero Banner
    st.markdown(
        textwrap.dedent(f"""
        <div class="saas-card" style="background: linear-gradient(135deg, rgba(139, 92, 246, 0.08), rgba(6, 182, 212, 0.08)); border-color: rgba(139, 92, 246, 0.2);">
            <div style="font-size:12px; font-weight:700; color:#A78BFA; letter-spacing:0.5px; margin-bottom:8px;">WELCOME TO AUDIOFLOW</div>
            <h1 style="font-size:28px; font-weight:800; margin:0 0 8px 0; color:#FFFFFF !important;">Good evening, {name} 👋</h1>
            <p style="font-size:14px; color:#8B91A1 !important; margin:0;">Create natural AI voices with Kokoro AI & Pocket TTS neural speech synthesis.</p>
        </div>
        """),
        unsafe_allow_html=True
    )

    # Compact Stats Row
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Generated Speech", "Active", delta="Kokoro 82M")
    with c2:
        st.metric("Cloud Storage", "Cloudinary", delta="Secure SSL")
    with c3:
        st.metric("Voice Cloning", "Pocket TTS", delta="Reference WAV")
    with c4:
        st.metric("Engine Status", "Online", delta="100% Operational")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div style="font-size:16px; font-weight:700; color:#FFFFFF; margin-bottom:16px;">AI Voice Studios</div>', unsafe_allow_html=True)

    # Feature Cards
    f1, f2, f3 = st.columns(3)
    with f1:
        st.markdown(
            textwrap.dedent("""
            <div class="saas-card">
                <div style="font-size:32px; margin-bottom:12px;">✨</div>
                <div style="font-weight:700; font-size:16px; color:#FFFFFF !important;">Voice Generation</div>
                <p style="font-size:13px; color:#8B91A1 !important; margin:6px 0 16px 0;">Turn text into natural American female and male speech with Kokoro.</p>
            </div>
            """),
            unsafe_allow_html=True
        )
        if st.button("Open Voice Studio ➔", key="dash_gen", use_container_width=True):
            st.session_state.page = "generate"
            st.rerun()

    with f2:
        st.markdown(
            textwrap.dedent("""
            <div class="saas-card">
                <div style="font-size:32px; margin-bottom:12px;">🪄</div>
                <div style="font-weight:700; font-size:16px; color:#FFFFFF !important;">Voice Cloning</div>
                <p style="font-size:13px; color:#8B91A1 !important; margin:6px 0 16px 0;">Synthesize speech using a reference sample audio with Pocket TTS.</p>
            </div>
            """),
            unsafe_allow_html=True
        )
        if st.button("Open Voice Cloning ➔", key="dash_clone", use_container_width=True):
            st.session_state.page = "clone"
            st.rerun()

    with f3:
        st.markdown(
            textwrap.dedent("""
            <div class="saas-card">
                <div style="font-size:32px; margin-bottom:12px;">🎛️</div>
                <div style="font-weight:700; font-size:16px; color:#FFFFFF !important;">Voice Mixing</div>
                <p style="font-size:13px; color:#8B91A1 !important; margin:6px 0 16px 0;">Blend two Kokoro voice style vectors into a brand new hybrid voice.</p>
            </div>
            """),
            unsafe_allow_html=True
        )
        if st.button("Open Voice Mixer ➔", key="dash_mix", use_container_width=True):
            st.session_state.page = "mixer"
            st.rerun()


# ============================================================
# PAGE: VOICE GENERATION
# ============================================================

def generate_voice_page():
    if not st.session_state.user:
        logout()
        return

    render_sidebar()
    render_page_header("Voice Generation", "Turn text into natural speech using Kokoro AI.", "✨")

    voices = {
        "af_heart": "American Female - Heart",
        "af_bella": "American Female - Bella",
        "af_nicole": "American Female - Nicole",
        "af_sarah": "American Female - Sarah",
        "am_adam": "American Male - Adam",
        "am_michael": "American Male - Michael",
    }

    col1, col2 = st.columns([2, 1])

    with col1:
        text = st.text_area(
            "Text to Speech",
            placeholder="Enter the text you want Kokoro AI to speak...",
            height=240
        )
        char_count = len(text)
        st.markdown(f'<div style="text-align:right; font-size:12px; color:#8B91A1;">Characters: {char_count} / 1000</div>', unsafe_allow_html=True)

    with col2:
        voice = st.selectbox("Kokoro Voice", options=list(voices.keys()), format_func=lambda x: voices[x])
        speed = st.slider("Speech Speed", min_value=0.5, max_value=2.0, value=1.0, step=0.1)

        st.markdown("<br>", unsafe_allow_html=True)
        generate = st.button("✨ Generate Voice", key="btn_gen_speech", use_container_width=True)

    if generate:
        if not text.strip():
            st.warning("Text cannot be empty.")
        else:
            try:
                with st.spinner("✨ Synthesizing speech with Kokoro AI..."):
                    res = requests.post(
                        f"{BACKEND_URL}/generate-voice",
                        headers=auth_headers(),
                        json={"text": text, "voice": voice, "speed": speed},
                        timeout=180
                    )
                data = res.json() if res.status_code == 200 else {}
                if res.status_code == 401:
                    st.error("🔐 Session expired. Please sign in again.")
                    logout()
                elif res.status_code == 200 and data.get("success"):
                    st.success("🎉 Voice generated successfully!")
                    render_audio_result(
                        "Generated Audio Result",
                        f"Voice: {voices.get(voice, voice)} • Speed: {speed}x",
                        data.get("url"),
                        data.get("filename")
                    )
                else:
                    st.error(data.get("error", data.get("message", data.get("detail", "Voice generation failed."))))
            except Exception as e:
                st.error(f"❌ Connection error: {e}")


# ============================================================
# PAGE: VOICE CLONING
# ============================================================

def clone_page():
    if not st.session_state.user:
        logout()
        return

    render_sidebar()
    render_page_header("Voice Cloning", "Create speech using a reference sample voice. Powered by Pocket TTS.", "🪄")

    col1, col2 = st.columns([2, 1])

    with col1:
        text = st.text_area(
            "Text to Clone",
            placeholder="Enter the text you want Pocket TTS to speak in the target voice...",
            height=260
        )

    with col2:
        reference_audio = st.file_uploader(
            "Reference / Sample Audio",
            type=["wav", "mp3", "m4a", "ogg"],
            help="Upload a clean audio sample of the voice to clone."
        )

        language = st.selectbox(
            "Pocket TTS Language / Model",
            options=["english", "english_2026-01", "english_2026-04", "french_24l", "german_24l", "italian", "portuguese", "spanish_24l"],
            index=0
        )

        st.markdown("<br>", unsafe_allow_html=True)
        generate = st.button("🪄 Generate Cloned Voice", key="btn_clone_speech", use_container_width=True)

    if generate:
        if not text.strip():
            st.warning("Please enter text to synthesize.")
        elif reference_audio is None:
            st.warning("Please upload a reference audio sample.")
        else:
            try:
                with st.spinner("🪄 Analyzing reference voice & cloning with Pocket TTS..."):
                    res = requests.post(
                        f"{BACKEND_URL}/clone-voice",
                        headers=auth_headers(),
                        data={"text": text, "language": language},
                        files={"reference_audio": (reference_audio.name, reference_audio, reference_audio.type)},
                        timeout=300
                    )
                data = res.json() if res.status_code == 200 else {}
                if res.status_code == 401:
                    st.error("🔐 Session expired. Please sign in again.")
                    logout()
                elif res.status_code == 200 and data.get("success"):
                    st.success("🎉 Voice cloned successfully!")
                    render_audio_result(
                        "Cloned Audio Result",
                        f"Language/Model: {language} • Powered by Pocket TTS & Cloudinary",
                        data.get("audio_url") or data.get("url"),
                        reference_audio.name
                    )
                else:
                    st.error(data.get("error", data.get("message", data.get("detail", "Voice cloning failed."))))
            except Exception as e:
                st.error(f"❌ Connection error: {e}")


# ============================================================
# PAGE: VOICE MIXING (HYBRID VOICE CREATION)
# ============================================================

def voice_mixing_page():
    if not st.session_state.user:
        logout()
        return

    render_sidebar()
    render_page_header("Voice Mixing", "Blend two Kokoro voice styles into one new hybrid voice.", "🎛️")

    voices = {
        "af_heart": "American Female - Heart",
        "af_bella": "American Female - Bella",
        "af_nicole": "American Female - Nicole",
        "af_sarah": "American Female - Sarah",
        "am_adam": "American Male - Adam",
        "am_michael": "American Male - Michael",
    }
    voice_keys = list(voices.keys())

    col1, col2 = st.columns([1, 1])

    with col1:
        voice_a = st.selectbox("Voice A", options=voice_keys, index=0, format_func=lambda x: voices[x], key="mix_v_a")

    with col2:
        voice_b = st.selectbox("Voice B", options=voice_keys, index=4 if len(voice_keys) > 4 else 1, format_func=lambda x: voices[x], key="mix_v_b")

    st.markdown("<br>", unsafe_allow_html=True)

    mix_percent = st.slider("Mix Balance", min_value=0, max_value=100, value=50, step=1, help="0% = 100% Voice A, 50% = 50% Voice A + 50% Voice B, 100% = 100% Voice B")
    weight = mix_percent / 100.0
    percent_a = 100 - mix_percent
    percent_b = mix_percent

    # Visual Balance Bar
    st.markdown(
        textwrap.dedent(f"""
        <div class="saas-card-subtle" style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px;">
            <div style="font-weight:600; color:#A78BFA;">Voice A ({percent_a}%)</div>
            <div style="font-size:13px; color:#8B91A1;">Voice A  ◀──────●──────▶  Voice B</div>
            <div style="font-weight:600; color:#06B6D4;">Voice B ({percent_b}%)</div>
        </div>
        """),
        unsafe_allow_html=True
    )

    text = st.text_area("Text", placeholder="Enter text for your new hybrid voice to speak...", height=180)

    st.markdown("<br>", unsafe_allow_html=True)
    generate = st.button("🎛️ Generate Hybrid Voice", key="btn_mix_speech", use_container_width=True)

    if generate:
        if not text.strip():
            st.warning("Text cannot be empty.")
        elif voice_a == voice_b:
            st.error("Voice A and Voice B must be different.")
        else:
            try:
                with st.spinner("🎛️ Interpolating voice style vectors & synthesizing hybrid voice..."):
                    res = requests.post(
                        f"{BACKEND_URL}/voice/mix",
                        headers=auth_headers(),
                        json={"voice_a": voice_a, "voice_b": voice_b, "weight": weight, "text": text},
                        timeout=300
                    )
                data = res.json() if res.status_code == 200 else {}
                if res.status_code == 401:
                    st.error("🔐 Session expired. Please sign in again.")
                    logout()
                elif res.status_code == 200 and data.get("success"):
                    st.success("🎉 Hybrid voice generated successfully!")
                    render_audio_result(
                        "✨ Hybrid Voice Result",
                        f"Voice A: {voices.get(voice_a, voice_a)} ({percent_a}%) • Voice B: {voices.get(voice_b, voice_b)} ({percent_b}%)",
                        data.get("audio_url") or data.get("url"),
                        data.get("filename")
                    )
                else:
                    detail = data.get("detail")
                    err = detail if isinstance(detail, str) else data.get("error", data.get("message", "Voice mixing failed."))
                    st.error(f"❌ {err}")
            except Exception as e:
                st.error(f"❌ Connection error: {e}")


# ============================================================
# ROUTER
# ============================================================

if st.session_state.logged_in:
    page = st.session_state.get("page", "dashboard")
    if page == "dashboard":
        dashboard()
    elif page == "generate":
        generate_voice_page()
    elif page == "clone":
        clone_page()
    elif page == "mixer":
        voice_mixing_page()
    else:
        dashboard()
else:
    auth_page()
