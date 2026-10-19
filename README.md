# Refinery Operations Monitoring System

A Python and MySQL-based refinery simulation that monitors processing units, tracks storage tank inventory, records production activity, and captures completed full-tank batches through an interactive Streamlit dashboard.

## Overview

The Refinery Operations Monitoring System simulates the core monitoring and inventory-tracking activities of a refinery. It combines a database-backed simulation engine with an operations dashboard to demonstrate how process data, alerts, storage levels, and production history can be managed in a single application.

The project was built as a portfolio project combining software engineering, database management, and data analytics.

**Important:** This is an educational simulation. Process readings, production schedules, and thresholds are fictional and must not be used for real industrial operations or safety decisions.

## Key Features

### Process Monitoring

- Simulates temperature, pressure, and flow-rate readings for five processing units.
- Classifies process conditions as `NORMAL`, `WARNING`, or `CRITICAL` using configured thresholds.
- Stores sensor readings in MySQL for historical reference.
- Retrieves the latest available reading for each process.

### Production and Storage Management

- Simulates production at configurable intervals for five refinery processes.
- Tracks current tank inventory and storage capacity.
- Prevents production quantities from exceeding available tank capacity.
- Records individual production events in MySQL.
- Automatically records a completed batch when a tank reaches full capacity.
- Resets the tank to zero after successfully recording a full-tank batch, allowing another fill cycle.
- Tracks cumulative completed batches and total litres collected.

### Operations Dashboard

- Displays process monitoring cards with the latest sensor readings and status.
- Shows storage tank levels, fill percentages, and capacity warnings.
- Summarises process statuses and completed production batches.
- Visualises production totals for the previous 24 hours.
- Displays recent alerts already recorded in the database.
- Refreshes automatically at five-second intervals.

## Technology Stack

| Technology     | Purpose                                                             |
| -------------- | ------------------------------------------------------------------- |
| Python         | Simulation and application logic                                    |
| MySQL          | Persistent storage for readings, inventory, production, and batches |
| Streamlit      | Interactive monitoring dashboard                                    |
| Pandas         | Data processing and tabular presentation                            |
| SQL            | Database queries, joins, aggregation, and reporting                 |
| Git and GitHub | Version control and project documentation                           |

## System Architecture

```text
              REFINERY SIMULATION
                      |
             +--------+--------+
             |                 |
       Sensor Readings     Production
             |                 |
      Monitoring Logic    Storage Tanks
             |                 |
          Alerts          Full Tank?
                               |
                         Record Batch
                               |
                         Reset Tank
             |                 |
             +--------+--------+
                      |
                  MySQL DB
                      |
              Streamlit Dashboard
                      |
       +--------------+--------------+
       |              |              |
   Operations       Inventory     Analytics
   Monitoring      Monitoring    & History
```

The simulation engines write operational data to MySQL. The Streamlit dashboard reads from the database, separating data generation and storage from data presentation.

## Processing Units and Production Schedule

The following schedules are fictional demonstration settings.

| Processing unit | Product  | Production quantity |    Interval |
| --------------- | -------- | ------------------: | ----------: |
| Distillation A  | Petrol   |             2,000 L | 240 seconds |
| Cracking B      | LPG      |               500 L |  20 seconds |
| Hydrotreating C | Diesel   |               100 L |   2 seconds |
| Reforming D     | Jet Fuel |               800 L |  60 seconds |
| Blending E      | Kerosene |               600 L |  40 seconds |

The production interval controls how frequently a production event is attempted. Actual quantities may be smaller when the remaining tank capacity is insufficient for the scheduled quantity.

## Database Design

The application uses a MySQL database named `refinery_monitor`.

| Table                | Responsibility                                           |
| -------------------- | -------------------------------------------------------- |
| `processes`          | Processing-unit metadata and configured limits           |
| `sensor_readings`    | Historical temperature, pressure, and flow-rate readings |
| `alerts`             | Recorded process alerts and their resolution information |
| `tanks`              | Tank capacity and current inventory                      |
| `production_records` | Individual production events                             |
| `batches`            | Completed full-tank batches                              |

### Full-Tank Batch Logic

A completed batch is recorded only when the tank reaches its full capacity.

For example, when a 10,000-litre tank fills:

1. The production event is recorded.
2. A batch record is inserted with the tank, product, collected quantity, capacity, and completion timestamp.
3. The tank's current inventory is reset to zero.
4. The next production cycle can begin filling the tank again.

The batch insert and tank reset are committed within the same database transaction. If a database operation fails, the transaction is rolled back.

The batch history provides a cumulative record of completed tank loads, while the `tanks` table represents current inventory. These values measure different things.

