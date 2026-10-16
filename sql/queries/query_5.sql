-- Showing the top 3 sales active recruiter
SELECT c.display_name, COUNT(a.adzuna_id) AS top_3
FROM jobs.ads AS a
JOIN jobs.companies AS c ON c.id = a.comp_id
WHERE last_seen = current_date
GROUP BY c.display_name
ORDER BY COUNT(a.adzuna_id) DESC LIMIT 3;