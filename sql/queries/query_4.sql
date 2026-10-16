-- Showing job the amount of openings per job title, ordered by their minimum annouced salary.
SELECT COUNT(*) AS nbr_openings, title, ROUND(AVG(salary_min)) AS avg_min, ROUND(AVG(salary_max)) AS avg_max
FROM jobs.ads
WHERE last_seen = current_date
GROUP BY title
ORDER BY avg_min DESC;