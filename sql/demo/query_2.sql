-- Showing all job openings that are still active and haven't been filled after a month.
SELECT * FROM jobs.ads
WHERE last_seen - created > 31
AND last_seen = current_date;