## Project Structure

```text
refinery-monitoring-system/
├── app.py
├── database.py
├── simulator.py
├── production_engine.py
├── README.md
├── requirements.txt
├── .gitignore
└── .env
```

- `app.py` — Streamlit dashboard and database reporting queries.
- `database.py` — Shared MySQL connection configuration.
- `simulator.py` — Process sensor simulation and monitoring logic.
- `production_engine.py` — Production scheduling, tank updates, and batch recording.
- `requirements.txt` — Python dependencies.
- `.env` — Local database credentials; excluded from version control.
- `.gitignore` — Prevents sensitive configuration and unnecessary local files from being committed.

## Getting Started

### Prerequisites

- Python 3.12 or another compatible Python version.
- MySQL Server.
- MySQL Workbench or another MySQL client.
- Git.
- A terminal and code editor such as VS Code.

### 1. Clone the Repository

```bash
git clone <your-github-repository-url>
cd <your-project-folder>
```

Replace the placeholders with your actual GitHub repository URL and folder name.

### 2. Create and Activate a Virtual Environment

Windows:

```bash
py -3.12 -m venv .venv
.venv\Scripts\activate
```

If Python 3.12 is unavailable, use an installed compatible version.

### 3. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

If you have not yet created or updated `requirements.txt`, install the required packages:

```bash
pip install mysql-connector-python python-dotenv streamlit pandas streamlit-autorefresh
```

### 4. Configure MySQL

Create the `refinery_monitor` database and configure the required tables using the SQL schema for this project.

Set up your `.env` file with the database connection settings expected by `database.py`. Keep your actual database password and other secrets private.

**Never commit `.env` or hardcode database credentials in source files.**

### 5. Start the Simulation

Open a terminal in the project directory and run:

```bash
python simulator.py
```

This starts the sensor simulation and process monitoring loop, provided the database is configured and the required tables exist.

### 6. Start the Production Engine

Open a second terminal, activate the same virtual environment, and run:

```bash
python production_engine.py
```

The production engine records production activity, updates tank inventory, and records completed full-tank batches.

### 7. Launch the Dashboard

Open a third terminal and run:

```bash
streamlit run app.py
```

Open the local URL displayed in the terminal, usually:

```text
http://localhost:8501
```

Keep the relevant simulation processes running to observe new data as it is generated.

## Example Analytics

The database supports questions such as:

- How many full-tank batches have been completed for each product?
- How many litres have been collected in completed batches?
- Which storage tanks are approaching capacity?
- What are the latest readings and status of each process?
- How much of each product was recorded in the last 24 hours?

Example SQL query for completed batch totals:

```sql
SELECT
    product,
    COUNT(*) AS completed_batches,
    SUM(quantity_litres) AS total_litres
FROM batches
GROUP BY product
ORDER BY total_litres DESC;
```

Example query for current tank utilisation:

```sql
SELECT
    tank_code,
    product,
    current_level_litres,
    capacity_litres,
    ROUND(
        current_level_litres / capacity_litres * 100,
        1
    ) AS fill_percentage
FROM tanks
ORDER BY fill_percentage DESC;
```

## Current Limitations

- Sensor readings and production schedules are simulated, not collected from physical equipment.
- Temperature and pressure thresholds are fictional demonstration values.
- Completed batches are recorded only for full tanks; partially filled tanks remain in inventory.
- Dispatching, sales, and outbound inventory movements are not yet implemented.
- Dashboard alerts display previously recorded alert records; live status classification is calculated separately from the latest readings.
- The dashboard uses periodic refresh rather than WebSockets or a dedicated real-time streaming service.
- Authentication, role-based access, deployment, automated tests, and production-grade monitoring are potential future improvements.

## Future Improvements

- Centralise monitoring thresholds in shared configuration.
- Add historical sensor trend charts and time-range filters.
- Improve alert lifecycle management and persist tank-specific alerts.
- Add dispatch simulation and inventory reconciliation.
- Introduce process-to-product configuration in the database.
- Add automated tests for capacity limits, batch completion, and transaction rollback.
- Add authentication and role-based dashboard access.
- Deploy the dashboard and database using a suitable hosting architecture.

## Learning Outcomes

This project provides practical experience with:

- Python application design and simulation logic.
- Relational database design and foreign-key relationships.
- SQL queries, joins, aggregations, and historical reporting.
- Persistent application state and database transactions.
- Data presentation and dashboard development.
- Git-based version control and technical documentation.

## Disclaimer

This project is intended for educational and portfolio demonstration purposes only. It is not an industrial control system, and its simulated values, schedules, thresholds, and behaviours do not represent validated refinery operating procedures or safety limits.
