SELECT us_state, tupleElement(winner, 1) AS category, tupleElement(winner, 2) AS amount
FROM
(
    SELECT us_state, argMax(tuple(cat_id, amount), tuple(amount, row_id)) AS winner
    FROM hw2.transactions_baseline
    GROUP BY us_state
)
ORDER BY us_state
FORMAT CSVWithNames;
