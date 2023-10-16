DROP TABLE IF EXISTS urls;
DROP TABLE IF EXISTS url_checks;
CREATE TABLE urls (
	id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
	name varchar(255) UNIQUE NOT NULL,
	created_at date NOT NULL
);

CREATE TABLE url_checks (
	id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
	url_id bigint REFERENCES urls (id) NOT NULL,
	status_code integer NOT NULL,
	h1 varchar(255),
	title varchar(255),
	description text,
	created_at date NOT NULL
);
