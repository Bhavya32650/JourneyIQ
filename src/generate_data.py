
import argparse
import csv
import random
from pathlib import Path
from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd


EVENTS_PER_SESSION = 20


def sid(i):
    return f"SES-2026-{i:06d}"


def eid(session, i):
    return f"EVT-{session}-{i:06d}"


def write_csv(path, rows, columns):
    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows, columns=columns).to_csv(path, index=False)


def generate(n_sessions, n_events, seed, output):

    if n_events < n_sessions:
        raise ValueError("Events must be >= sessions")

    if n_events > n_sessions * EVENTS_PER_SESSION:
        raise ValueError(
            f"Maximum supported events for {n_sessions} sessions "
            f"is {n_sessions * EVENTS_PER_SESSION}"
        )

    rng = np.random.default_rng(seed)
    random.seed(seed)

    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)

    # ==========================================
    # 1. MASTER DATA
    # ==========================================

    customers = []

    for i in range(1, max(2, n_sessions // 2) + 1):
        customers.append({
            "customer_id": f"CUS-{i:06d}",
            "consent_status": bool(rng.random() < 0.75),
            "created_at": "2026-01-01T00:00:00Z",
            "lifecycle_state": "active"
        })

    pages = [
        {
            "page_id": f"PAGE-{i:06d}",
            "page_name": name,
            "page_type": page_type
        }
        for i, (name, page_type) in enumerate([
            ("Home", "landing"),
            ("Catalog", "listing"),
            ("Product Detail", "product"),
            ("Cart", "cart"),
            ("Checkout", "checkout"),
            ("Confirmation", "confirmation")
        ], 1)
    ]

    products = [
        {
            "product_id": f"PROD-{i:06d}",
            "product_name": f"Product {i}",
            "category": ["Electronics", "Fashion", "Home"][i % 3],
            "unit_price": round(float(rng.uniform(10, 500)), 2),
            "lifecycle_state": "active"
        }
        for i in range(1, 101)
    ]

    experiments = [{
        "experiment_id": "EXP-2026-000001",
        "experiment_name": "Checkout UX Experiment",
        "start_date": "2026-01-01",
        "end_date": "2026-12-31",
        "lifecycle_state": "active"
    }]

    write_csv(output / "customers.csv", customers, list(customers[0]))
    write_csv(output / "pages.csv", pages, list(pages[0]))
    write_csv(output / "products.csv", products, list(products[0]))
    write_csv(output / "experiments.csv", experiments, list(experiments[0]))

    # ==========================================
    # 2. INITIALIZE DATA COLLECTIONS
    # ==========================================

    sessions = []
    carts = []
    orders = []
    tickets = []
    assignments = []
    links = []
    outcomes = []

    gt_rows = []

    event_path = output / "journey_events.csv"

    gt_path = (
        output.parent / "ground_truth" / "ground_truth.csv"
    )

    gt_path.parent.mkdir(parents=True, exist_ok=True)

    event_columns = [
        "event_id",
        "session_id",
        "customer_id",
        "anonymous_id",
        "channel",
        "event_type",
        "page_id",
        "product_id",
        "cart_id",
        "order_id",
        "ticket_id",
        "event_timestamp",
        "ingestion_timestamp",
        "latency_ms",
        "is_bot"
    ]

    event_count = 0

    base = datetime(
        2026, 10, 1, tzinfo=timezone.utc
    )

    # ==========================================
    # 3. GENERATE CUSTOMER SESSIONS AND EVENTS
    # ==========================================

    with event_path.open(
        "w",
        newline="",
        encoding="utf-8"
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=event_columns
        )

        writer.writeheader()

        for i in range(1, n_sessions + 1):

            session = sid(i)

            known = (i % 2 == 0)

            customer = (
                f"CUS-{((i - 1) // 2) + 1:06d}"
                if known else ""
            )

            anonymous = f"ANON-{i:07d}"

            channel = ["web", "app", "support"][i % 3]

            start = base + timedelta(
                minutes=int(rng.integers(0, 400000))
            )

            is_bot = (i % 97 == 0)

            pattern = i % 5

            # ----------------------------------
            # CUSTOMER JOURNEY PATTERNS
            # ----------------------------------

            if pattern == 0:

                types = [
                    "page_view",
                    "product_view",
                    "add_to_cart",
                    "checkout_start",
                    "payment_attempt",
                    "purchase"
                ]

                outcome = "conversion"

            elif pattern == 1:

                types = [
                    "page_view",
                    "product_view"
                ]

                outcome = "abandonment"

            elif pattern == 2:

                types = [
                    "page_view",
                    "product_view",
                    "add_to_cart",
                    "checkout_start",
                    "payment_attempt",
                    "payment_failed",
                    "ticket_created"
                ]

                outcome = "support_contact"

            elif pattern == 3:

                types = [
                    "app_open",
                    "page_view",
                    "product_view",
                    "add_to_cart"
                ]

                outcome = "abandonment"

            else:

                types = [
                    "page_view",
                    "product_view",
                    "add_to_cart",
                    "checkout_start",
                    "payment_attempt",
                    "payment_failed"
                ]

                outcome = "abandonment"

            # ----------------------------------
            # CONTROLLED DUPLICATE PURCHASE CASE
            # Session 113, 226, etc.
            # ----------------------------------

            if i % 113 == 0:

                types = [
                    "page_view",
                    "product_view",
                    "add_to_cart",
                    "checkout_start",
                    "payment_attempt",
                    "purchase"
                ]

                outcome = "conversion"

            cart_id = (
                f"CART-{i:06d}"
                if "add_to_cart" in types else ""
            )

            order_id = (
                f"ORD-{i:06d}"
                if "purchase" in types else ""
            )

            ticket_id = (
                f"TKT-{i:06d}"
                if "ticket_created" in types else ""
            )

            # ----------------------------------
            # SESSION TABLE
            # ----------------------------------

            sessions.append({
                "session_id": session,
                "customer_id": customer or None,
                "anonymous_id": anonymous,
                "channel": channel,
                "started_at": start.isoformat(),
                "ended_at": (
                    start + timedelta(minutes=20)
                ).isoformat(),
                "is_bot": is_bot,
                "lifecycle_state": "completed"
            })

            # ----------------------------------
            # CART TABLE
            # ----------------------------------

            if cart_id:

                carts.append({
                    "cart_id": cart_id,
                    "session_id": session,
                    "customer_id": customer or None,
                    "created_at": start.isoformat(),
                    "status": (
                        "converted" if order_id else "abandoned"
                    )
                })

            # ----------------------------------
            # ORDER TABLE
            # ----------------------------------

            if order_id:

                product = f"PROD-{(i % 100) + 1:06d}"

                price = next(
                    p["unit_price"]
                    for p in products
                    if p["product_id"] == product
                )

                orders.append({
                    "order_id": order_id,
                    "session_id": session,
                    "customer_id": customer or None,
                    "cart_id": cart_id,
                    "order_timestamp": (
                        start + timedelta(minutes=15)
                    ).isoformat(),
                    "total_amount": price,
                    "status": "paid"
                })

            # ----------------------------------
            # SUPPORT TICKET TABLE
            # ----------------------------------

            if ticket_id:

                tickets.append({
                    "ticket_id": ticket_id,
                    "session_id": session,
                    "customer_id": customer or None,
                    "created_at": (
                        start + timedelta(minutes=18)
                    ).isoformat(),
                    "status": "open"
                })

            # ----------------------------------
            # EXPERIMENT ASSIGNMENTS
            # ----------------------------------

            assignments.append({
                "experiment_id": "EXP-2026-000001",
                "session_id": session,
                "variant": "A" if i % 2 else "B",
                "assigned_at": start.isoformat()
            })

            # ----------------------------------
            # CONSENT-BASED IDENTITY LINKS
            # ----------------------------------

            if (
                known
                and customers[(i - 1) // 2]["consent_status"]
            ):

                links.append({
                    "identity_link_id": f"LINK-{i:06d}",
                    "customer_id": customer,
                    "anonymous_id": anonymous,
                    "consent_status": True,
                    "valid_from": start.isoformat(),
                    "valid_to": ""
                })

            # ==================================
            # 4. EVENT COUNT DISTRIBUTION
            # ==================================

            remaining_sessions = n_sessions - i + 1

            remaining_events = n_events - event_count

            count = min(
                max(
                    1,
                    remaining_events - (remaining_sessions - 1)
                ),
                EVENTS_PER_SESSION
            )

            count = max(1, count)

            event_types = list(types)

            # Add one intentional duplicate purchase
            if i % 113 == 0:
                event_types.append("purchase")

            # Fill remaining events with browsing events
            while len(event_types) < count:

                if len(event_types) % 2 == 0:
                    event_types.append("page_view")
                else:
                    event_types.append("product_view")

            event_types = event_types[:count]

            # ==================================
            # 5. GENERATE JOURNEY EVENTS
            # ==================================

            for j in range(1, count + 1):

                event_count += 1

                etype = event_types[j - 1]

                occurrence = start + timedelta(
                    minutes=(j - 1) * 2
                )

                delay = int(rng.integers(0, 120))

                # ----------------------------------
                # RULE-01: DELAYED INGESTION
                # ----------------------------------

                if i % 101 == 0 and j == 2:

                    delay = 7200

                    gt_rows.append({
                        "issue_id": f"ISS-{len(gt_rows)+1:06d}",
                        "entity_type": "JourneyEvent",
                        "entity_id": eid(session, j),
                        "issue_type": "DELAYED_INGESTION",
                        "expected_decision": "ORDER_BY_EVENT_TIMESTAMP",
                        "rule_id": "RULE-01"
                    })

                # ----------------------------------
                # RULE-02: DUPLICATE PURCHASE
                # ----------------------------------

                if i % 113 == 0 and j == 7:

                    gt_rows.append({
                        "issue_id": f"ISS-{len(gt_rows)+1:06d}",
                        "entity_type": "JourneyEvent",
                        "entity_id": eid(session, j),
                        "issue_type": "DUPLICATE_PURCHASE_EVENT",
                        "expected_decision": "COUNT_DISTINCT_ORDER_ONCE",
                        "rule_id": "RULE-02"
                    })

                # ----------------------------------
                # RULE-03: BOT TRAFFIC
                # ----------------------------------

                if is_bot and j == 1:

                    gt_rows.append({
                        "issue_id": f"ISS-{len(gt_rows)+1:06d}",
                        "entity_type": "Session",
                        "entity_id": session,
                        "issue_type": "BOT_TRAFFIC",
                        "expected_decision": "EXCLUDE_FROM_HUMAN_FUNNEL",
                        "rule_id": "RULE-03"
                    })

                event_channel = (
                    "support"
                    if etype == "ticket_created"
                    else channel
                )

                row = {
                    "event_id": eid(session, j),
                    "session_id": session,
                    "customer_id": customer or None,
                    "anonymous_id": anonymous,
                    "channel": event_channel,
                    "event_type": etype,
                    "page_id": f"PAGE-{((j - 1) % 6) + 1:06d}",
                    "product_id": (
                        f"PROD-{(i % 100) + 1:06d}"
                        if etype in (
                            "product_view",
                            "add_to_cart",
                            "purchase"
                        )
                        else ""
                    ),
                    "cart_id": cart_id,
                    "order_id": (
                        order_id if etype == "purchase" else ""
                    ),
                    "ticket_id": (
                        ticket_id if etype == "ticket_created" else ""
                    ),
                    "event_timestamp": occurrence.isoformat(),
                    "ingestion_timestamp": (
                        occurrence + timedelta(seconds=delay)
                    ).isoformat(),
                    "latency_ms": int(rng.integers(50, 1500)),
                    "is_bot": is_bot
                }

                writer.writerow(row)

            # ----------------------------------
            # JOURNEY OUTCOMES
            # ----------------------------------

            outcomes.append({
                "outcome_id": f"OUT-{session}",
                "session_id": session,
                "primary_outcome": outcome,
                "converted": outcome == "conversion",
                "abandoned": outcome == "abandonment",
                "support_contact": outcome == "support_contact",
                "derived_rule": "RULE-OUTCOME-01"
            })

    # ==========================================
    # 6. CONTROLLED IDENTITY MERGE ANOMALY
    # ==========================================

    # Session 114 is linked to CUS-000057.
    # Add a second conflicting customer mapping.

    if n_sessions >= 114:

        links = [
            link for link in links
            if link["anonymous_id"] != "ANON-0000114"
        ]

        links.append({
            "identity_link_id": "LINK-000114",
            "customer_id": "CUS-000057",
            "anonymous_id": "ANON-0000114",
            "consent_status": True,
            "valid_from": "2026-10-01T00:00:00+00:00",
            "valid_to": ""
        })

        links.append({
            "identity_link_id": "LINK-ERR-000114",
            "customer_id": "CUS-000058",
            "anonymous_id": "ANON-0000114",
            "consent_status": True,
            "valid_from": "2026-10-01T00:00:00+00:00",
            "valid_to": ""
        })

        gt_rows.append({
            "issue_id": f"ISS-{len(gt_rows)+1:06d}",
            "entity_type": "IdentityLink",
            "entity_id": "LINK-ERR-000114",
            "issue_type": "INCORRECT_IDENTITY_MERGE",
            "expected_decision": "REJECT_CONFLICTING_MAPPING",
            "rule_id": "RULE-04"
        })

    # ==========================================
    # 7. EXPORT TABLES
    # ==========================================

    tables = {
        "sessions.csv": sessions,
        "carts.csv": carts,
        "orders.csv": orders,
        "support_tickets.csv": tickets,
        "experiment_assignments.csv": assignments,
        "identity_links.csv": links,
        "journey_outcomes.csv": outcomes
    }

    for name, rows in tables.items():

        if rows:
            write_csv(
                output / name,
                rows,
                list(rows[0])
            )
        else:
            (output / name).write_text(
                "",
                encoding="utf-8"
            )

    # ==========================================
    # 8. CART ITEMS
    # ==========================================

    cart_items = [
        {
            "cart_item_id": f"CI-{i:06d}",
            "cart_id": cart["cart_id"],
            "product_id": f"PROD-{(i % 100) + 1:06d}",
            "quantity": 1
        }
        for i, cart in enumerate(carts, 1)
    ]

    write_csv(
        output / "cart_items.csv",
        cart_items,
        [
            "cart_item_id",
            "cart_id",
            "product_id",
            "quantity"
        ]
    )

    # ==========================================
    # 9. ORDER ITEMS
    # ==========================================

    order_items = [
        {
            "order_item_id": f"OI-{i:06d}",
            "order_id": order["order_id"],
            "product_id": f"PROD-{(int(order['order_id'].split('-')[1]) % 100) + 1:06d}",
            "quantity": 1,
            "unit_price": order["total_amount"]
        }
        for i, order in enumerate(orders, 1)
    ]

    write_csv(
        output / "order_items.csv",
        order_items,
        [
            "order_item_id",
            "order_id",
            "product_id",
            "quantity",
            "unit_price"
        ]
    )

    # ==========================================
    # 10. EXPORT GROUND TRUTH
    # ==========================================

    write_csv(
        gt_path,
        gt_rows,
        [
            "issue_id",
            "entity_type",
            "entity_id",
            "issue_type",
            "expected_decision",
            "rule_id"
        ]
    )

    print("\nDATA GENERATION COMPLETED")

    print(f"Sessions generated: {n_sessions:,}")
    print(f"Events generated: {event_count:,}")
    print(f"Ground truth anomalies: {len(gt_rows)}")

    print(f"\nData location: {output}")
    print(f"Ground truth location: {gt_path}")


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--sessions",
        type=int,
        default=100
    )

    parser.add_argument(
        "--events",
        type=int,
        default=2000
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=20261022
    )

    parser.add_argument(
        "--output",
        default="data/raw/starter"
    )

    args = parser.parse_args()

    generate(
        args.sessions,
        args.events,
        args.seed,
        args.output
    )
