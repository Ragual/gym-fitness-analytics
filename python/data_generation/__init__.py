from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"

# Reproducibility
RANDOM_SEED = 42

# Synthetic dataset size
NUM_MEMBERS = 2000

# Simulation timeline
DATA_START_DATE = "2025-01-01"
DATA_END_DATE = "2026-11-18"

# Churn prediction configuration
SNAPSHOT_DATE = "2026-09-30"
FEATURE_WINDOW_DAYS = 90
CHURN_PREDICTION_WINDOW_DAYS = 30

# Database
DB_NAME = "gym_fitness_db"
DB_HOST = "localhost"
DB_PORT = 5432
DB_USER = "postgres"