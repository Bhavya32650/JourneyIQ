
from pathlib import Path
import pandas as pd


def run_identity_stitching(
    data_dir="data/raw/starter",
    output_dir="data/processed"
):
    data_path = Path(data_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Load source data
    events = pd.read_csv(data_path / "journey_events.csv")
    sessions = pd.read_csv(data_path / "sessions.csv")
    customers = pd.read_csv(data_path / "customers.csv")
    links = pd.read_csv(data_path / "identity_links.csv")

    anomalies = []

    # Normalize consent values
    links["consent_status"] = (
        links["consent_status"]
        .astype(str)
        .str.strip()
        .str.lower()
        .isin(["true", "1", "yes"])
    )

    # RULE-04: Find anonymous IDs linked to multiple customers
    valid_links = links[links["consent_status"]].copy()

    mapping_counts = (
        valid_links.groupby("anonymous_id")["customer_id"]
        .nunique()
    )

    conflicting_ids = mapping_counts[
        mapping_counts > 1
    ].index.tolist()

    # Report only the additional conflicting links.
    # The first link is treated as the original link.
    for anonymous_id in conflicting_ids:
        conflict_rows = valid_links[
            valid_links["anonymous_id"] == anonymous_id
        ]

        customer_ids = sorted(
            conflict_rows["customer_id"].dropna().unique()
        )

        for _, row in conflict_rows.iloc[1:].iterrows():
            anomalies.append({
                "entity_id": row["identity_link_id"],
                "issue_type": "INCORRECT_IDENTITY_MERGE",
                "severity": "high",
                "rule_id": "RULE-04",
                "evidence": (
                    f"Anonymous ID {anonymous_id} is linked "
                    f"to multiple customers: {customer_ids}"
                )
            })

    # RULE-05: Find links without consent
    for _, row in links[~links["consent_status"]].iterrows():
        anomalies.append({
            "entity_id": row["identity_link_id"],
            "issue_type": "IDENTITY_LINK_WITHOUT_CONSENT",
            "severity": "high",
            "rule_id": "RULE-05",
            "evidence": (
                f"Identity link for {row['anonymous_id']} "
                "does not have consent"
            )
        })

    # Keep only unambiguous, consented mappings
    safe_links = valid_links[
        ~valid_links["anonymous_id"].isin(conflicting_ids)
    ].copy()

    safe_links = safe_links.drop_duplicates(
        subset=["anonymous_id", "customer_id"]
    )

    # Build anonymous ID -> customer ID mapping
    identity_map = (
        safe_links[["anonymous_id", "customer_id"]]
        .drop_duplicates(subset=["anonymous_id"])
    )

    # Resolve customer IDs in journey events
    events = events.merge(
        identity_map,
        on="anonymous_id",
        how="left",
        suffixes=("", "_resolved")
    )

    # Preserve existing customer ID; otherwise use consented mapping
    events["resolved_customer_id"] = (
        events["customer_id"]
        .combine_first(events["customer_id_resolved"])
    )

    events =events.drop(
        columns=["customer_id_resolved"],
    )

    # Add identity resolution status
    events["identity_status"] = "anonymous"

    events.loc[
        events["customer_id"].notna(),
        "identity_status"
    ] = "known_customer"

    events.loc[
        events["customer_id"].isna()
        & events["resolved_customer_id"].notna(),
        "identity_status"
    ] = "stitched_customer"

    # Never resolve ambiguous anonymous IDs
    events.loc[
        events["anonymous_id"].isin(conflicting_ids),
        "resolved_customer_id"
    ] = pd.NA

    events.loc[
        events["anonymous_id"].isin(conflicting_ids),
        "identity_status"
    ] = "identity_conflict"

    # Export resolved events
    resolved_file = output_path / "identity_resolved_events.csv"
    events.to_csv(resolved_file, index=False)

    # Export identity anomalies
    anomaly_columns = [
        "entity_id",
        "issue_type",
        "severity",
        "rule_id",
        "evidence"
    ]

    anomaly_df = pd.DataFrame(
        anomalies,
        columns=anomaly_columns
    )

    anomaly_file = output_path / "identity_anomalies.csv"
    anomaly_df.to_csv(anomaly_file, index=False)

    # Print summary
    print("\nIdentity stitching completed!")

    print("\nIdentity status summary:")
    print(events["identity_status"].value_counts().to_string())

    print("\nIdentity anomaly summary:")

    if not anomaly_df.empty:
        print(
            anomaly_df.groupby("issue_type")
            .size()
            .to_string()
        )
    else:
        print("No identity anomalies detected.")

    print(f"\nResolved events saved to: {resolved_file}")
    print(f"Identity anomalies saved to: {anomaly_file}")

    return events, anomaly_df


if __name__ == "__main__":
    run_identity_stitching()
