import streamlit as st
import pandas as pd
from sklearn.linear_model import LinearRegression
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

st.set_page_config(page_title="EcoCore AI", layout="wide")

# ---------------- LOGIN ----------------
users = pd.read_csv("users.csv")

def login(username, password):
    user = users[(users['username']==username) & (users['password']==password)]
    return not user.empty

st.sidebar.title("🔐 Login")
username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")

if st.sidebar.button("Login"):
    if login(username, password):
        st.session_state["logged_in"] = True
    else:
        st.sidebar.error("Invalid credentials")

if "logged_in" not in st.session_state:
    st.stop()

# ---------------- HEADER ----------------
st.markdown("""
<h1 style='text-align:center;color:green;'>
🌱 EcoCore AI — Factory Optimization Dashboard
</h1>
""", unsafe_allow_html=True)

st.markdown("---")

# ---------------- INPUT ----------------
st.sidebar.header("📂 Upload Data")
file = st.sidebar.file_uploader("Upload CSV/Excel", type=["csv","xlsx"])

# ---------------- MANUAL INPUT ----------------
st.subheader("✏️ Quick Analysis")

col1, col2, col3 = st.columns(3)

units = col1.number_input("Units Produced", min_value=0)
energy = col2.number_input("Energy (kWh)", min_value=0)
hours = col3.number_input("Machine Hours", min_value=0)

if st.button("🚀 Analyze Now"):
    efficiency = units / energy if energy > 0 else 0
    savings = (1 - efficiency) * 50000
    co2 = energy * 0.82 / 1000

    c1, c2, c3 = st.columns(3)
    c1.metric("Efficiency", f"{efficiency:.2f}")
    c2.metric("Estimated Savings", f"₹{int(savings)}")
    c3.metric("CO2 Reduction", f"{co2:.2f} tons")

    if efficiency < 0.5:
        st.error("⚠️ High Energy Waste Detected")
        suggestion = "Reduce idle time & optimize machines"
    else:
        st.success("✅ Good Efficiency")
        suggestion = "Maintain current performance"

    # PDF
    def create_pdf():
        c = canvas.Canvas("report.pdf", pagesize=letter)
        c.drawString(100, 750, "EcoCore AI Report")
        c.drawString(100, 700, f"Efficiency: {efficiency:.2f}")
        c.drawString(100, 680, f"CO2: {co2:.2f} tons")
        c.drawString(100, 660, f"Savings: ₹{int(savings)}")
        c.drawString(100, 640, f"Suggestion: {suggestion}")
        c.save()

    if st.button("📄 Download PDF"):
        create_pdf()
        with open("report.pdf", "rb") as f:
            st.download_button("Download Report", f, "EcoCore_Report.pdf")

# ---------------- DATA DASHBOARD ----------------
if file:
    try:
        df = pd.read_csv(file)
    except:
        df = pd.read_excel(file)

    st.markdown("## 🏭 Factory Dashboard")

    factory = st.selectbox("Select Factory", df['factory_name'].unique())
    data = df[df['factory_name'] == factory]

    st.line_chart(data[['energy','units']])

    # ML Model
    model = LinearRegression()
    model.fit(data[['hours']], data['energy'])

    future = st.number_input("Enter Future Hours")

    if st.button("🔮 Predict Energy"):
        pred = model.predict([[future]])
        st.success(f"Predicted Energy: {pred[0]:.2f} kWh")

    # Summary
    avg_energy = data['energy'].mean()
    avg_units = data['units'].mean()

    st.write(f"📊 Avg Energy: {avg_energy:.2f}")
    st.write(f"📊 Avg Units: {avg_units:.2f}")
