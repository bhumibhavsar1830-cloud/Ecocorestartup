import streamlit as st
import pandas as pd
from sklearn.linear_model import LinearRegression
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

st.set_page_config(page_title="EcoCore AI", layout="wide")

# ---------------- LOGIN ----------------
users = pd.DataFrame({
    "username": ["admin", "neha"],
    "password": ["1234", "pass123"]
})

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
🌱 EcoCore AI — Smart Factory Dashboard
</h1>
""", unsafe_allow_html=True)

st.markdown("---")

# ---------------- FILE UPLOAD ----------------
st.sidebar.header("📂 Upload Data")
file = st.sidebar.file_uploader("Upload CSV/Excel", type=["csv","xlsx"])

# ---------------- QUICK ANALYSIS ----------------
st.subheader("⚡ Quick Analysis")

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
        suggestion = "Maintain performance"

    # PDF REPORT
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

# ---------------- DASHBOARD ----------------
if file:
    try:
        df = pd.read_csv(file)
    except:
        df = pd.read_excel(file)

    st.markdown("## 🏭 Factory Dashboard")

    factory = st.selectbox("Select Factory", df['factory_name'].unique())
    data = df[df['factory_name'] == factory]

    # Basic Graph
    st.line_chart(data[['energy','units']])

    # Convert date
    data['date'] = pd.to_datetime(data['date'])

    # 📊 Trend Graph
    st.markdown("## 📊 Energy Trend")
    st.line_chart(data.set_index('date')['energy'])

    # 🧠 AI Insights
    st.markdown("## 🧠 AI Insights")

    avg_energy = data['energy'].mean()
    high_spikes = data[data['energy'] > avg_energy * 1.2]

    if not high_spikes.empty:
        st.error(f"⚠️ {len(high_spikes)} energy spikes detected!")
        st.write("👉 Machines may be inefficient during these periods")
    else:
        st.success("✅ No major energy issues")

    # 🚨 Anomaly Detection
    st.markdown("## 🚨 Anomaly Detection")

    threshold = data['energy'].mean() + 2 * data['energy'].std()
    anomalies = data[data['energy'] > threshold]

    if not anomalies.empty:
        st.warning("⚠️ Critical anomalies detected!")
        st.dataframe(anomalies)
    else:
        st.success("✅ System running normally")

    # 💰 Savings
    st.markdown("## 💰 Savings Analysis")

    waste_energy = data[data['energy'] > avg_energy]['energy'].sum()
    estimated_savings = waste_energy * 0.1

    st.metric("Estimated Savings", f"₹{int(estimated_savings)}")

    # 🤖 ML Prediction
    st.markdown("## 🔮 Energy Prediction")

    model = LinearRegression()
    model.fit(data[['hours']], data['energy'])

    future = st.number_input("Enter Future Hours")

    if st.button("Predict Energy"):
        pred = model.predict([[future]])
        st.success(f"Predicted Energy: {pred[0]:.2f} kWh")

    # 🏭 Factory Comparison
    st.markdown("## 🏭 Factory Comparison")

    comparison = df.groupby('factory_name')['energy'].mean()
    st.bar_chart(comparison)

    # Summary
    st.markdown("## 📊 Summary")
    st.write(f"Avg Energy: {data['energy'].mean():.2f}")
    st.write(f"Avg Units: {data['units'].mean():.2f}")
