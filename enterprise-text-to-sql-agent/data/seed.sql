DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS shipments;
DROP TABLE IF EXISTS inventory;

CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    business_unit TEXT NOT NULL,
    order_date TEXT NOT NULL,
    ordered_qty INTEGER NOT NULL,
    filled_qty INTEGER NOT NULL,
    order_total REAL NOT NULL,
    status TEXT NOT NULL
);

CREATE TABLE shipments (
    shipment_id INTEGER PRIMARY KEY,
    order_id INTEGER NOT NULL,
    business_unit TEXT NOT NULL,
    shipped_date TEXT NOT NULL,
    delivered_date TEXT NOT NULL,
    promised_date TEXT NOT NULL,
    carrier TEXT NOT NULL
);

CREATE TABLE inventory (
    sku TEXT PRIMARY KEY,
    warehouse TEXT NOT NULL,
    on_hand_qty INTEGER NOT NULL,
    safety_stock_qty INTEGER NOT NULL
);

INSERT INTO orders VALUES
    (1, 100, 'East', '2026-01-01', 100, 95, 12000.00, 'FILLED'),
    (2, 101, 'East', '2026-01-02', 200, 180, 18000.00, 'PARTIAL'),
    (3, 102, 'West', '2026-01-03', 150, 120, 15500.00, 'PARTIAL'),
    (4, 103, 'West', '2026-01-05', 80, 80, 7600.00, 'FILLED'),
    (5, 104, 'Central', '2026-01-08', 300, 200, 30500.00, 'BACKLOG'),
    (6, 105, 'Central', '2026-01-10', 60, 60, 6400.00, 'FILLED'),
    (7, 106, 'East', '2026-01-12', 90, 70, 8900.00, 'BACKLOG'),
    (8, 107, 'West', '2026-01-14', 110, 100, 9800.00, 'PARTIAL'),
    (9, 108, 'Central', '2026-01-15', 250, 220, 26000.00, 'PARTIAL'),
    (10, 109, 'East', '2026-01-16', 75, 75, 7200.00, 'FILLED'),
    (11, 110, 'East', '2026-01-18', 130, 90, 14000.00, 'BACKLOG'),
    (12, 111, 'West', '2026-01-19', 95, 95, 9100.00, 'FILLED'),
    (13, 112, 'Central', '2026-01-20', 210, 150, 21500.00, 'PARTIAL'),
    (14, 113, 'East', '2026-01-22', 140, 120, 15000.00, 'PARTIAL'),
    (15, 114, 'West', '2026-01-23', 160, 160, 16200.00, 'FILLED');

INSERT INTO shipments VALUES
    (1, 1, 'East', '2026-01-02', '2026-01-04', '2026-01-03', 'UPS'),
    (2, 2, 'East', '2026-01-03', '2026-01-05', '2026-01-05', 'FedEx'),
    (3, 3, 'West', '2026-01-05', '2026-01-08', '2026-01-07', 'UPS'),
    (4, 4, 'West', '2026-01-06', '2026-01-07', '2026-01-08', 'DHL'),
    (5, 5, 'Central', '2026-01-10', '2026-01-12', '2026-01-11', 'UPS'),
    (6, 6, 'Central', '2026-01-11', '2026-01-12', '2026-01-12', 'FedEx'),
    (7, 7, 'East', '2026-01-13', '2026-01-14', '2026-01-14', 'UPS'),
    (8, 8, 'West', '2026-01-15', '2026-01-16', '2026-01-16', 'DHL'),
    (9, 9, 'Central', '2026-01-16', '2026-01-18', '2026-01-17', 'UPS'),
    (10, 10, 'East', '2026-01-17', '2026-01-19', '2026-01-18', 'FedEx'),
    (11, 11, 'East', '2026-01-19', '2026-01-20', '2026-01-20', 'UPS'),
    (12, 12, 'West', '2026-01-20', '2026-01-22', '2026-01-21', 'DHL'),
    (13, 13, 'Central', '2026-01-21', '2026-01-23', '2026-01-23', 'UPS'),
    (14, 14, 'East', '2026-01-23', '2026-01-25', '2026-01-24', 'FedEx'),
    (15, 15, 'West', '2026-01-24', '2026-01-26', '2026-01-26', 'UPS');

INSERT INTO inventory VALUES
    ('SKU-100', 'ATL', 500, 120),
    ('SKU-200', 'DAL', 300, 80),
    ('SKU-300', 'LAX', 150, 50),
    ('SKU-400', 'CHI', 220, 60),
    ('SKU-500', 'NYC', 450, 100);
