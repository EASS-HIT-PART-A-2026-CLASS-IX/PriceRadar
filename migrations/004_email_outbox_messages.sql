CREATE TABLE IF NOT EXISTS email_outbox_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    alert_event_id INTEGER,
    product_id INTEGER NOT NULL,
    recipient_email VARCHAR(254) NOT NULL,
    subject VARCHAR(180) NOT NULL,
    product_name VARCHAR(120) NOT NULL,
    store VARCHAR(80) NOT NULL,
    product_url VARCHAR(500) NOT NULL,
    current_price FLOAT NOT NULL,
    target_price FLOAT NOT NULL,
    currency VARCHAR(3) NOT NULL DEFAULT 'ILS',
    status VARCHAR(40) NOT NULL DEFAULT 'sent',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(alert_event_id) REFERENCES price_alert_events(id),
    FOREIGN KEY(product_id) REFERENCES tracked_products(id)
);

CREATE INDEX IF NOT EXISTS ix_email_outbox_messages_product_id ON email_outbox_messages(product_id);
CREATE INDEX IF NOT EXISTS ix_email_outbox_messages_recipient_email ON email_outbox_messages(recipient_email);
