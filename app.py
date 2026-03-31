import streamlit as st
import pandas as pd
from sklearn.linear_model import LinearRegression
from io import BytesIO

# PDF
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

st.set_page_config(page_title="EcoCore AI", layout="wide", page_icon="🌱")

# ---------------- LOGIN ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

users = {"admin": "1234", "neha": "pass123"}

st.sidebar.title("🔐 Login")

if not st.session_state.logged_in:
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")

    if st.sidebar.button("Login"):
        if username in users and users[username] == password:
            st.session_state.logged_in = True
            st.success("Login successful")
            st.rerun()
        else:
            st.error("Invalid credentials")

    st.stop()

if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()

# ---------------- HEADER ----------------
st.markdown("<h1 style='text-align:center;color:green;'>🌱 EcoCore AI Dashboard</h1>", unsafe_allow_html=True)
st.markdown("### 💡 Reduce energy cost by up to 20% using AI insights")
st.markdown("---")

# ---------------- FILE UPLOAD ----------------
file = st.sidebar.file_uploader("Upload Factory Data", type=["csv", "xlsx"])

if file:
    try:
        df = pd.read_csv(file)
    except:
        df = pd.read_excel(file)

    factory = st.selectbox("Select Factory", df['factory_name'].unique())
    data = df[df['factory_name'] == factory].copy()

    data['date'] = pd.to_datetime(data['date'])

    # ---------------- METRICS ----------------
    st.markdown("## 📊 Overview")

    total_energy = data['energy'].sum()
    avg_energy = data['energy'].mean()
    cost = total_energy * 10
    carbon = total_energy * 0.82 / 1000
    savings = cost * 0.15

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Energy", f"{int(total_energy)} kWh")
    c2.metric("Estimated Cost", f"₹{int(cost)}")
    c3.metric("Carbon Emission", f"{carbon:.2f} tons")
    c4.metric("Potential Saving", f"₹{int(savings)}")

    # ---------------- GRAPH ----------------
    st.markdown("## 📈 Energy Trend")
    st.line_chart(data.set_index('date')['energy'])

    # ---------------- AI INSIGHTS ----------------
    st.markdown("## 🧠 AI Insights")

    spikes = data[data['energy'] > avg_energy * 1.2]

    if not spikes.empty:
        st.error(f"⚠ {len(spikes)} energy spikes detected")
        st.write("💡 Suggestion: Shift load to off-peak hours")
    else:
        st.success("Energy usage is stable")

    # ---------------- CARBON SCORE ----------------
    st.markdown("## 🌱 Carbon Score")

    score = max(0, 100 - (avg_energy / data['energy'].max() * 100))
    st.metric("Carbon Score", f"{int(score)}/100")

    # ---------------- PREDICTION ----------------
    st.markdown("## 🔮 Energy Prediction")

    data['day'] = range(len(data))
    model = LinearRegression()
    model.fit(data[['day']], data['energy'])

    future_days = pd.DataFrame({'day': range(len(data), len(data)+7)})
    predictions = model.predict(future_days)

    pred_df = pd.DataFrame({
        "day": future_days['day'],
        "Predicted Energy": predictions
    })

    st.line_chart(data.set_index('day')['energy'])
    st.line_chart(pred_df.set_index('day'))

    # ---------------- RECOMMENDATIONS ----------------
    st.markdown("## 💡 Recommendations")
    st.write("- Reduce peak hour usage")
    st.write("- Optimize machine timing")
    st.write("- Avoid idle machines")

    # ---------------- PDF REPORT ----------------
    st.markdown("## 📄 Download Report")

    def create_pdf():
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer)
        styles = getSampleStyleSheet()

        elements = []

        elements.append(Paragraph("<b>EcoCore AI – Energy Optimization Report</b>", styles['Title']))
        elements.append(Spacer(1, 20))

        table_data = [
            ["Metric", "Value"],
            ["Total Energy", f"{int(total_energy)} kWh"],
            ["Cost", f"₹{int(cost)}"],
            ["Carbon", f"{carbon:.2f} tons"],
            ["Savings", f"₹{int(savings)}"]
        ]

        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.green),
            ('TEXTCOLOR',(0,0),(-1,0),colors.white),
            ('GRID',(0,0),(-1,-1),1,colors.black)
        ]))

        elements.append(table)
        elements.append(Spacer(1, 20))

        elements.append(Paragraph("<b>Insights</b>", styles['Heading2']))
        elements.append(Paragraph("Energy spikes detected during peak hours.", styles['Normal']))

        elements.append(Spacer(1, 10))

        elements.append(Paragraph("<b>Recommendations</b>", styles['Heading2']))
        elements.append(Paragraph("- Reduce peak usage", styles['Normal']))
        elements.append(Paragraph("- Optimize operations", styles['Normal']))

        elements.append(Spacer(1, 30))
        elements.append(Paragraph("Generated by EcoCore AI", styles['Italic']))

        doc.build(elements)
        buffer.seek(0)

        return buffer

    pdf = create_pdf()

    st.download_button("Download PDF", pdf, "EcoCore_Report.pdf")

else:
    st.info("Upload factory data to start analysis")
