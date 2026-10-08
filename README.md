# Refinery Operations Monitoring System

A Python and MySQL-based simulation system for monitoring refinery process conditions, detecting abnormal sensor readings, and maintaining historical operational data.

> **Educational simulation:** Process values and alert thresholds are fictional and are not real refinery safety limits.

## What I Built

The system simulates five refinery processes:

- Distillation A
- Cracking B
- Hydrotreating C
- Reforming D
- Blending E

Each process continuously generates simulated **temperature, pressure, and flow-rate readings**.

The monitoring engine:

- Detects **WARNING** and **CRITICAL** conditions
- Supports multiple simultaneous alerts
- Stores sensor readings and alerts in MySQL
- Retrieves the **latest stored reading** when restarted, allowing the simulation to continue from its previous state

## Architecture

```text
MySQL
  ↓
Process Configuration
  ↓
Python Simulator
  ↓
Monitoring Engine
  ├── Sensor Readings → MySQL
  └── Alerts → MySQL
```

The database is the persistent source of truth rather than relying on hard-coded process data.

## Tech Stack

**Python · MySQL · SQL · mysql-connector-python · python-dotenv · Git/GitHub**

## Database

```text
refinery_monitor
├── processes
├── sensor_readings
└── alerts
```

The relational design separates process configuration, time-based sensor data, and operational alerts, providing a foundation for historical analysis and future scaling.

## Roadmap

- Real-time admin dashboard
- Storage tank monitoring
- Production tracking
- Historical sensor visualizations
- Alert history and analytics
- Predictive maintenance with ML
- API and cloud deployment

## Run Locally

```bash
pip install mysql-connector-python python-dotenv
python database.py
python simulator.py
```

Database credentials are stored in `.env` and excluded from Git using `.gitignore`.
