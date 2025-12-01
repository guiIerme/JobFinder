CREATE TABLE IF NOT EXISTS services_servicerequest (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    provider_id INTEGER,
    service_id INTEGER,
    custom_service_id INTEGER,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    category VARCHAR(50) NOT NULL,
    scheduled_date DATETIME NOT NULL,
    address TEXT NOT NULL,
    notes TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    rejection_reason TEXT,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES auth_user (id),
    FOREIGN KEY (provider_id) REFERENCES auth_user (id),
    FOREIGN KEY (service_id) REFERENCES services_service (id),
    FOREIGN KEY (custom_service_id) REFERENCES services_customservice (id)
);

CREATE TABLE IF NOT EXISTS services_notification (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    sender_id INTEGER,
    notification_type VARCHAR(20) NOT NULL,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN NOT NULL DEFAULT 0,
    related_object_id INTEGER,
    related_object_type VARCHAR(50),
    created_at DATETIME NOT NULL,
    FOREIGN KEY (user_id) REFERENCES auth_user (id),
    FOREIGN KEY (sender_id) REFERENCES auth_user (id)
);