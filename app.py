
import os
import streamlit as st
import pandas as pd
import plotly.express as px
from google import genai

# ---------------- PAGE CONFIGURATION ----------------
st.set_page_config(
    page_title="AI Financial Advisor",
    page_icon="💰",
    layout="wide"
)

# ---------------- GEMINI CONFIGURATION ----------------
API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()

st.title("💰 AI-Powered Financial Advisor")
st.caption(
    "Understand your spending, plan your savings, "
    "and make informed financial decisions."
)

if not API_KEY:
    st.error("Gemini API key is missing. Restart the setup cell.")
    st.stop()

client = genai.Client(api_key=API_KEY)

# ---------------- SIDEBAR: FINANCIAL INPUTS ----------------
st.sidebar.header("📊 Your Monthly Finances")

income = st.sidebar.number_input(
    "Monthly income (₹)",
    min_value=0,
    value=30000,
    step=1000
)

rent = st.sidebar.number_input(
    "Rent / housing (₹)",
    min_value=0,
    value=7000,
    step=500
)

food = st.sidebar.number_input(
    "Food and groceries (₹)",
    min_value=0,
    value=4000,
    step=500
)

transport = st.sidebar.number_input(
    "Transport (₹)",
    min_value=0,
    value=2000,
    step=500
)

shopping = st.sidebar.number_input(
    "Shopping and entertainment (₹)",
    min_value=0,
    value=3000,
    step=500
)

other = st.sidebar.number_input(
    "Other expenses (₹)",
    min_value=0,
    value=2000,
    step=500
)

# ---------------- FINANCIAL CALCULATIONS ----------------
expenses = rent + food + transport + shopping + other
savings = income - expenses
savings_rate = (savings / income * 100) if income > 0 else 0

# ---------------- DASHBOARD ----------------
st.subheader("Your Financial Overview")

c1, c2, c3 = st.columns(3)

c1.metric("Monthly income", f"₹{income:,.0f}")
c2.metric("Monthly expenses", f"₹{expenses:,.0f}")
c3.metric("Remaining balance", f"₹{savings:,.0f}")

if savings < 0:
    st.error(
        f"Your expenses exceed your income by ₹{abs(savings):,.0f}. "
        "Review your spending and essential commitments."
    )
elif income > 0:
    st.success(f"You are saving approximately {savings_rate:.1f}% of your income.")
else:
    st.info("Enter your monthly income to calculate your savings rate.")

# ---------------- EXPENSE CHART ----------------
st.subheader("Expense Breakdown")

expense_data = pd.DataFrame({
    "Category": [
        "Rent / housing",
        "Food and groceries",
        "Transport",
        "Shopping and entertainment",
        "Other expenses"
    ],
    "Amount": [rent, food, transport, shopping, other]
})

expense_data = expense_data[expense_data["Amount"] > 0]

if not expense_data.empty:
    fig = px.pie(
        expense_data,
        names="Category",
        values="Amount",
        title="Where does your money go?",
        hole=0.4
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Add some expenses to see your chart.")

# ---------------- 50-30-20 BUDGET ----------------
st.subheader("The 50–30–20 Budget Guide")

st.write(
    "A common budgeting guideline allocates 50% of income to needs, "
    "30% to wants, and 20% to savings or debt repayment."
)

b1, b2, b3 = st.columns(3)

b1.metric("Needs guide (50%)", f"₹{income * 0.50:,.0f}")
b2.metric("Wants guide (30%)", f"₹{income * 0.30:,.0f}")
b3.metric("Savings guide (20%)", f"₹{income * 0.20:,.0f}")

st.caption(
    "This is a general guideline, not a strict rule. "
    "Adjust it to your circumstances and essential costs."
)

# ---------------- AI FINANCIAL ADVISOR ----------------
st.divider()
st.subheader("🤖 Chat with Your AI Financial Advisor")

st.write(
    "Ask questions about budgeting, saving money, reducing expenses, "
    "or building better financial habits."
)

financial_context = f"""
The user's monthly financial figures are:
Income: ₹{income}
Rent/housing: ₹{rent}
Food/groceries: ₹{food}
Transport: ₹{transport}
Shopping/entertainment: ₹{shopping}
Other expenses: ₹{other}
Total expenses: ₹{expenses}
Remaining balance: ₹{savings}
Savings rate: {savings_rate:.1f}%

Give practical, understandable educational guidance based on these figures.
Explain calculations when useful. Do not invent financial facts.
Do not guarantee investment returns or present yourself as a licensed
financial adviser. Explain risks and uncertainty where relevant.
"""

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

question = st.chat_input(
    "Example: How can I improve my monthly savings?"
)

if question:
    st.session_state.messages.append(
        {"role": "user", "content": question}
    )

    with st.chat_message("user"):
        st.markdown(question)

    history = ""
    for message in st.session_state.messages[-10:]:
        history += f'{message["role"].upper()}: {message["content"]}\n'

    prompt = f"""
You are a helpful AI Financial Advisor chatbot for a student project.

Rules:
- Use clear, beginner-friendly language.
- Use Indian rupees (₹) when discussing the user's finances.
- Provide practical budgeting and savings education.
- Never ask for passwords, bank login details, or OTPs.
- Do not guarantee investment profits.
- Explain that investment choices involve risk.
- Do not claim that you have accessed the user's actual bank account.

{financial_context}

Conversation:
{history}

Write a helpful response to the user's latest question.
"""

    with st.chat_message("assistant"):
        with st.spinner("Your AI advisor is thinking..."):
            try:
                response = client.models.generate_content(
                    model="gemini-flash-latest",
                    contents=prompt
                )

                answer = response.text

                if not answer:
                    answer = "I couldn't generate a response. Please try again."

                st.markdown(answer)

                st.session_state.messages.append(
                    {"role": "assistant", "content": answer}
                )

            except Exception as e:
                st.error(
                    "The AI request failed. Check that your Gemini API "
                    "key is valid, the selected model is available, and "
                    "your API quota has not been exceeded."
                )
                st.caption(f"Technical details: {str(e)[:500]}")

# ---------------- FOOTER ----------------
st.divider()
st.caption(
    "Educational project only. This app uses the financial figures "
    "you enter and does not connect to a bank account."
)
