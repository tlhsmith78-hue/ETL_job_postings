BEGIN;

TRUNCATE TABLE jobs.temp_data;
COPY jobs.temp_data
FROM 'local_path_file.csv'
WITH (
	HEADER false,
	FORMAT csv,
	DELIMITER ','
);

INSERT INTO jobs.companies (display_name)
SELECT DISTINCT company_display_name 
FROM jobs.temp_data
WHERE company_display_name IS NOT NULL
ON CONFLICT (display_name) DO NOTHING;

INSERT INTO jobs.locations(country, region, city, display_name)
SELECT DISTINCT location_country,
location_region,
location_city,
location_display_name
FROM jobs.temp_data
ON CONFLICT(country, region, city, display_name) DO NOTHING;

INSERT INTO jobs.ads (adzuna_id, adref, created, redirect_url,
category_label, category_tag, 
first_seen, last_seen, title,
description,contract_time, contract_type,
salary_is_predicted, salary_min, salary_max,
comp_id, loc_id)
SELECT t.id, t.adref, t.created, t.redirect_url,
t.category_label, t.category_tag,
current_date, current_date, t.title,
t.description, t.contract_time, t.contract_type,
t.salary_is_predicted, t.salary_min, t.salary_max,
c.id, l.id
FROM jobs.temp_data AS t
LEFT JOIN jobs.companies AS c ON c.display_name = t.company_display_name
LEFT JOIN jobs.locations AS l ON l.country = t.location_country
	AND l.region = t.location_region
	AND l.city = t.location_city
	AND l.display_name = t.location_display_name
ON CONFLICT(adzuna_id) DO UPDATE
SET last_seen = current_date;

COMMIT;