import streamlit as st
import google.generativeai as genai
import pandas as pd
import os

st.set_page_config(page_title="HR AI Agent Dashboard", layout="centered")
st.title("📊 HR AI Agent Dashboard")

# Google Cloud Run ke environment variables se keys uthana
gemini_key = os.environ.get("GEMINI_API_KEY")
sheet_url = os.environ.get("GOOGLE_SHEET_URL")

if not gemini_key or not sheet_url:
    st.warning("⚠️ Setup Incomplete: Cloud par Environment Variables configure nahi kiye gaye.")
    st.stop()

genai.configure(api_key=gemini_key)

@st.cache_data(ttl=30)
def load_data(url):
    # Public sharing link ko direct CSV download mein convert karna
    csv_url = url.replace('/edit?usp=sharing', '/export?format=csv').replace('/edit#gid=', '/export?format=csv&gid=')
    return pd.read_csv(csv_url)

try:
    df = load_data(sheet_url)
    st.success("✅ Real-time Google Sheet Connected!")
    with st.expander("👀 View Current Sheet Preview"):
        st.dataframe(df.head(5))
except Exception as e:
    st.error(f"❌ Sheet connect nahi ho saki: {e}")
    st.stop()

user_prompt = st.text_input("💬 Ask AI anything (e.g., 'L1 kitne qualify huwe?'):")

if user_prompt:
    with st.spinner("AI Data analyze kar raha hai..."):
        data_summary = df.to_string()
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        full_prompt = f"""
        You are an HR Data Analyst AI. Here is the recruitment data:
        {data_summary}
        
        Answer the manager's query accurately in simple Roman Urdu or English based on the language they ask.
        Query: {user_prompt}
        """
        response = model.generate_content(full_prompt)
        st.write("### 🤖 AI Response:")
        st.info(response.text)
