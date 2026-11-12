
from pathlib import Path

import pandas as pd

from src.validation import validate
from src.anomaly_detection import detect
from src.identity_stitching import run_identity_stitching


DATA_DIR = Path("data/raw/starter")
PROCESSED_DIR = Path("data/processed")


# 1. Check required source files
def test_starter_files_exist():
    required_files = [
        "customers.csv",
        "sessions.csv",
        "journey_events.csv",
        "products.csv",
        "pages.csv",
        "identity_links.csv",
    ]

    for filename in required_files:
        assert (DATA_DIR / filename).exists()


# 2. Check event IDs are unique
def test_event_ids_unique():
    events = pd.read_csv(DATA_DIR / "journey_events.csv")
    assert events["event_id"].is_unique


# 3. Check every event belongs to an existing session
def test_event_session_links():
    events = pd.read_csv(DATA_DIR / "journey_events.csv")
    sessions = pd.read_csv(DATA_DIR / "sessions.csv")

    assert events["session_id"].isin(
        sessions["session_id"]
    ).all()


# 4. Check validation rules
def test_data_validation():
    result = validate()

    assert result["failed"] == 0
    assert result["passed"] == 9


# 5. Check bot traffic detection
def test_bot_traffic_detection():
    anomalies = detect()

    assert (
        anomalies["issue_type"] == "BOT_TRAFFIC"
    ).sum() >= 1


# 6. Check delayed ingestion detection
def test_delayed_ingestion_detection():
    anomalies = detect()

    assert (
        anomalies["issue_type"] == "DELAYED_INGESTION"
    ).sum() >= 1


# 7. Check duplicate purchase detection
def test_duplicate_purchase_detection():
    anomalies = detect()

    assert (
        anomalies["issue_type"]
        == "DUPLICATE_PURCHASE_EVENT"
    ).sum() >= 1


# 8. Check incorrect identity merge detection
def test_identity_merge_detection():
    _, anomalies = run_identity_stitching()

    assert (
        anomalies["issue_type"]
        == "INCORRECT_IDENTITY_MERGE"
    ).sum() == 1

    assert (
        anomalies["entity_id"] == "LINK-ERR-000114"
    ).any()


# 9. Check conflicting identities are not stitched
def test_identity_conflict_handling():
    events, _ = run_identity_stitching()

    conflict_events = events[
        events["anonymous_id"] == "ANON-0000114"
    ]

    assert len(conflict_events) > 0

    assert (
        conflict_events["identity_status"]
        == "identity_conflict"
    ).all()

    assert conflict_events["resolved_customer_id"].isna().all()


# 10. Check analytics output
def test_analytics_output_exists():
    expected_files = [
        "session_metrics.csv",
        "funnel_metrics.csv",
    ]

    for filename in expected_files:
        assert (PROCESSED_DIR / filename).exists()