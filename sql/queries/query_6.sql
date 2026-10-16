-- Showing all active job openings from the top recruiter
WITH top_1 AS (
	SELECT c.id, COUNT(a.adzuna_id)
	FROM jobs.ads AS a
	JOIN jobs.companies AS c ON c.id = a.comp_id
	WHERE last_seen = current_date
	GROUP BY c.id
	ORDER BY COUNT(a.adzuna_id) DESC LIMIT 1
)
SELECT * FROM jobs.ads AS a
JOIN top_1 AS t ON t.id = a.comp_id
WHERE last_seen = current_date;