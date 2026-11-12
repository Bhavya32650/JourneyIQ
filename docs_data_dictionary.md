# Data dictionary (starter)
All IDs are strings and immutable. Timestamps are ISO-8601 UTC strings.
- Customer: customer_id (PK, CUS-######), consent_status (required boolean), created_at (required timestamp), lifecycle_state (active).
- Session: session_id (PK, SES-2026-######), customer_id (optional FK), anonymous_id, channel (web/app/support), started_at, ended_at, is_bot, lifecycle_state.
- JourneyEvent: event_id (PK, EVT-<session-id>-######), session_id (FK), customer_id (optional FK), anonymous_id, channel, event_type, page_id (FK), product_id (optional FK), cart_id/order_id/ticket_id (optional references), event_timestamp, ingestion_timestamp, latency_ms, is_bot.
- Page: page_id (PK), page_name, page_type.
- Product: product_id (PK), product_name, category, unit_price (currency units), lifecycle_state.
- Cart: cart_id (PK), session_id (FK), customer_id (optional FK), created_at, status.
- Order: order_id (PK), session_id (FK), customer_id (optional FK), cart_id (FK), order_timestamp, total_amount, status.
- SupportTicket: ticket_id (PK), session_id (FK), customer_id (optional FK), created_at, status.
- Experiment: experiment_id (PK), experiment_name, start_date, end_date, lifecycle_state.
- JourneyOutcome: outcome_id (PK, OUT-<session-id>), session_id (unique FK), primary_outcome, converted, abandoned, support_contact, derived_rule.
- CartItem and OrderItem are bridge/detail tables connecting carts/orders to products.
- ExperimentAssignment bridges Experiment and Session (N:M).
- IdentityLink stores consented identity relationships with effective dates.
