CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    company TEXT NOT NULL,
    location TEXT NOT NULL,
    type TEXT NOT NULL,
    experience_level TEXT NOT NULL,
    salary_range TEXT,
    description TEXT NOT NULL,
    requirements TEXT NOT NULL,
    benefits TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS candidates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    name TEXT,
    email TEXT,
    phone TEXT,
    score INTEGER,
    recommendation TEXT,
    full_report TEXT, -- JSON stored as text
    status TEXT DEFAULT 'Analyzed',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);