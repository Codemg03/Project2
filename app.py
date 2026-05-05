import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="Healthcare Dashboard", layout="wide")

# -----------------------------
# CUSTOM CSS
# -----------------------------
st.markdown("""
<style>

/* Sidebar gradient */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f4c81 0%, #1e90ff 60%, #ffffff 100%);
    padding-top: 20px;
}

/* Default sidebar text BLACK */
section[data-testid="stSidebar"] * {
    color: black !important;
}

/* 🔥 Make only "Filters" WHITE */
section[data-testid="stSidebar"] h2 {
    color: white !important;
}

/* Input fields */
section[data-testid="stSidebar"] .stDateInput {
    background-color: white;
    border-radius: 10px;
    padding: 6px;
}

/* Tabs styling */
.stTabs [role="tablist"] {
    background-color: #e6f2ff;
    border-radius: 10px;
    padding: 5px;
}

.stTabs [role="tab"] {
    color: #003366;
    font-weight: 600;
    border-radius: 8px;
    padding: 8px 16px;
}

.stTabs [aria-selected="true"] {
    background-color: #4da6ff;
    color: white;
}

</style>
""", unsafe_allow_html=True)

# -----------------------------
# TITLE
# -----------------------------
st.title("Child Migration Healthcare Capacity Dashboard")

# -----------------------------
# LOAD DATA
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("df.csv")

    df.columns = df.columns.str.strip()

    if "date" not in df.columns:
        df = pd.read_csv("df.csv", index_col=0).reset_index()
        df.rename(columns={"index": "date"}, inplace=True)

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.sort_values("date")

    return df

df = load_data()

# -----------------------------
# SIDEBAR FILTER
# -----------------------------
st.sidebar.markdown("## Filters")  # This will now be WHITE

start_date = st.sidebar.date_input("Start Date", df["date"].min())
end_date = st.sidebar.date_input("End Date", df["date"].max())

filtered_df = df[
    (df["date"] >= pd.to_datetime(start_date)) &
    (df["date"] <= pd.to_datetime(end_date))
]

# -----------------------------
# EARLY vs LATE COMPARISON
# -----------------------------
midpoint = len(filtered_df) // 2

early_df = filtered_df.iloc[:midpoint]
late_df = filtered_df.iloc[midpoint:]

comparison = pd.DataFrame({
    "Early Avg Load": [early_df["total_system_load"].mean()],
    "Late Avg Load": [late_df["total_system_load"].mean()]
})
# -----------------------------
# KPI SUMMARY
# -----------------------------
st.markdown("## 📊 KPI Summary")

latest = filtered_df.iloc[-1]

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Total Children Under Care", int(latest["total_system_load"]))
col2.metric("Net Intake Pressure", round(filtered_df["net_intake"].mean(), 2))
col3.metric("Volatility Index", round(filtered_df["volatility"].mean(), 2))
col4.metric("Backlog Rate", round(filtered_df["backlog_indicator"].mean(), 2))
#col5.metric("Discharge Offset Ratio", round(filtered_df["discharge_offset_ratio"].mean(), 2))
col5.metric("Discharge Offset Ratio", f"{filtered_df['discharge_offset_ratio'].replace([float('inf'), -float('inf')], pd.NA).mean(skipna=True):.2f}")

# -----------------------------
# TABS
# -----------------------------
tab1, tab2, tab3 = st.tabs([
    "System Load Overview",
    "CBP vs HHS Comparison",
    "Net Intake & Backlog"
])

# -----------------------------
# TAB 1
# -----------------------------
with tab1:
    st.subheader("System Load Overview")

    fig1 = px.line(
        filtered_df,
        x="date",
        y="total_system_load",
        title="Total System Load Trend"
    )
    st.plotly_chart(fig1, use_container_width=True)

    # Early vs Late comparison bar chart
    fig = go.Figure(data=[
        go.Bar(
            x=['Early Period', 'Late Period'],
            y=[
                comparison['Early Avg Load'].iloc[0],
                comparison['Late Avg Load'].iloc[0]
            ]
        )
    ])

    fig.update_layout(
        title='Comparison of Average Total System Load: Early vs. Late Periods',
        xaxis_title='Period',
        yaxis_title='Average Total System Load'
    )

    st.plotly_chart(fig, use_container_width=True)



# -----------------------------
# TAB 2
# -----------------------------
with tab2:
    st.subheader("CBP vs HHS Load Comparison")
    fig2 = px.area(
        filtered_df,
        x="date",
        y=["Children in CBP custody", "Children in HHS Care"],
        title="CBP vs HHS Load (Stacked)"
    )
    st.plotly_chart(fig2, use_container_width=True)

    fig3 = px.line(
        filtered_df,
        x="date",
        y=["Children in CBP custody", "Children in HHS Care"],
        title="CBP vs HHS Line Comparison"
    )
    st.plotly_chart(fig3, use_container_width=True)

# -----------------------------
# TAB 3
# -----------------------------
with tab3:
    st.subheader("Net Intake & Backlog Trends")

    fig4 = px.bar(
        filtered_df,
        x="date",
        y="net_intake",
        title="Daily Net Intake"
    )
    st.plotly_chart(fig4, use_container_width=True)

    fig5 = px.line(
        filtered_df,
        x="date",
        y="backlog_indicator",
        title="Backlog Trend (Rolling)"
    )
    st.plotly_chart(fig5, use_container_width=True)

# -----------------------------
# DATA TABLE
# -----------------------------
st.subheader("Filtered Data")
st.dataframe(filtered_df)