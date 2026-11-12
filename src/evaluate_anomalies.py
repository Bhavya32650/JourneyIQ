
from pathlib import Path
import pandas as pd


def evaluate_anomalies(
    ground_truth_path="data/raw/ground_truth/ground_truth.csv",
    detected_path="data/processed/detected_anomalies.csv",
    identity_path="data/processed/identity_anomalies.csv",
    output_dir="data/processed"
):
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------
    # 1. LOAD GROUND TRUTH
    # ------------------------------------------------

    truth = pd.read_csv(ground_truth_path)

    # ------------------------------------------------
    # 2. LOAD DETECTED ANOMALIES
    # ------------------------------------------------

    detected = pd.read_csv(detected_path)

    # Load identity stitching anomalies
    identity_file = Path(identity_path)

    if identity_file.exists():
        identity_anomalies = pd.read_csv(identity_file)

        detected = pd.concat(
            [detected, identity_anomalies],
            ignore_index=True
        )
    else:
        print("Warning: Identity anomaly file not found.")

    # ------------------------------------------------
    # 3. KEEP COMPARABLE COLUMNS
    # ------------------------------------------------

    required_columns = [
        "entity_id",
        "issue_type",
        "rule_id"
    ]

    truth = truth[required_columns].copy()
    detected = detected[required_columns].copy()

    # ------------------------------------------------
    # 4. NORMALIZE TEXT VALUES
    # ------------------------------------------------

    for df in [truth, detected]:
        for col in required_columns:
            df[col] = (
                df[col]
                .astype(str)
                .str.strip()
            )

    # ------------------------------------------------
    # 5. REMOVE DUPLICATE RECORDS
    # ------------------------------------------------

    truth = truth.drop_duplicates(
        subset=["entity_id", "issue_type"]
    )

    detected = detected.drop_duplicates(
        subset=["entity_id", "issue_type"]
    )

    # ------------------------------------------------
    # 6. MATCH GROUND TRUTH WITH DETECTIONS
    # ------------------------------------------------

    comparison = truth.merge(
        detected,
        on=["entity_id", "issue_type"],
        how="outer",
        suffixes=("_expected", "_detected"),
        indicator=True
    )

    true_positives = int(
        (comparison["_merge"] == "both").sum()
    )

    false_negatives = int(
        (comparison["_merge"] == "left_only").sum()
    )

    false_positives = int(
        (comparison["_merge"] == "right_only").sum()
    )

    # ------------------------------------------------
    # 7. CALCULATE EVALUATION METRICS
    # ------------------------------------------------

    precision = (
        true_positives /
        (true_positives + false_positives)
        if true_positives + false_positives else 0
    )

    recall = (
        true_positives /
        (true_positives + false_negatives)
        if true_positives + false_negatives else 0
    )

    f1_score = (
        2 * precision * recall / (precision + recall)
        if precision + recall else 0
    )

    # ------------------------------------------------
    # 8. OVERALL EVALUATION SUMMARY
    # ------------------------------------------------

    summary = pd.DataFrame([{
        "ground_truth_count": len(truth),
        "detected_count": len(detected),
        "true_positives": true_positives,
        "false_positives": false_positives,
        "false_negatives": false_negatives,
        "precision_pct": round(precision * 100, 2),
        "recall_pct": round(recall * 100, 2),
        "f1_score_pct": round(f1_score * 100, 2)
    }])

    # ------------------------------------------------
    # 9. RULE-WISE EVALUATION
    # ------------------------------------------------

    rule_results = []

    all_rules = sorted(
        set(truth["rule_id"]) |
        set(detected["rule_id"])
    )

    for rule_id in all_rules:

        expected = truth[
            truth["rule_id"] == rule_id
        ]

        actual = detected[
            detected["rule_id"] == rule_id
        ]

        expected_keys = set(
            zip(
                expected["entity_id"],
                expected["issue_type"]
            )
        )

        actual_keys = set(
            zip(
                actual["entity_id"],
                actual["issue_type"]
            )
        )

        tp = len(expected_keys & actual_keys)
        fp = len(actual_keys - expected_keys)
        fn = len(expected_keys - actual_keys)

        p = tp / (tp + fp) if tp + fp else 0
        r = tp / (tp + fn) if tp + fn else 0

        f1 = (
            2 * p * r / (p + r)
            if p + r else 0
        )

        rule_results.append({
            "rule_id": rule_id,
            "ground_truth": len(expected_keys),
            "detected": len(actual_keys),
            "true_positives": tp,
            "false_positives": fp,
            "false_negatives": fn,
            "precision_pct": round(p * 100, 2),
            "recall_pct": round(r * 100, 2),
            "f1_score_pct": round(f1 * 100, 2)
        })

    rule_df = pd.DataFrame(rule_results)

    # ------------------------------------------------
    # 10. SAVE EVALUATION FILES
    # ------------------------------------------------

    summary.to_csv(
        output_path / "anomaly_evaluation_summary.csv",
        index=False
    )

    rule_df.to_csv(
        output_path / "anomaly_evaluation_by_rule.csv",
        index=False
    )

    comparison.to_csv(
        output_path / "anomaly_evaluation_details.csv",
        index=False
    )

    # ------------------------------------------------
    # 11. DISPLAY RESULTS
    # ------------------------------------------------

    print("\nANOMALY EVALUATION COMPLETED")

    print("\nOverall evaluation:")
    print(summary.to_string(index=False))

    print("\nRule-wise evaluation:")
    print(rule_df.to_string(index=False))

    print("\nEvaluation files saved in:", output_path)

    return summary, rule_df, comparison


if __name__ == "__main__":
    evaluate_anomalies()
