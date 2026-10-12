SELECT us_state, tupleElement(winner, 1) AS category, tupleElement(winner, 2) AS amount
FROM
(
    SELECT us_state, argMaxMerge(winner) AS winner
    FROM hw2.state_max
    GROUP BY us_state
)
ORDER BY us_state
FORMAT CSVWithNames;
