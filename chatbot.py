import streamlit as st
import google.generativeai as genai
import datetime
import os
from dotenv import load_dotenv


load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


st.set_page_config(page_title="AI Mental Health Companion", layout="centered")


if "conversation" not in st.session_state:
    st.session_state.conversation = []
if "last_mood" not in st.session_state:
    st.session_state.last_mood = None
if "mood_insight_shown" not in st.session_state:
    st.session_state.mood_insight_shown = False
if "user_input" not in st.session_state:
    st.session_state.user_input = ""


def ask_gemini(prompt):
    try:
        model = genai.GenerativeModel("models/gemini-2.5-flash")
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"⚠️ Gemini API Error: {e}"


def send_message():
    user_message = st.session_state.user_input.strip()
    if not user_message:
        return

    st.session_state.conversation.append({"role": "user", "content": user_message})
    with st.spinner("Thinking..."):
        ai_response = ask_gemini(user_message)
    st.session_state.conversation.append({"role": "assistant", "content": ai_response})

    
    st.session_state.user_input = ""


st.title("🧘 AI Mental Health Companion")
st.write("Select your mood and chat with your caring AI companion 💖")


st.subheader("💭 How are you feeling right now?")
moods = {
    "😀": "Happy",
    "😐": "Neutral",
    "😢": "Sad",
    "😠": "Angry",
    "😌": "Relaxed",
    "😴": "Tired"
}

cols = st.columns(len(moods))
for i, (emoji, label) in enumerate(moods.items()):
    if cols[i].button(emoji):
        st.session_state.last_mood = label
        st.session_state.mood_insight_shown = False
        with open("mood_log.csv", "a", encoding="utf-8") as f:
            f.write(f"{datetime.datetime.now()},{emoji} {label}\n")
        st.rerun()


if st.session_state.last_mood and not st.session_state.mood_insight_shown:
    st.markdown("<br>", unsafe_allow_html=True)
    mood_prompt = f"""
    You are a compassionate AI mental health companion.
    The user feels {st.session_state.last_mood}.
    Respond warmly with:
    - A short empathetic statement.
    - One caring self-care suggestion.
    - One friendly question to keep chatting.
    """
    mood_reply = ask_gemini(mood_prompt)
    st.session_state.conversation.append({
        "role": "assistant",
        "content": f"🧠 Insight for your mood ({st.session_state.last_mood}): {mood_reply}"
    })
    st.session_state.mood_insight_shown = True
    st.rerun()


st.markdown("---")
st.subheader("💬 Continue the conversation")

for msg in st.session_state.conversation:
    if msg["role"] == "user":
        st.markdown(f"🧍 **You:** {msg['content']}")
    else:
        st.markdown(f"🤖 **AI:** {msg['content']}")

st.text_input(
    "Type your message here:",
    key="user_input",
    on_change=send_message
)


st.markdown("<br>", unsafe_allow_html=True)
st.subheader("🌿 Self-Care Tools")

col1, col2 = st.columns(2)
with col1:
    if st.button("💖 Positive Affirmation"):
        affirmation = ask_gemini("Give a short positive affirmation for motivation and calmness.")
        st.success(affirmation)

with col2:
    if st.button("🧘 Guided Meditation"):
        meditation = ask_gemini("Give a 2-minute calming meditation script for stress relief.")
        st.info(meditation)


st.markdown("---")
st.subheader("🆘 Mental Health Resources")

st.info("""
If you're feeling overwhelmed or need immediate help, please reach out to a professional:

- 🇮🇳 **AASRA Helpline:** 91-9820466726  
- 🇮🇳 **NIMHANS Helpline:** 080-4611-0007  
- 🌍 **Find a local therapist:** [findahelpline.com](https://findahelpline.com) | [betterhelp.com](https://www.betterhelp.com)

Remember — reaching out for help is a sign of strength 💙
""")


