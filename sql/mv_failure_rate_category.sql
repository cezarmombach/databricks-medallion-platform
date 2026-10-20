-- Method: CREATE OR REPLACE MATERIALIZED VIEW (run in the SQL Editor, SQL warehouse)
-- Objective: Precompute the failure rate per category so dashboards read a stored result.
CREATE OR REPLACE MATERIALIZED VIEW workspace.gold.mv_failure_rate_category AS
SELECT
    c.category_name,                                                     -- category label from the dimension
    COUNT(*) AS total_transactions,                                      -- all transactions in the category
    SUM(CASE WHEN f.status = 'failed' THEN 1 ELSE 0 END) AS failed_transactions,  -- only failed ones
    ROUND(SUM(CASE WHEN f.status = 'failed' THEN 1 ELSE 0 END) / COUNT(*) * 100, 2) AS failure_rate_pct  -- BR-03
FROM workspace.gold.fact_transactions f
JOIN workspace.gold.dim_category c
    ON f.category_key = c.category_key
GROUP BY c.category_name;