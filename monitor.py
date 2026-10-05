import csv


# ==========================================
# PROCESSING UNIT MONITOR
# ==========================================

print("================================")
print("     PROCESSING UNIT MONITOR")
print("================================")

with open("data/processing_units.csv", "r") as file:

    reader = csv.DictReader(file)

    for unit in reader:

        name = unit["unit"]

        temperature = float(unit["temperature_c"])
        pressure = float(unit["pressure_bar"])
        flow_rate = float(unit["flow_rate_m3h"])
        status = unit["status"]

        print(f"\nChecking: {name}")

        # Check temperature
        if temperature > 450:
            print("ALERT: Temperature is too high!")

        # Check pressure
        if pressure > 10:
            print("ALERT: Pressure is too high!")

        # Check status
        if status.lower() != "running":
            print("ALERT: Unit is not running!")


# ==========================================
# STORAGE TANK MONITOR
# ==========================================

print("\n================================")
print("       STORAGE TANK MONITOR")
print("================================")

with open("data/storage_tanks.csv", "r") as file:

    reader = csv.DictReader(file)

    for tank in reader:

        tank_id = tank["tank_id"]
        product = tank["product"]

        capacity = float(tank["capacity_m3"])
        current_level = float(tank["current_level_m3"])
        status = tank["status"]

        # Calculate tank percentage
        percentage = (current_level / capacity) * 100

        print(f"\nChecking: {tank_id} - {product}")
        print(f"Tank level: {percentage:.1f}%")

        # Check capacity
        if percentage >= 90:
            print("ALERT: Tank is almost full!")

        if percentage <= 10:
            print("ALERT: Tank level is very low!")

        # Check status
        if status.lower() != "available":
            print("ALERT: Tank is not available!")