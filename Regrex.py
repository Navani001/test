WITH failure_types AS (
    SELECT DISTINCT failure_type
    FROM point_failures
),
output_types AS (
    SELECT DISTINCT output_type
    FROM point_failures
),
counts AS (
    SELECT
        failure_type,
        output_type,
        COUNT(*) AS failure_count
    FROM point_failures
    GROUP BY failure_type, output_type
)
SELECT
    f.failure_type,
    o.output_type,
    COALESCE(c.failure_count, 0) AS failure_count
FROM failure_types f
CROSS JOIN output_types o
LEFT JOIN counts c
    ON c.failure_type = f.failure_type
    AND c.output_type = o.output_type
ORDER BY f.failure_type, o.output_type;
