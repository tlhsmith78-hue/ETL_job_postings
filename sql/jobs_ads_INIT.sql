CREATE SCHEMA jobs;

CREATE TABLE IF NOT EXISTS jobs.temp_data (
	adref TEXT,
	category_label TEXT,
	category_tag TEXT,
	company_display_name TEXT,
	contract_time TEXT CHECK(contract_time IN ('full_time', 'half-time')),
	contract_type TEXT CHECK(contract_type IN ('permanent', 'temporary')),
	created DATE,
	description TEXT,
	id BIGINT PRIMARY KEY,
	location_country TEXT,
	location_region TEXT,
	location_city TEXT,
	location_display_name TEXT,
	redirect_url TEXT,
	salary_is_predicted BOOLEAN,
	salary_max REAL,
	salary_min REAL,
	title TEXT,
	source TEXT,
	trans_run DATE
);

CREATE TABLE IF NOT EXISTS jobs.companies (
	id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
	display_name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS jobs.locations (
	id INT GENERATED ALWAYS AS  IDENTITY PRIMARY KEY,
	country TEXT,
	region TEXT,
	city TEXT,
	display_name TEXT NOT NULL,
	UNIQUE (country, region, city, display_name)
);

CREATE TABLE IF NOT EXISTS jobs.ads (
	adzuna_id BIGINT PRIMARY KEY,
	adref TEXT,
	created DATE,
	redirect_url TEXT,
	category_label TEXT,
	category_tag TEXT,
	first_seen DATE,
	last_seen DATE,
	title TEXT,
	description TEXT,
	contract_time TEXT,
	contract_type TEXT,
	salary_is_predicted BOOLEAN,
	salary_min REAL,
	salary_max REAL,
	comp_id INT REFERENCES jobs.companies,
	loc_id INT REFERENCES jobs.locations
);
