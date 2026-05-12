ALTER TABLE tracked_products ADD COLUMN image_url VARCHAR(500);

CREATE TABLE IF NOT EXISTS price_alert_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    product_name VARCHAR(120) NOT NULL,
    store VARCHAR(80) NOT NULL,
    product_url VARCHAR(500) NOT NULL,
    current_price FLOAT NOT NULL,
    target_price FLOAT NOT NULL,
    currency VARCHAR(3) NOT NULL DEFAULT 'ILS',
    message VARCHAR(300) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(product_id) REFERENCES tracked_products(id)
);

CREATE INDEX IF NOT EXISTS ix_price_alert_events_product_id ON price_alert_events(product_id);
