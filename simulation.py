import random
import time
from database import get_connection


while True:

    db = get_connection()
    cursor = db.cursor(dictionary=True)

    # Get all processes from MySQL
    cursor.execute("SELECT * FROM processes")
    processes = cursor.fetchall()

    for process in processes:

        # Get the latest sensor reading for this process
        cursor.execute(
            """
            SELECT temperature, pressure, flow_rate
            FROM sensor_readings
            WHERE process_id = %s
            ORDER BY recorded_at DESC, id DESC
            LIMIT 1
            """,
            (process["id"],)
        )

        reading = cursor.fetchone()

        temperature = float(reading["temperature"])
        pressure = float(reading["pressure"])
        flow_rate = float(reading["flow_rate"])

        alerts = []

        # Simulate sensor changes
        temperature += random.randint(-3, 3)

        if random.random() < 0.2:
            pressure += random.uniform(0.5, 1.0)
        else:
            pressure += random.uniform(-0.5, 0.5)

        flow_rate += random.randint(-2, 2)

        # Temperature monitoring
        if temperature > process["temperature_limit"]:
            alerts.append(
                ("CRITICAL", "TEMPERATURE", "Temperature too high")
            )

        elif temperature > 450:
            alerts.append(
                ("WARNING", "TEMPERATURE", "Temperature getting high")
            )

        # Pressure monitoring
        if pressure > process["pressure_limit"]:
            alerts.append(
                ("CRITICAL", "PRESSURE", "Pressure too high")
            )

        elif pressure > 8:
            alerts.append(
                ("WARNING", "PRESSURE", "Pressure getting high")
            )

        # Overall status
        if any(alert[0] == "CRITICAL" for alert in alerts):
            status = "CRITICAL"

        elif alerts:
            status = "WARNING"

        else:
            status = "NORMAL"

        # Save new sensor reading
        cursor.execute(
            """
            INSERT INTO sensor_readings
            (process_id, temperature, pressure, flow_rate)
            VALUES (%s, %s, %s, %s)
            """,
            (
                process["id"],
                temperature,
                pressure,
                flow_rate
            )
        )

        # Save alerts
        for severity, alert_type, message in alerts:

            cursor.execute(
                """
                INSERT INTO alerts
                (process_id, severity, alert_type, message)
                VALUES (%s, %s, %s, %s)
                """,
                (
                    process["id"],
                    severity,
                    alert_type,
                    message
                )
            )

        print(process["name"])
        print("Temperature:", round(temperature, 1))
        print("Pressure:", round(pressure, 1))
        print("Flow:", round(flow_rate, 1))
        print("Status:", status)
        print("Alerts:", alerts)
        print("--------------------------------")

    db.commit()

    cursor.close()
    db.close()

    time.sleep(3)