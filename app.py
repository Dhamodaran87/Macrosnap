import json
import time

import streamlit as st
from google import genai
from google.genai import types
from twilio.rest import Client as TwilioClient

from prompts import SUMMARY_REQUEST_PROMPT, SYSTEM_PROMPT, WELCOME_MESSAGE_TEMPLATE


PRIMARY_MODEL = "gemini-3.8-flash"
FALLBACK_MODEL = "gemini-3.5-flash-lite"


st.set_page_config(
    page_title="MacroSnap",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    :root {
        color-scheme: dark;
    }

    * {
        font-family: 'Inter', sans-serif;
        box-sizing: border-box;
    }

    .stApp {
        background:
            radial-gradient(circle at 14% 0%, rgba(34, 197, 94, 0.10), transparent 24%),
            radial-gradient(circle at 92% 7%, rgba(16, 185, 129, 0.10), transparent 24%),
            linear-gradient(180deg, #061310 0%, #070b0f 48%, #05080c 100%);
    }

    [data-testid="stHeader"] {
        background: rgba(5, 9, 13, 0.74);
    }

    .block-container {
        max-width: 1400px;
        padding: 1.4rem 2rem 7rem;
    }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #071117 0%, #071016 100%);
        border-right: 1px solid rgba(255,255,255,0.07);
    }

    section[data-testid="stSidebar"] > div {
        padding: 1.1rem 0.9rem 1rem;
    }

    .brand {
        display: flex;
        align-items: center;
        gap: 11px;
        margin: 4px 8px 25px;
    }

    .brand-icon {
        width: 48px;
        height: 48px;
        border-radius: 16px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, #40ef94, #12b977);
        box-shadow: 0 12px 34px rgba(34,197,94,0.20);
        font-size: 24px;
    }

    .brand-name {
        color: #f8fafc;
        font-size: 21px;
        font-weight: 800;
        letter-spacing: -0.7px;
    }

    .brand-name span {
        color: #3eea8b;
    }

    .brand-caption {
        color: #6f8191;
        font-size: 10px;
        margin-top: 3px;
    }

    .sidebar-label {
        color: #5d7082;
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 1.1px;
        margin: 21px 8px 9px;
        text-transform: uppercase;
    }

    .profile-card,
    .sidebar-stat {
        background: rgba(14, 25, 32, 0.82);
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 16px;
        padding: 13px;
        margin: 0 3px;
    }

    .profile-row {
        display: flex;
        align-items: center;
        gap: 11px;
    }

    .avatar {
        width: 39px;
        height: 39px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        background: rgba(34,197,94,0.13);
        border: 1px solid rgba(34,197,94,0.21);
        font-size: 17px;
    }

    .profile-name {
        color: #f8fafc;
        font-size: 13px;
        font-weight: 700;
    }

    .profile-phone {
        color: #6f8292;
        font-size: 10px;
        margin-top: 3px;
    }

    .sidebar-footer {
        margin: 32px 8px 0;
        padding-top: 20px;
        border-top: 1px solid rgba(255,255,255,0.06);
        color: #718294;
        font-size: 10px;
        line-height: 1.65;
    }

    .page-title {
        color: #f8fafc;
        font-size: 31px;
        font-weight: 800;
        letter-spacing: -0.9px;
        margin: 0;
        margin-top: 30px;
    }

    .page-subtitle {
        color: #728596;
        font-size: 12px;
        margin-top: 4px;
        line-height: 1.6;
    }

    .online-status {
        display: inline-flex;
        align-items: center;
        gap: 7px;
        padding: 8px 12px;
        border-radius: 999px;
        background: rgba(34,197,94,0.07);
        border: 1px solid rgba(34,197,94,0.17);
        color: #7af4af;
        font-size: 10px;
        font-weight: 700;
        white-space: nowrap;
    }

    .online-dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: #31e88a;
        box-shadow: 0 0 12px rgba(49,232,138,0.8);
    }

    .hero {
        position: relative;
        overflow: hidden;
        min-height: 208px;
        border-radius: 24px;
        padding: 27px 30px;
        margin-top: 18px;
        border: 1px solid rgba(42,231,142,0.24);
        background:
            radial-gradient(circle at 82% 45%, rgba(38,214,129,0.19), transparent 20%),
            radial-gradient(circle at 8% 110%, rgba(26,177,108,0.12), transparent 30%),
            linear-gradient(135deg, rgba(5,42,37,0.96), rgba(7,23,29,0.95));
        box-shadow:
            inset 0 1px 0 rgba(255,255,255,0.04),
            0 22px 55px rgba(0,0,0,0.18);
    }

    .hero-kicker {
        display: inline-block;
        padding: 7px 11px;
        border-radius: 999px;
        color: #7af4af;
        background: rgba(36,224,133,0.10);
        border: 1px solid rgba(36,224,133,0.20);
        font-size: 9px;
        font-weight: 700;
    }

    .hero-title {
        color: #f8fafc;
        font-size: 28px;
        line-height: 1.1;
        font-weight: 800;
        letter-spacing: -0.9px;
        margin-top: 13px;
    }

    .hero-text {
        max-width: 680px;
        color: #a5b8c5;
        font-size: 11px;
        line-height: 1.7;
        margin-top: 9px;
    }

    .quick-row {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
        margin-top: 17px;
    }

    .quick-chip {
        padding: 8px 11px;
        border-radius: 999px;
        background: rgba(4,18,23,0.56);
        border: 1px solid rgba(255,255,255,0.07);
        color: #dce8ec;
        font-size: 9px;
        font-weight: 600;
    }

    .hero-food {
        position: absolute;
        right: 36px;
        top: 22px;
        width: 165px;
        height: 165px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 87px;
        background: radial-gradient(circle, rgba(38,235,143,0.22), rgba(3,28,27,0.07) 57%, transparent 58%);
        transform: rotate(-5deg);
    }

    .section-title {
        color: #f8fafc;
        font-size: 15px;
        font-weight: 750;
        margin: 22px 0 5px;
    }

    .section-subtitle {
        color: #657789;
        font-size: 10px;
        margin-bottom: 11px;
    }

    .stat-card {
        min-height: 108px;
        padding: 16px;
        border-radius: 18px;
        border: 1px solid rgba(255,255,255,0.07);
        background: linear-gradient(145deg, rgba(16,29,37,0.90), rgba(9,18,24,0.90));
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.025);
    }

    .stat-top {
        display: flex;
        align-items: center;
        gap: 11px;
    }

    .stat-icon {
        width: 39px;
        height: 39px;
        border-radius: 13px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
        background: rgba(34,197,94,0.11);
        border: 1px solid rgba(34,197,94,0.17);
    }

    .stat-label {
        color: #7f92a2;
        font-size: 10px;
    }

    .stat-value {
        color: #f8fafc;
        font-size: 20px;
        font-weight: 800;
        margin-top: 2px;
    }

    .stat-note {
        color: #637789;
        font-size: 9px;
        margin-top: 8px;
    }

    .panel-heading {
        color: #f8fafc;
        font-size: 15px;
        font-weight: 750;
    }

    .panel-caption {
        color: #67798a;
        font-size: 10px;
        margin-top: 4px;
    }

    .nutrition-card {
        min-height: 100%;
        border: 1px solid rgba(255,255,255,0.08);
        background: linear-gradient(145deg, rgba(11,25,32,0.94), rgba(8,15,21,0.96));
        border-radius: 21px;
        padding: 18px;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 20px;
        border-color: rgba(255,255,255,0.08);
        background: linear-gradient(145deg, rgba(12,28,34,0.86), rgba(8,17,23,0.90));
    }

    div[data-testid="stForm"] {
        border-radius: 20px;
        border: 1px solid rgba(255,255,255,0.08);
        background: rgba(7,17,22,0.86);
        padding: 19px 20px 17px;
        margin-top: 8px;
    }

    div[data-testid="stFileUploader"] {
        border-radius: 16px;
        background: rgba(7,21,27,0.66);
        border: 1px dashed rgba(92,146,160,0.40);
        padding: 9px;
    }

    div[data-testid="stFileUploader"] section {
        padding: 0;
    }

    div[data-testid="stFileUploaderDropzone"] {
        background: transparent;
        border: none;
    }

    div[data-baseweb="input"] {
        border-radius: 11px;
    }

    textarea {
        border-radius: 13px !important;
    }

    .stButton > button,
    .stFormSubmitButton > button {
        min-height: 42px;
        border-radius: 12px;
        font-weight: 650;
        border: 1px solid rgba(255,255,255,0.09);
    }

    .stButton > button:hover,
    .stFormSubmitButton > button:hover {
        border-color: rgba(74,235,147,0.32);
    }

    div[data-testid="stChatMessage"] {
        border-radius: 17px;
        border: 1px solid rgba(255,255,255,0.045);
        background: rgba(12,22,28,0.62);
        margin-bottom: 8px;
    }

    div[data-testid="stChatInput"] {
        border-radius: 17px;
    }

    .login-shell {
        max-width: 1160px;
        margin: 30px auto 0;
    }

    .login-hero {
        position: relative;
        overflow: hidden;
        min-height: 420px;
        border: 1px solid rgba(42,231,142,0.24);
        border-radius: 28px;
        padding: 46px 48px;
        background:
            radial-gradient(circle at 80% 35%, rgba(35,220,130,0.17), transparent 23%),
            radial-gradient(circle at 18% 112%, rgba(19,159,98,0.13), transparent 30%),
            linear-gradient(135deg, #071d19 0%, #071217 68%, #061015 100%);
        box-shadow: 0 24px 65px rgba(0,0,0,0.20);
    }

    .login-kicker {
        display: inline-block;
        padding: 8px 12px;
        border-radius: 999px;
        color: #7af4af;
        border: 1px solid rgba(50,231,142,0.22);
        background: rgba(30,220,126,0.08);
        font-size: 9px;
        font-weight: 700;
    }

    .login-title {
        color: #f8fafc;
        font-size: 47px;
        line-height: 1.0;
        font-weight: 800;
        letter-spacing: -1.8px;
        margin-top: 18px;
        max-width: 650px;
    }

    .login-title span {
        color: #37e98b;
    }

    .login-copy {
        color: #96aab8;
        font-size: 12px;
        line-height: 1.75;
        max-width: 620px;
        margin-top: 16px;
    }

    .login-features {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 23px;
    }

    .login-feature {
        padding: 9px 12px;
        border-radius: 12px;
        color: #dbe8ec;
        border: 1px solid rgba(255,255,255,0.07);
        background: rgba(4,17,22,0.60);
        font-size: 9px;
        font-weight: 600;
    }

    .login-food {
        position: absolute;
        right: 65px;
        top: 46px;
        width: 250px;
        height: 250px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        background: radial-gradient(circle, rgba(38,231,143,0.18), rgba(3,28,27,0.08) 58%, transparent 59%);
        font-size: 135px;
        transform: rotate(-4deg);
    }

    .form-title {
        color: #f8fafc;
        font-size: 18px;
        font-weight: 750;
        margin: 0 0 4px;
    }

    .form-caption {
        color: #6d8191;
        font-size: 10px;
        margin-bottom: 3px;
    }

    @media (max-width: 1000px) {
        .hero-food,
        .login-food {
            opacity: .25;
            right: 5px;
        }
    }

    @media (max-width: 700px) {
        .block-container {
            padding: 1rem .75rem 6rem;
        }

        .page-title {
            font-size: 24px;
        }

        .hero {
            padding: 21px;
            min-height: 225px;
        }

        .hero-food {
            display: none;
        }

        .login-hero {
            padding: 29px 22px;
            min-height: 390px;
        }

        .login-title {
            font-size: 34px;
        }

        .login-food {
            display: none;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
TWILIO_ACCOUNT_SID = st.secrets["TWILIO_ACCOUNT_SID"]
TWILIO_AUTH_TOKEN = st.secrets["TWILIO_AUTH_TOKEN"]
TWILIO_WHATSAPP_FROM = st.secrets["TWILIO_WHATSAPP_FROM"]
TWILIO_CONTENT_SID = st.secrets["TWILIO_CONTENT_SID"]


@st.cache_resource
def get_gemini_client():
    retry_options = types.HttpRetryOptions(
        attempts=6,
        initial_delay=1,
        max_delay=30,
        exp_base=2,
        jitter=1,
        http_status_codes=[408, 429, 500, 502, 503, 504],
    )

    return genai.Client(
        api_key=GEMINI_API_KEY,
        http_options=types.HttpOptions(retry_options=retry_options),
    )


@st.cache_resource
def get_twilio_client():
    return TwilioClient(
        TWILIO_ACCOUNT_SID,
        TWILIO_AUTH_TOKEN,
    )


gemini_client = get_gemini_client()
twilio_client = get_twilio_client()


if "messages" not in st.session_state:
    st.session_state.messages = []

if "active_model" not in st.session_state:
    st.session_state.active_model = PRIMARY_MODEL

if "model_fallback_used" not in st.session_state:
    st.session_state.model_fallback_used = False

if "analyzed_upload" not in st.session_state:
    st.session_state.analyzed_upload = None


def create_chat(model):
    return gemini_client.chats.create(
        model=model,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
        ),
    )


def render_message(message):
    with st.chat_message(message["role"]):
        if message["kind"] == "text":
            st.markdown(message["content"])
        elif message["kind"] == "image":
            st.image(
                message["content"],
                use_container_width=True,
            )


def add_message(role, kind, content):
    st.session_state.messages.append(
        {
            "role": role,
            "kind": kind,
            "content": content,
        }
    )


def is_temporary_error(error):
    error_text = str(error).upper()
    return any(
        code in error_text
        for code in [
            "503",
            "UNAVAILABLE",
            "429",
            "RESOURCE_EXHAUSTED",
            "500",
            "502",
            "504",
        ]
    )


def ask_gemini(parts):
    try:
        response = st.session_state.chat.send_message(parts)
        st.session_state.active_model = PRIMARY_MODEL
        st.session_state.model_fallback_used = False
        return response.text
    except Exception as primary_error:
        if not is_temporary_error(primary_error):
            return f"Sorry, something went wrong.\n\n{primary_error}"

        try:
            time.sleep(1)
            fallback_chat = create_chat(FALLBACK_MODEL)
            response = fallback_chat.send_message(parts)
            st.session_state.chat = fallback_chat
            st.session_state.active_model = FALLBACK_MODEL
            st.session_state.model_fallback_used = True
            return response.text
        except Exception:
            return (
                "MacroSnap is temporarily busy.\n\n"
                "The AI service is experiencing high traffic right now. "
                "Please try again in a few seconds."
            )


def clean_whatsapp_text(text):
    if not text:
        return "No nutrition summary available."

    text = " ".join(text.split())
    return text[:1500] + "..." if len(text) > 1500 else text


def send_whatsapp(to_number, user_name, summary):
    try:
        from_number = TWILIO_WHATSAPP_FROM.strip()
        if not from_number.startswith("whatsapp:"):
            from_number = f"whatsapp:{from_number}"

        destination = to_number.strip()
        if not destination.startswith("whatsapp:"):
            destination = f"whatsapp:{destination}"

        content_variables = json.dumps(
            {
                "1": user_name,
                "2": clean_whatsapp_text(summary),
            },
            ensure_ascii=False,
        )

        message = twilio_client.messages.create(
            from_=from_number,
            to=destination,
            content_sid=TWILIO_CONTENT_SID,
            content_variables=content_variables,
        )

        return True, message.sid
    except Exception as error:
        return False, str(error)


def reset_workspace():
    for key in [
        "onboarded",
        "name",
        "whatsapp_number",
        "chat",
        "messages",
        "active_model",
        "model_fallback_used",
        "analyzed_upload",
    ]:
        st.session_state.pop(key, None)

    st.rerun()


def build_photo_prompt():
    return (
        "Analyze this meal carefully. Identify the visible foods and estimate "
        "reasonable portion sizes. Give estimated total calories, protein, "
        "carbohydrates, fat and fiber. Present the answer with clear headings "
        "and a compact nutrition summary. State clearly that the values are estimates."
    )


if "onboarded" not in st.session_state:
    st.markdown(
        """
        <div class="login-shell">
            <div class="login-hero">
                <div class="login-kicker">✦ AI POWERED NUTRITION TRACKER</div>
                <div class="login-title">Welcome to<br><span>MacroSnap</span></div>
                <div class="login-copy">
                    Snap your meal, get instant nutrition insights, track calories and
                    macros, and send your daily summary to WhatsApp.
                </div>
                <div class="login-features">
                    <div class="login-feature">📸 Meal Analysis</div>
                    <div class="login-feature">🔥 Calories</div>
                    <div class="login-feature">💪 Macros</div>
                    <div class="login-feature">📲 WhatsApp</div>
                </div>
                <div class="login-food">🥗</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    login_left = st.container()

    with login_left:
        st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
        st.markdown(
            """
            <div>
                <div class="form-title">Create your workspace</div>
                <div class="form-caption">
                    Enter your details once and start analyzing your meals.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.form("onboarding_form"):
            name = st.text_input(
                "Your name",
                placeholder="Enter your name",
            )

            whatsapp_number = st.text_input(
                "WhatsApp number",
                placeholder="+91XXXXXXXXXX",
                help="Include your country code.",
            )

            submitted = st.form_submit_button(
                "Enter MacroSnap  →",
                use_container_width=True,
            )


    if submitted:
        if not name.strip() or not whatsapp_number.strip():
            st.warning("Please enter your name and WhatsApp number.")
        else:
            st.session_state.name = name.strip()
            st.session_state.whatsapp_number = whatsapp_number.strip()
            st.session_state.chat = create_chat(PRIMARY_MODEL)
            st.session_state.active_model = PRIMARY_MODEL
            st.session_state.model_fallback_used = False
            st.session_state.messages = []
            st.session_state.analyzed_upload = None
            st.session_state.nutrition = {
                "calories": None,
                "protein": None,
                "carbs": None,
                "fat": None,
            }
            st.session_state.onboarded = True
            st.rerun()

    st.stop()


with st.sidebar:
    st.markdown(
        """
        <div class="brand">
            <div class="brand-icon">🥗</div>
            <div>
                <div class="brand-name">Macro<span>Snap</span></div>
                <div class="brand-caption">AI Nutrition Workspace</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="sidebar-label">PROFILE</div>', unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class="profile-card">
            <div class="profile-row">
                <div class="avatar">👤</div>
                <div>
                    <div class="profile-name">{st.session_state.name}</div>
                    <div class="profile-phone">📱 {st.session_state.whatsapp_number}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="sidebar-label">WORKSPACE</div>', unsafe_allow_html=True)

    if st.button("⌂  Home", use_container_width=True):
        st.toast("Home workspace is active.")

    if st.button("📷  Meal Analysis", use_container_width=True):
        st.toast("Attach a meal photo in Meal Analyzer below.")

    if st.button("◷  History", use_container_width=True):
        st.toast("Your current AI conversation is shown below.")

    if st.button("⚙  Settings", use_container_width=True):
        st.toast("Settings are coming next.")

    st.markdown('<div class="sidebar-label">ACTIVITY</div>', unsafe_allow_html=True)

    question_count = len(
        [
            message
            for message in st.session_state.messages
            if message["role"] == "user"
        ]
    )

    st.markdown(
        f"""
        <div class="sidebar-stat">
            <div class="metric-number">{question_count}</div>
            <div class="metric-caption">Meals / questions analyzed</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")

    if st.button("＋  New Workspace", use_container_width=True):
        reset_workspace()

    st.markdown(
        """
        <div class="sidebar-footer">
            🌿 Better food.<br>
            Better choices.<br>
            A healthier you.
        </div>
        """,
        unsafe_allow_html=True,
    )


header_left, header_right = st.columns(
    [4, 1],
    vertical_alignment="center",
)

with header_left:
    st.markdown(
        f"""
        <div class="page-title">Good to see you, {st.session_state.name} 👋</div>
        <div class="page-subtitle">
            Analyze your meals, understand your macros, and keep your nutrition organized.
        </div>
        """,
        unsafe_allow_html=True,
    )

with header_right:
    st.markdown(
        """
        <div style="text-align:right;">
            <span class="online-status">
                <span class="online-dot"></span>
                AI Workspace Online
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )


st.markdown(
    """
    <div class="hero">
        <div class="hero-kicker">✦ YOUR AI NUTRITION ASSISTANT</div>
        <div class="hero-title">Let's build your healthier journey!</div>
        <div class="hero-text">
            Snap a photo of your meal, ask questions, or simply describe what you ate.
            MacroSnap will analyze it and give you calories, macros and practical insights.
        </div>
        <div class="quick-row">
            <span class="quick-chip">📷 Meal Analysis</span>
            <span class="quick-chip">🔥 Calories</span>
            <span class="quick-chip">📊 Macros</span>
            <span class="quick-chip">💬 WhatsApp</span>
        </div>
        <div class="hero-food">🥙</div>
    </div>
    """,
    unsafe_allow_html=True,
)


st.markdown('<div class="section-title">Workspace overview</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-subtitle">A quick look at your current MacroSnap workspace.</div>',
    unsafe_allow_html=True,
)

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(
        f"""
        <div class="stat-card">
            <div class="stat-top">
                <div class="stat-icon">🔥</div>
                <div>
                    <div class="stat-label">Nutrition checks</div>
                    <div class="stat-value">{question_count}</div>
                </div>
            </div>
            <div class="stat-note">Meals and nutrition questions analyzed</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c2:
    st.markdown(
        f"""
        <div class="stat-card">
            <div class="stat-top">
                <div class="stat-icon">🤖</div>
                <div>
                    <div class="stat-label">AI engine</div>
                    <div class="stat-value">Active</div>
                </div>
            </div>
            <div class="stat-note">{st.session_state.active_model}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c3:
    st.markdown(
        """
        <div class="stat-card">
            <div class="stat-top">
                <div class="stat-icon">📲</div>
                <div>
                    <div class="stat-label">WhatsApp</div>
                    <div class="stat-value">Ready</div>
                </div>
            </div>
            <div class="stat-note">Send your nutrition summary anytime</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


st.markdown('<div class="section-title">Meal analyzer</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-subtitle">Attach a meal photo or describe what you ate, then analyze it with Gemini.</div>',
    unsafe_allow_html=True,
)

analyzer_left = st.container()

with analyzer_left:
    with st.container(border=True):
        st.markdown('<div class="panel-heading">📷 Attach a meal photo</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="panel-caption">Upload JPG, JPEG, PNG or WEBP. Your photo will be sent to Gemini for meal analysis.</div>',
            unsafe_allow_html=True,
        )

        uploaded_photo = st.file_uploader(
            "Attach a meal photo",
            type=["jpg", "jpeg", "png", "webp"],
            key="meal_photo_uploader",
            label_visibility="visible",
        )

        meal_description = st.text_area(
            "Describe your meal",
            placeholder="Example: grilled chicken, rice and mixed vegetables...",
            height=90,
        )

        analyze_col, clear_col = st.columns([3, 1])

        with analyze_col:
            analyze_clicked = st.button(
                "🔎 Analyze meal",
                use_container_width=True,
            )

        with clear_col:
            clear_clicked = st.button(
                "Clear",
                use_container_width=True,
            )

        if clear_clicked:
            st.session_state.analyzed_upload = None
            st.session_state.pop("meal_photo_uploader", None)
            st.rerun()

        if uploaded_photo is not None:
            st.image(
                uploaded_photo,
                caption="Selected meal photo",
                use_container_width=True,
            )

        if analyze_clicked:
            if uploaded_photo is None and not meal_description.strip():
                st.warning("Attach a meal photo or describe your meal first.")
            else:
                parts = []

                if uploaded_photo is not None:
                    photo_bytes = uploaded_photo.getvalue()
                    file_signature = f"{uploaded_photo.name}:{len(photo_bytes)}"

                    add_message("user", "image", photo_bytes)

                    parts.append(
                        types.Part.from_bytes(
                            data=photo_bytes,
                            mime_type=uploaded_photo.type,
                        )
                    )

                    st.session_state.analyzed_upload = file_signature

                prompt = build_photo_prompt()

                if meal_description.strip():
                    add_message("user", "text", meal_description.strip())
                    prompt = (
                        f"{prompt}\n\nAdditional user description: "
                        f"{meal_description.strip()}"
                    )

                parts.append(prompt)

                with st.spinner("Analyzing your nutrition..."):
                    answer = ask_gemini(parts)

                add_message("assistant", "text", answer)

                st.rerun()


st.markdown('<div class="section-title">Your AI conversation</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-subtitle">Ask follow-up questions about any meal you analyzed.</div>',
    unsafe_allow_html=True,
)

if st.session_state.model_fallback_used:
    st.info("The primary AI model was busy, so MacroSnap switched to the backup model.")

if not st.session_state.messages:
    add_message(
        "assistant",
        "text",
        WELCOME_MESSAGE_TEMPLATE.format(name=st.session_state.name),
    )

for message in st.session_state.messages:
    render_message(message)


user_input = st.chat_input(
    "Ask MacroSnap about your meal or attach a meal photo...",
    accept_file=True,
    file_type=["jpg", "jpeg", "png", "webp"],
)


if user_input:
    photo = user_input.files[0] if user_input.files else None
    text = user_input.text
    parts = []

    if photo is not None:
        photo_bytes = photo.getvalue()

        add_message("user", "image", photo_bytes)

        parts.append(
            types.Part.from_bytes(
                data=photo_bytes,
                mime_type=photo.type,
            )
        )

    if text:
        add_message("user", "text", text)
        parts.append(text)
    elif photo is not None:
        parts.append(build_photo_prompt())

    if parts:
        with st.spinner("Analyzing your nutrition..."):
            answer = ask_gemini(parts)

        add_message("assistant", "text", answer)

    st.rerun()


if question_count > 0:
    st.markdown('<div class="section-title">Nutrition summary</div>', unsafe_allow_html=True)

    send_col, info_col = st.columns([1.25, 3.75], vertical_alignment="center")

    with send_col:
        if st.button("📲 Send to WhatsApp", use_container_width=True):
            with st.spinner("Preparing your nutrition summary..."):
                summary = ask_gemini([SUMMARY_REQUEST_PROMPT])

            success, info = send_whatsapp(
                st.session_state.whatsapp_number,
                st.session_state.name,
                summary,
            )

            if success:
                st.success("Nutrition summary sent to WhatsApp.")
            else:
                st.error(f"Couldn't send summary: {info}")

    with info_col:
        st.caption(
            "Send the current AI-generated nutrition summary directly to your WhatsApp."
        )



# import json

# import streamlit as st

# from google import genai

# from google.genai import types

# from twilio.rest import Client as TwilioClient

# from prompts import SUMMARY_REQUEST_PROMPT, SYSTEM_PROMPT, WELCOME_MESSAGE_TEMPLATE

# MODEL_NAME = "gemini-3.8-flash"

# st.set_page_config(page_title="MacroSnap", page_icon="🥗")


# GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
# TWILIO_ACCOUNT_SID = st.secrets["TWILIO_ACCOUNT_SID"]
# TWILIO_AUTH_TOKEN = st.secrets["TWILIO_AUTH_TOKEN"]
# TWILIO_WHATSAPP_FROM = st.secrets["TWILIO_WHATSAPP_FROM"]
# TWILIO_CONTENT_SID = st.secrets["TWILIO_CONTENT_SID"]
 
 
# @st.cache_resource
# def get_gemini_client():
#     return genai.Client(api_key=GEMINI_API_KEY)
 
 
# @st.cache_resource
# def get_twilio_client():
#     return TwilioClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
 
 
# gemini_client = get_gemini_client()
# twilio_client = get_twilio_client()
 
 
# def render_message(message):
#     with st.chat_message(message["role"]):
#         if message["kind"] == "text":
#             st.write(message["content"])
#         elif message["kind"] == "image":
#             st.image(message["content"])
 
 
# def add_message(role, kind, content):
#     st.session_state.messages.append({"role": role, "kind": kind, "content": content})
#     render_message(st.session_state.messages[-1])
 
 
# def ask_gemini(parts):
#     try:
#         return st.session_state.chat.send_message(parts).text
#     except Exception as error:
#         return f"Sorry, something went wrong: {error}"


# def clean_whatsapp_text(text):
#     if not text:
#         return "No nutrition summary available."
#     text = " ".join(text.split())  # collapse whitespace/newlines
#     return text[:1500] + "..." if len(text) > 1500 else text
 
 
# def send_whatsapp(to_number, user_name, summary):
#     # Content template expects {{1}} = name, {{2}} = summary.
#     try:
#         content_variables = json.dumps(
#             {"1": user_name, "2": clean_whatsapp_text(summary)}, ensure_ascii=False
#         )
#         message = twilio_client.messages.create(
#             from_=TWILIO_WHATSAPP_FROM,
#             to=f"whatsapp:{to_number}",
#             content_sid=TWILIO_CONTENT_SID,
#             content_variables=content_variables,
#         )
#         return True, message.sid
#     except Exception as error:
#         return False, str(error)
 
 
# # Step 1: onboarding
# if "onboarded" not in st.session_state:
#     st.title("🥗 MacroSnap")
#     st.caption("Snap it. Track it. Text yourself the results.")
#     with st.form("onboarding_form"):
#         name = st.text_input("Your name")
#         whatsapp_number = st.text_input(
#             "WhatsApp number (with country code)",
#             placeholder="+91XXXXXXXXXX",
#             help="This is the number MacroSnap will text your summary to.",
#         )
#         submitted = st.form_submit_button("Let's go 🚀")
#     if submitted:
#         if not name.strip() or not whatsapp_number.strip():
#             st.warning("Please fill in both your name and WhatsApp number.")
#         else:
#             st.session_state.name = name.strip()
#             st.session_state.whatsapp_number = whatsapp_number.strip()
#             st.session_state.chat = gemini_client.chats.create(
#                 model=MODEL_NAME,
#                 config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
#             )
#             st.session_state.messages = []
#             st.session_state.onboarded = True
#             st.rerun()
#     st.stop()
 
# # Step 2: chat interface
# header_col, button_col = st.columns([5, 2], vertical_alignment="center")
 
# with header_col:
#     st.title("🥗 MacroSnap")
 
# with button_col:
#     send_disabled = len(st.session_state.messages) <= 2
#     if st.button("📤 Send to WhatsApp", disabled=send_disabled, use_container_width=True):
#         with st.spinner("Summarizing your day..."):
#             summary = ask_gemini([SUMMARY_REQUEST_PROMPT])
#         success, info = send_whatsapp(st.session_state.whatsapp_number, st.session_state.name, summary)
#         if success:
#             st.success("Sent! Check your WhatsApp 📲")
#         else:
#             st.error(f"Couldn't send that: {info}")
 
# st.caption(f"Logged in as {st.session_state.name} - updates go to {st.session_state.whatsapp_number}")
 
# if not st.session_state.messages:
#     add_message("assistant", "text", WELCOME_MESSAGE_TEMPLATE.format(name=st.session_state.name))
# else:
#     for message in st.session_state.messages:
#         render_message(message)
 
# user_input = st.chat_input(
#     "Ask a question, or attach a photo of your meal",
#     accept_file=True,
#     file_type=["jpg", "jpeg", "png"],
# )
 
# if user_input:
#     photo = user_input.files[0] if user_input.files else None
#     text = user_input.text
#     parts = []
 
#     if photo is not None:
#         photo_bytes = photo.getvalue()
#         add_message("user", "image", photo_bytes)
#         parts.append(types.Part.from_bytes(data=photo_bytes, mime_type=photo.type))
#     if text:
#         add_message("user", "text", text)
#         parts.append(text)
#     elif photo is not None:
#         parts.append("What is this meal? Give me the calories and macros.")
 
#     with st.spinner("Crunching the numbers..."):
#         answer = ask_gemini(parts)
#     add_message("assistant", "text", answer)



