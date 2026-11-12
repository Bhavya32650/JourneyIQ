
from pathlib import Path
import pandas as pd

FUNNEL = [
    "page_view",
    "product_view",
    "add_to_cart",
    "checkout_start",
    "purchase"
]


def build_metrics(
    data_dir="data/raw/starter",
    processed_dir="data/processed"
):
    data_dir = Path(data_dir)
    processed_dir = Path(processed_dir)
    processed_dir.mkdir(parents=True, exist_ok=True)

    # Load source data
    sessions = pd.read_csv(data_dir / "sessions.csv")
    events = pd.read_csv(data_dir / "journey_events.csv")

    events["event_timestamp"] = pd.to_datetime(
        events["event_timestamp"], utc=True
    )

    events = events.sort_values(
        ["session_id", "event_timestamp", "event_id"]
    )

    # Exclude bot sessions
    human = sessions[
        ~sessions["is_bot"].astype(str).str.lower().isin(
            ["true", "1", "yes"]
        )
    ].copy()

    eligible_ids = set(human["session_id"])

    events = events[
        events["session_id"].isin(eligible_ids)
    ].drop_duplicates(subset=["event_id"]).copy()

    # ------------------------------------------------
    # SEQUENTIAL FUNNEL ANALYSIS
    # ------------------------------------------------

    session_rows = []

    for session_id, group in events.groupby(
        "session_id", sort=False
    ):
        group = group.reset_index(drop=True)

        row = {"session_id": session_id}
        cursor = -1
        funnel_completed = True
        purchase_order_id = None

        for stage in FUNNEL:
            row[stage] = False

            if not funnel_completed:
                continue

            # Find the next required event after the previous stage
            candidates = group[
                (group.index > cursor)
                & (group["event_type"] == stage)
            ]

            if stage == "purchase":
                candidates = candidates[
                    candidates["order_id"].notna()
                ]

            if not candidates.empty:
                matched_index = candidates.index[0]

                row[stage] = True
                cursor = matched_index

                if stage == "purchase":
                    purchase_order_id = group.loc[
                        matched_index, "order_id"
                    ]
            else:
                funnel_completed = False

        row["converted"] = purchase_order_id is not None

        row["support_contact"] = (
            "ticket_created" in group["event_type"].values
        )

        row["abandoned"] = not row["converted"]
        row["event_count"] = len(group)

        session_rows.append(row)

    metrics = pd.DataFrame(session_rows)

    metrics.to_csv(
        processed_dir / "session_metrics.csv",
        index=False
    )

    # ------------------------------------------------
    # FUNNEL METRICS
    # ------------------------------------------------

    funnel_rows = []
    previous_count = None

    for stage in FUNNEL:
        count = (
            int(metrics[stage].sum())
            if not metrics.empty else 0
        )

        dropoff = (
            0
            if previous_count in (None, 0)
            else round(
                (previous_count - count)
                / previous_count * 100,
                2
            )
        )

        funnel_rows.append({
            "stage": stage,
            "sessions": count,
            "dropoff_from_previous_pct": dropoff
        })

        previous_count = count

    funnel_df = pd.DataFrame(funnel_rows)

    funnel_df.to_csv(
        processed_dir / "funnel_metrics.csv",
        index=False
    )

    # ------------------------------------------------
    # CHANNEL PERFORMANCE
    # ------------------------------------------------

    channel_data = human[
        ["session_id", "channel"]
    ].merge(
        metrics,
        on="session_id",
        how="left"
    )

    channel_data["converted"] = (
        channel_data["converted"].fillna(False).astype(bool)
    )

    channel_data["support_contact"] = (
        channel_data["support_contact"].fillna(False).astype(bool)
    )

    channel_data["abandoned"] = ~channel_data["converted"]

    channel_rows = []

    for channel_name, group in channel_data.groupby(
        "channel", dropna=False
    ):
        total_sessions = len(group)
        conversions = int(group["converted"].sum())
        abandoned = int(group["abandoned"].sum())

        conversion_rate = (
            round(conversions / total_sessions * 100, 2)
            if total_sessions else 0
        )

        abandonment_rate = (
            round(abandoned / total_sessions * 100, 2)
            if total_sessions else 0
        )

        channel_rows.append({
            "channel": channel_name,
            "total_sessions": total_sessions,
            "converted_sessions": conversions,
            "abandoned_sessions": abandoned,
            "conversion_rate_pct": conversion_rate,
            "abandonment_rate_pct": abandonment_rate,
            "support_contacts": int(
                group["support_contact"].sum()
            )
        })

    channel_df = pd.DataFrame(channel_rows)

    if not channel_df.empty:
        channel_df = channel_df.sort_values(
            "conversion_rate_pct",
            ascending=False
        )

    channel_df.to_csv(
        processed_dir / "channel_performance.csv",
        index=False
    )

    # ------------------------------------------------
    # DISPLAY RESULTS
    # ------------------------------------------------

    print("\nSequential analytics completed!")

    print("\nFunnel metrics:")
    print(funnel_df.to_string(index=False))

    print("\nChannel performance:")
    print(channel_df.to_string(index=False))

    return metrics, funnel_df, channel_df


if __name__ == "__main__":
    build_metrics()
