# KPI Dictionary

## order_fill_rate
Definition: Filled units / ordered units within a time window.
Tables: orders
Columns: ordered_qty, filled_qty, order_date
Unit: ratio

## late_ship_rate
Definition: % of shipments where shipped_date > promised_date.
Tables: shipments
Columns: shipped_date, promised_date
Unit: ratio

## backlog_units
Definition: Sum of ordered_qty - filled_qty where status = BACKLOG.
Tables: orders
Columns: ordered_qty, filled_qty, status
Unit: units

## on_time_delivery_rate
Definition: % of shipments with delivered_date <= promised_date.
Tables: shipments
Columns: delivered_date, promised_date
Unit: ratio

## total_revenue
Definition: Sum of order_total in a time window.
Tables: orders
Columns: order_total, order_date
Unit: usd
