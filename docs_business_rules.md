# Business rules
1. Session timeout: 30 minutes of inactivity; this starter assigns sessions before event generation.
2. Sort journey events by event_timestamp, not ingestion_timestamp.
3. Cross-device identity links are created only for known customers with consent_status=true.
4. Funnel: page_view -> product_view -> add_to_cart -> checkout_start -> purchase.
5. A conversion requires a valid distinct paid order; repeated purchase events for one order count once.
6. Bot sessions are excluded from human funnel metrics.
7. Ground truth is for evaluation only and must never be an input feature.
8. State changes should be appended to state history in the full implementation.
