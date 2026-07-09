-- 1. CLIENTS TABLE
CREATE TABLE clients (
    client_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    home_address_text VARCHAR(255) NOT NULL,
    latitude DECIMAL(9,6),
    longitude DECIMAL(9,6),
    phone VARCHAR(15) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. WORKERS TABLE
CREATE TABLE workers (
    worker_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    age INT NOT NULL,
    experience_years INT NOT NULL,
    category VARCHAR(20) NOT NULL CHECK (category IN ('plumber', 'electrician', 'carpenter')),
    location_text VARCHAR(255) NOT NULL,
    latitude DECIMAL(9,6),
    longitude DECIMAL(9,6),
    photo_url VARCHAR(255),
    phone VARCHAR(15) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    status VARCHAR(20) DEFAULT 'available' CHECK (status IN ('available', 'busy', 'offline')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. ISSUES TABLE (Jobs)
CREATE TABLE issues (
    issue_id SERIAL PRIMARY KEY,
    client_id INT NOT NULL REFERENCES clients(client_id) ON DELETE CASCADE,
    category VARCHAR(20) NOT NULL CHECK (category IN ('plumber', 'electrician', 'carpenter')),
    description TEXT NOT NULL,
    photo_url VARCHAR(255),
    location_text VARCHAR(255) NOT NULL,
    latitude DECIMAL(9,6),
    longitude DECIMAL(9,6),
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'accepted', 'completed', 'cancelled')),
    accepted_by INT REFERENCES workers(worker_id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    accepted_at TIMESTAMP,
    completed_at TIMESTAMP
);

-- Helpful indexes for faster lookups
CREATE INDEX idx_workers_category ON workers(category);
CREATE INDEX idx_workers_status ON workers(status);
CREATE INDEX idx_issues_status ON issues(status);
CREATE INDEX idx_issues_category ON issues(category);

-- Additional indexes: composite index for the hot-path "nearby available workers
-- in category X" query, and an index on accepted_by for "this worker's jobs" lookups.
CREATE INDEX idx_workers_category_status ON workers(category, status);
CREATE INDEX idx_issues_accepted_by ON issues(accepted_by);
