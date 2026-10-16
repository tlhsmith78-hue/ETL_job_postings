-- Showing all inactive job advertisements.
SELECT * FROM jobs.ads
WHERE last_seen < current_date;

