
CREATE TABLE IF NOT EXISTS prompt (
	id SERIAL PRIMARY KEY,
	vector vector(1536),
	prompt TEXT NOT NULL,
	completion TEXT NOT NULL,
	duration FLOAT,
	time TIMESTAMPTZ DEFAULT NOW(),
	model TEXT,
	data JSONB
);
