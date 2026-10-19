CREATE TABLE IF NOT EXISTS services (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    category TEXT NOT NULL,
    price REAL NOT NULL,
    duration INTEGER NOT NULL
);


CREATE TABLE IF NOT EXISTS clients (
    id INTEGER PRIMARY KEY,
    full_name TEXT NOT NULL,
    phone TEXT NOT NULL UNIQUE
);


CREATE TABLE IF NOT EXISTS appointments (
    id INTEGER PRIMARY KEY,
    client_id INTEGER NOT NULL,
    service_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    total REAL NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (client_id) REFERENCES clients(id),
    FOREIGN KEY (service_id) REFERENCES services(id)
);


-- Тестовые данные
INSERT INTO services (name, category, price, duration)
SELECT 'Стрижка женская', 'Стрижка', 1500.00, 60
WHERE NOT EXISTS (SELECT 1 FROM services WHERE name = 'Стрижка женская');


INSERT INTO services (name, category, price, duration)
SELECT 'Стрижка мужская', 'Стрижка', 1000.00, 45
WHERE NOT EXISTS (SELECT 1 FROM services WHERE name = 'Стрижка мужская');


INSERT INTO services (name, category, price, duration)
SELECT 'Окрашивание «Балаяж»', 'Окрашивание', 4500.00, 180
WHERE NOT EXISTS (SELECT 1 FROM services WHERE name = 'Окрашивание «Балаяж»');


INSERT INTO services (name, category, price, duration)
SELECT 'Укладка вечерняя', 'Укладка', 2000.00, 60
WHERE NOT EXISTS (SELECT 1 FROM services WHERE name = 'Укладка вечерняя');


INSERT INTO services (name, category, price, duration)
SELECT 'Маникюр классический', 'Ногти', 1200.00, 50
WHERE NOT EXISTS (SELECT 1 FROM services WHERE name = 'Маникюр классический');


INSERT INTO clients (full_name, phone)
SELECT 'Смирнова Ольга', '+7-900-111-22-33'
WHERE NOT EXISTS (SELECT 1 FROM clients WHERE phone = '+7-900-111-22-33');


INSERT INTO clients (full_name, phone)
SELECT 'Козлов Дмитрий', '+7-900-444-55-66'
WHERE NOT EXISTS (SELECT 1 FROM clients WHERE phone = '+7-900-444-55-66');
