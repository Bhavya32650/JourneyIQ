
from pathlib import Path
import pandas as pd


def detect(
    data_dir="data/raw/starter",
    output="data/processed/detected_anomalies.csv"
):

    data_path = Path(data_dir)

    events = pd.read_csv(data_path / "journey_events.csv")
    sessions = pd.read_csv(data_path / "sessions.csv")

    issues = []

    # Parse timestamps
    events["event_timestamp"] = pd.to_datetime(
        events["event_timestamp"],
        utc=True
    )

    events["ingestion_timestamp"] = pd.to_datetime(
        events["ingestion_timestamp"],
        utc=True
    )

    # --------------------------------
    # RULE-01: DELAYED EVENT INGESTION
    # --------------------------------

    events["delay_seconds"] = (
        events["ingestion_timestamp"]
        - events["event_timestamp"]
    ).dt.total_seconds()

    delayed = events[events["delay_seconds"] > 3600]

    for _, row in delayed.iterrows():

        issues.append({
            "entity_id": row["event_id"],
            "issue_type": "DELAYED_INGESTION",
            "severity": "medium",
            "rule_id": "RULE-01",
            "evidence": (
                f"Ingestion delay "
                f"{row['delay_seconds']:.0f} seconds"
            )
        })

    # --------------------------------
    # RULE-02: DUPLICATE PURCHASE EVENT
    # --------------------------------

    purchases = events[
        (events["event_type"] == "purchase")
        & events["order_id"].notna()
        & (events["order_id"].astype(str).str.strip() != "")
    ].copy()

    purchases = purchases.sort_values("event_timestamp")

    duplicate_purchases = purchases[
        purchases.duplicated(
            subset=["order_id"],
            keep="first"
        )
    ]

    for _, row in duplicate_purchases.iterrows():

        issues.append({
            "entity_id": row["event_id"],
            "issue_type": "DUPLICATE_PURCHASE_EVENT",
            "severity": "high",
            "rule_id": "RULE-02",
            "evidence": f"Repeated purchase reference for order {row['order_id']}"
        })

    # --------------------------------
    # RULE-03: BOT TRAFFIC
    # --------------------------------

    bot_sessions = sessions[
        sessions["is_bot"].astype(str).str.lower().isin(
            ["true", "1", "yes"]
        )
    ]

    for _, row in bot_sessions.iterrows():

        issues.append({
            "entity_id": row["session_id"],
            "issue_type": "BOT_TRAFFIC",
            "severity": "medium",
            "rule_id": "RULE-03",
            "evidence": "Session marked as bot traffic"
        })

    # --------------------------------
    # SAVE ANOMALY REPORT
    # --------------------------------

    columns = [
        "entity_id",
        "issue_type",
        "severity",
        "rule_id",
        "evidence"
    ]

    result = pd.DataFrame(issues, columns=columns)

    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    result.to_csv(output_path, index=False)

    print("\nAnomaly detection completed!")

    if not result.empty:
        print("\nAnomaly summary:")
        print(
            result.groupby(
                ["issue_type", "severity"]
            ).size().to_string()
        )
    else:
        print("No anomalies detected.")

    print(f"\nTotal anomalies: {len(result)}")

    return result


if __name__ == "__main__":
    detect()
