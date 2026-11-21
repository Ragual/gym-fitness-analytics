@'
# Gym & Fitness Analytics Platform

An end-to-end gym intelligence platform built with PostgreSQL, Python, machine learning, FastAPI, and Streamlit. It transforms gym membership, attendance, payment, and workout data into actionable business insights.

## Overview

The platform helps gym operators understand member activity, identify members who may be at risk of becoming inactive, analyze member segments, and generate workout recommendations.

It includes a relational database, automated data pipelines, machine learning models, a REST API, and an interactive dashboard.

## Features

- **Relational database:** PostgreSQL database with seven core operational tables.
- **Data generation:** Realistic synthetic gym data generated using Python.
- **ETL pipeline:** Data generation, validation, database loading, and feature engineering.
- **Data quality:** Automated checks for data integrity and consistency.
- **Churn intelligence:** Machine learning model to estimate member inactivity risk.
- **Member segmentation:** K-Means clustering to identify different member behavior groups.
- **Workout recommendations:** Rule-based workout recommendations based on member activity and goals.
- **Analytics assistant:** Natural-language questions answered using verified project analytics, with optional Gemini integration.
- **REST API:** FastAPI endpoints for churn prediction and analytics questions.
- **Interactive dashboard:** Streamlit interface for exploring gym performance and member insights.
- **Docker support:** Containerized PostgreSQL, API, and dashboard services.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Data processing and application logic |
| PostgreSQL 16 | Relational database |
| SQL | Database design and analytics |
| Pandas / NumPy | Data manipulation |
| Scikit-learn | Machine learning |
| FastAPI | REST API |
| Streamlit | Interactive dashboard |
| Docker / Docker Compose | Containerization |
| Pytest | Automated testing |
| Gemini API | AI-assisted analytics explanations |
| Git / GitHub | Version control |

## Architecture

```text
             Synthetic Gym Data
                     |
                     v
             Python Data Pipeline
                     |
                     v
                PostgreSQL
                     |
                     v
            Feature Engineering
                     |
          +----------+----------+
          |          |          |
          v          v          v
       Churn      Member     Workout
       Model    Segmentation Recommendations
          |          |          |
          +----------+----------+
                     |
              Processed Analytics
                     |
             +-------+-------+
             |               |
             v               v
          FastAPI         Streamlit
             |               |
             +-------+-------+
                     |
              Gemini Assistant
              (Optional AI layer)