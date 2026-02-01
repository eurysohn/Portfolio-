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
    (1, 100, 'East', date('now','-28 days'), 100, 95, 12000.00, 'FILLED'),
    (2, 101, 'East', date('now','-27 days'), 200, 180, 18000.00, 'PARTIAL'),
    (3, 102, 'West', date('now','-26 days'), 150, 120, 15500.00, 'PARTIAL'),
    (4, 103, 'West', date('now','-25 days'), 80, 80, 7600.00, 'FILLED'),
    (5, 104, 'Central', date('now','-24 days'), 300, 200, 30500.00, 'BACKLOG'),
    (6, 105, 'Central', date('now','-23 days'), 60, 60, 6400.00, 'FILLED'),
    (7, 106, 'East', date('now','-22 days'), 90, 70, 8900.00, 'BACKLOG'),
    (8, 107, 'West', date('now','-21 days'), 110, 100, 9800.00, 'PARTIAL'),
    (9, 108, 'Central', date('now','-20 days'), 250, 220, 26000.00, 'PARTIAL'),
    (10, 109, 'East', date('now','-19 days'), 75, 75, 7200.00, 'FILLED'),
    (11, 110, 'East', date('now','-18 days'), 130, 90, 14000.00, 'BACKLOG'),
    (12, 111, 'West', date('now','-17 days'), 95, 95, 9100.00, 'FILLED'),
    (13, 112, 'Central', date('now','-16 days'), 210, 150, 21500.00, 'PARTIAL'),
    (14, 113, 'East', date('now','-15 days'), 140, 120, 15000.00, 'PARTIAL'),
    (15, 114, 'West', date('now','-14 days'), 160, 160, 16200.00, 'FILLED'),
    (16, 115, 'East', date('now','-10 days'), 180, 170, 19000.00, 'PARTIAL'),
    (17, 116, 'West', date('now','-9 days'), 120, 120, 13500.00, 'FILLED'),
    (18, 117, 'Central', date('now','-8 days'), 200, 180, 22000.00, 'PARTIAL'),
    (19, 118, 'East', date('now','-7 days'), 150, 145, 16800.00, 'PARTIAL'),
    (20, 119, 'West', date('now','-6 days'), 90, 90, 9500.00, 'FILLED'),
    (21, 120, 'Central', date('now','-5 days'), 220, 200, 24500.00, 'PARTIAL'),
    (22, 121, 'East', date('now','-4 days'), 170, 165, 18200.00, 'PARTIAL'),
    (23, 122, 'West', date('now','-3 days'), 100, 100, 11000.00, 'FILLED'),
    (24, 123, 'Central', date('now','-2 days'), 130, 120, 14500.00, 'PARTIAL'),
    (25, 124, 'East', date('now','-1 day'), 95, 90, 10200.00, 'PARTIAL'),
    (26, 125, 'West', date('now','start of month'), 110, 105, 11800.00, 'PARTIAL'),
    (27, 126, 'Central', date('now','start of month','+1 day'), 85, 80, 9200.00, 'PARTIAL'),
    (28, 127, 'East', date('now','start of month','+2 days'), 140, 135, 15300.00, 'PARTIAL'),
    (29, 128, 'West', date('now','start of month','+3 days'), 95, 95, 10400.00, 'FILLED'),
    (30, 129, 'Central', date('now','start of month','+5 days'), 175, 160, 19200.00, 'PARTIAL');

INSERT INTO shipments VALUES
    (1, 1, 'East', date('now','-27 days'), date('now','-25 days'), date('now','-26 days'), 'UPS'),
    (2, 2, 'East', date('now','-26 days'), date('now','-24 days'), date('now','-24 days'), 'FedEx'),
    (3, 3, 'West', date('now','-25 days'), date('now','-22 days'), date('now','-23 days'), 'UPS'),
    (4, 4, 'West', date('now','-24 days'), date('now','-23 days'), date('now','-22 days'), 'DHL'),
    (5, 5, 'Central', date('now','-23 days'), date('now','-21 days'), date('now','-22 days'), 'UPS'),
    (6, 6, 'Central', date('now','-22 days'), date('now','-21 days'), date('now','-21 days'), 'FedEx'),
    (7, 7, 'East', date('now','-21 days'), date('now','-20 days'), date('now','-20 days'), 'UPS'),
    (8, 8, 'West', date('now','-20 days'), date('now','-19 days'), date('now','-19 days'), 'DHL'),
    (9, 9, 'Central', date('now','-19 days'), date('now','-17 days'), date('now','-18 days'), 'UPS'),
    (10, 10, 'East', date('now','-18 days'), date('now','-16 days'), date('now','-17 days'), 'FedEx'),
    (11, 11, 'East', date('now','-17 days'), date('now','-16 days'), date('now','-16 days'), 'UPS'),
    (12, 12, 'West', date('now','-16 days'), date('now','-14 days'), date('now','-15 days'), 'DHL'),
    (13, 13, 'Central', date('now','-15 days'), date('now','-13 days'), date('now','-13 days'), 'UPS'),
    (14, 14, 'East', date('now','-14 days'), date('now','-12 days'), date('now','-13 days'), 'FedEx'),
    (15, 15, 'West', date('now','-13 days'), date('now','-11 days'), date('now','-11 days'), 'UPS'),
    (16, 16, 'East', date('now','-9 days'), date('now','-8 days'), date('now','-8 days'), 'FedEx'),
    (17, 17, 'West', date('now','-8 days'), date('now','-7 days'), date('now','-7 days'), 'UPS'),
    (18, 18, 'Central', date('now','-7 days'), date('now','-6 days'), date('now','-6 days'), 'DHL'),
    (19, 19, 'East', date('now','-6 days'), date('now','-5 days'), date('now','-5 days'), 'UPS'),
    (20, 20, 'West', date('now','-5 days'), date('now','-4 days'), date('now','-4 days'), 'FedEx'),
    (21, 21, 'Central', date('now','-4 days'), date('now','-3 days'), date('now','-3 days'), 'UPS'),
    (22, 22, 'East', date('now','-3 days'), date('now','-2 days'), date('now','-2 days'), 'DHL'),
    (23, 23, 'West', date('now','-2 days'), date('now','-1 day'), date('now','-1 day'), 'FedEx'),
    (24, 24, 'Central', date('now','-1 day'), date('now'), date('now'), 'UPS'),
    (25, 25, 'East', date('now'), date('now'), date('now'), 'DHL'),
    (26, 26, 'West', date('now','start of month','+1 day'), date('now','start of month','+2 days'), date('now','start of month','+2 days'), 'UPS'),
    (27, 27, 'Central', date('now','start of month','+2 days'), date('now','start of month','+3 days'), date('now','start of month','+3 days'), 'FedEx'),
    (28, 28, 'East', date('now','start of month','+3 days'), date('now','start of month','+4 days'), date('now','start of month','+4 days'), 'DHL'),
    (29, 29, 'West', date('now','start of month','+4 days'), date('now','start of month','+5 days'), date('now','start of month','+5 days'), 'UPS'),
    (30, 30, 'Central', date('now','start of month','+6 days'), date('now','start of month','+7 days'), date('now','start of month','+7 days'), 'FedEx');

INSERT INTO inventory VALUES
    ('SKU-100', 'ATL', 500, 120),
    ('SKU-200', 'DAL', 300, 80),
    ('SKU-300', 'LAX', 150, 50),
    ('SKU-400', 'CHI', 220, 60),
    ('SKU-500', 'NYC', 450, 100);
