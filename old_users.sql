SELECT
    users.id as external_id,
    users.first_name,
    users.last_name,
    users.email,
    users.status,
    users.user_type,
    sub.stripe_plan
FROM (
    SELECT
        id,
        first_name,
        last_name,
        email,
        status,
        user_type
    FROM macroplate.users
) users
INNER JOIN macroplate.subscriptions sub
ON users.id = sub.user_id;
