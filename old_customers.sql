SELECT b.json_data
FROM (
    SELECT user_id, MAX(updated_at) as updated_latest
    FROM macroplate.customer_api_logs
    GROUP BY user_id
) a
INNER JOIN macroplate.customer_api_logs b
ON a.user_id = b.user_id AND a.updated_latest = b.updated_at;
