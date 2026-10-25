
CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    message VARCHAR(255) NOT NULL
);

INSERT INTO messages (message)
VALUES ('Hello from PostgreSQL Docker!');
