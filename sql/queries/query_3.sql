-- Showing the average salary range for sales positions in Paris
SELECT ROUND(AVG(salary_min)) AS avg_min, ROUND(AVG(salary_max)) AS avg_max
FROM jobs.ads
WHERE last_seen = current_date;