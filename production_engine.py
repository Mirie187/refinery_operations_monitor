
import time
from database import get_connection


# Fictional simulation schedule:
# process name: (product, production quantity in litres, interval in seconds)
PRODUCTION_SCHEDULE = {
    "Distillation A": ("Petrol", 2000, 240),
    "Cracking B": ("LPG", 500, 20),
    "Hydrotreating C": ("Diesel", 100, 2),
    "Reforming D": ("Jet Fuel", 800, 60),
    "Blending E": ("Kerosene", 600, 40),
}

TANK_WARNING_PERCENT = 90
TANK_CRITICAL_PERCENT = 98


def record_completed_batch(cursor, tank_id, tank_code, product, capacity):
    """Record a full tank as a completed batch, then empty it."""

    cursor.execute(
        """
        INSERT INTO batches
            (tank_id, product, quantity_litres, capacity_litres)
        VALUES (%s, %s, %s, %s)
        """,
        (tank_id, product, capacity, capacity)
    )

    cursor.execute(
        """
        UPDATE tanks
        SET current_level_litres = 0
        WHERE id = %s
        """,
        (tank_id,)
    )

    print(
        f"BATCH COMPLETED: {tank_code} | {product} | "
        f"{capacity:.1f} L collected. Tank emptied and ready."
    )


def produce_batch(cursor, process, product, quantity):
    """Produce product and record a batch whenever its tank fills."""

    cursor.execute(
        """
        SELECT id, tank_code, capacity_litres, current_level_litres
        FROM tanks
        WHERE product = %s
        """,
        (product,)
    )

    tank = cursor.fetchone()

    if tank is None:
        print(f"No storage tank found for {product}.")
        return

    tank_id, tank_code, capacity, current_level = tank

    capacity = float(capacity)
    current_level = float(current_level)

    # Recover a full tank left over from a previous run.
    if current_level >= capacity:
        record_completed_batch(
            cursor, tank_id, tank_code, product, capacity
        )
        current_level = 0

    # Never produce more than the available tank space.
    available_space = capacity - current_level

    if available_space <= 0:
        print(f"No available space in {tank_code}.")
        return

    actual_quantity = min(float(quantity), available_space)
    new_level = current_level + actual_quantity

    # Record the individual production event.
    cursor.execute(
        """
        INSERT INTO production_records
            (process_id, tank_id, product, quantity_litres)
        VALUES (%s, %s, %s, %s)
        """,
        (process["id"], tank_id, product, actual_quantity)
    )

    # Update the tank's current level.
    cursor.execute(
        """
        UPDATE tanks
        SET current_level_litres = %s
        WHERE id = %s
        """,
        (new_level, tank_id)
    )

    fill_percent = new_level / capacity * 100

    print(
        f"{process['name']} produced {actual_quantity:.1f} L "
        f"of {product}. {tank_code}: {fill_percent:.1f}% full."
    )

    # A full tank becomes a completed batch and resets to zero.
    if new_level >= capacity:
        record_completed_batch(
            cursor, tank_id, tank_code, product, capacity
        )

    elif fill_percent >= TANK_CRITICAL_PERCENT:
        print(f"CRITICAL: {tank_code} is nearly full!")

    elif fill_percent >= TANK_WARNING_PERCENT:
        print(f"WARNING: {tank_code} is above 90% capacity.")


def main():
    last_production = {}
    start_time = time.monotonic()

    for process_name in PRODUCTION_SCHEDULE:
        last_production[process_name] = start_time

    print("Production engine running. Press Ctrl+C to stop.")

    try:
        while True:
            now = time.monotonic()
            db = get_connection()
            cursor = None

            try:
                cursor = db.cursor()

                cursor.execute("SELECT id, name FROM processes")
                processes = cursor.fetchall()

                for process_id, process_name in processes:
                    if process_name not in PRODUCTION_SCHEDULE:
                        continue

                    product, quantity, interval = (
                        PRODUCTION_SCHEDULE[process_name]
                    )

                    elapsed = now - last_production[process_name]

                    if elapsed >= interval:
                        process = {
                            "id": process_id,
                            "name": process_name
                        }

                        produce_batch(
                            cursor, process, product, quantity
                        )

                        last_production[process_name] = now

                # Save production, tank updates and batch records together.
                db.commit()

            except Exception as error:
                db.rollback()
                print(f"Database error: {error}")
                raise

            finally:
                if cursor is not None:
                    cursor.close()
                db.close()

            time.sleep(1)

    except KeyboardInterrupt:
        print("\nProduction engine stopped.")


if __name__ == "__main__":
    main()

