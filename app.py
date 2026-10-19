
import streamlit as st
import pandas as pd
from streamlit_autorefresh import st_autorefresh
from database import get_connection


# ---------------- PAGE CONFIGURATION ----------------

st.set_page_config(
    page_title="Refinery Operations",
    page_icon="🏭",
    layout="wide"
)

st_autorefresh(interval=5000, key="dashboard_refresh")


# ---------------- DATABASE HELPERS ----------------

def fetch_data(query):
    """Read data from MySQL and return it as a DataFrame."""
    db = get_connection()

    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute(query)
        rows = cursor.fetchall()
        return pd.DataFrame(rows)

    finally:
        cursor.close()
        db.close()


# ---------------- STATUS CLASSIFICATION ----------------

def get_process_status(temperature, pressure):
    """Use the same fictional warning thresholds as the simulator."""

    if temperature is None or pressure is None:
        return "NO DATA"

    temperature = float(temperature)
    pressure = float(pressure)

    if temperature > 510 or pressure > 10:
        return "CRITICAL"

    if temperature > 450 or pressure > 8:
        return "WARNING"

    return "NORMAL"


# ---------------- LOAD DATABASE DATA ----------------

try:
    processes = fetch_data("""
        SELECT
            p.id,
            p.name,
            sr.temperature,
            sr.pressure,
            sr.flow_rate,
            sr.recorded_at
        FROM processes p
        LEFT JOIN sensor_readings sr
            ON sr.id = (
                SELECT sr2.id
                FROM sensor_readings sr2
                WHERE sr2.process_id = p.id
                ORDER BY sr2.recorded_at DESC, sr2.id DESC
                LIMIT 1
            )
        ORDER BY p.id
    """)

    tanks = fetch_data("""
        SELECT
            id,
            tank_code,
            product,
            capacity_litres,
            current_level_litres,
            ROUND(
                current_level_litres / capacity_litres * 100,
                1
            ) AS fill_percentage
        FROM tanks
        ORDER BY id
    """)

    batches = fetch_data("""
        SELECT
            COUNT(*) AS completed_batches,
            COALESCE(SUM(quantity_litres), 0) AS total_litres
        FROM batches
    """)

    recent_alerts = fetch_data("""
        SELECT
            a.severity,
            a.alert_type,
            a.message,
            a.created_at,
            p.name AS process_name
        FROM alerts a
        LEFT JOIN processes p ON p.id = a.process_id
        ORDER BY a.created_at DESC
        LIMIT 10
    """)

    production = fetch_data("""
        SELECT
            product,
            SUM(quantity_litres) AS total_litres
        FROM production_records
        WHERE produced_at >= NOW() - INTERVAL 24 HOUR
        GROUP BY product
        ORDER BY total_litres DESC
    """)

except Exception as error:
    st.error(f"Could not load dashboard data: {error}")
    st.info(
        "Check that MySQL is running, database.py connects successfully, "
        "and the required tables exist."
    )
    st.stop()


# ---------------- DASHBOARD HEADER ----------------

st.title("🏭 Refinery Operations Dashboard")

st.caption(
    "Live monitoring of simulated refinery processes, storage tanks "
    "and production history."
)

st.caption("Dashboard refreshes every 5 seconds.")

st.divider()


# ---------------- PROCESS STATUS SUMMARY ----------------

st.subheader("Operations Overview")

if processes.empty:
    st.warning("No processes have been registered in the database.")
    st.stop()

processes["status"] = processes.apply(
    lambda row: get_process_status(
        row["temperature"], row["pressure"]
    ),
    axis=1
)

critical_count = (processes["status"] == "CRITICAL").sum()
warning_count = (processes["status"] == "WARNING").sum()
normal_count = (processes["status"] == "NORMAL").sum()

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Processes", len(processes))
col2.metric("Normal", int(normal_count))
col3.metric("Warnings", int(warning_count))
col4.metric("Critical", int(critical_count))


# ---------------- INDIVIDUAL PROCESS CARDS ----------------

st.subheader("Process Monitoring")

for start in range(0, len(processes), 3):
    process_columns = st.columns(3)

    for column, (_, process) in zip(
        process_columns,
        processes.iloc[start:start + 3].iterrows()
    ):
        with column:
            with st.container(border=True):
                st.markdown(f"### {process['name']}")

                status = process["status"]

                if status == "CRITICAL":
                    st.error(f"Status: {status}")
                elif status == "WARNING":
                    st.warning(f"Status: {status}")
                elif status == "NO DATA":
                    st.info("Status: NO DATA")
                else:
                    st.success(f"Status: {status}")

                if pd.isna(process["temperature"]):
                    st.write("Temperature: No reading")
                    st.write("Pressure: No reading")
                    st.write("Flow rate: No reading")
                else:
                    st.metric(
                        "Temperature",
                        f"{float(process['temperature']):.1f} °C"
                    )
                    st.metric(
                        "Pressure",
                        f"{float(process['pressure']):.1f} bar"
                    )
                    st.metric(
                        "Flow rate",
                        f"{float(process['flow_rate']):.1f}"
                    )

                    st.caption(
                        f"Last reading: {process['recorded_at']}"
                    )


# ---------------- TANK MONITORING ----------------

st.divider()
st.subheader("Storage Tank Monitoring")

if tanks.empty:
    st.info("No storage tanks found.")
else:
    tank_columns = st.columns(3)

    for index, (_, tank) in enumerate(tanks.iterrows()):
        column = tank_columns[index % 3]

        with column:
            with st.container(border=True):
                st.markdown(
                    f"### {tank['tank_code']} — {tank['product']}"
                )

                capacity = float(tank["capacity_litres"])
                level = float(tank["current_level_litres"])
                percentage = float(tank["fill_percentage"] or 0)

                st.metric(
                    "Current inventory",
                    f"{level:,.0f} L",
                    f"{percentage:.1f}% full"
                )

                st.progress(
                    min(max(percentage / 100, 0.0), 1.0)
                )

                st.caption(f"Capacity: {capacity:,.0f} L")

                if percentage >= 98:
                    st.error("Critical: tank nearly full")
                elif percentage >= 90:
                    st.warning("Warning: tank above 90%")
                else:
                    st.success("Storage available")


# ---------------- BATCH SUMMARY ----------------

st.divider()
st.subheader("Completed Production Batches")

batch_row = batches.iloc[0]

batch_col1, batch_col2 = st.columns(2)

batch_col1.metric(
    "Completed full-tank batches",
    f"{int(batch_row['completed_batches']):,}"
)

batch_col2.metric(
    "Total litres in completed batches",
    f"{float(batch_row['total_litres']):,.0f} L"
)

st.caption(
    "These totals come from the batch history. They are cumulative "
    "and are separate from the tanks' current inventory."
)


# ---------------- PRODUCTION HISTORY ----------------

st.divider()
st.subheader("Production — Last 24 Hours")

if production.empty:
    st.info("No production records in the last 24 hours.")
else:
    st.bar_chart(
        production.set_index("product")["total_litres"]
    )

    st.dataframe(
        production,
        use_container_width=True,
        hide_index=True
    )


# ---------------- RECENT ALERTS ----------------

st.divider()
st.subheader("Recent Recorded Alerts")

if recent_alerts.empty:
    st.info(
        "No alerts have been recorded in the alerts table yet. "
        "Live process statuses above are calculated from sensor readings."
    )
else:
    st.dataframe(
        recent_alerts,
        use_container_width=True,
        hide_index=True
    )
