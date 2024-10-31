SELECT
	user_id, SUM(
		CASE
			WHEN created_at >= '2022-01-01' AND created_at < '2023-01-01'
			THEN reward
			ELSE 0
		END
	) AS total_reward_2022
FROM
	reports
WHERE
	user_id IN (
        SELECT
            user_id
		FROM
			reports
        WHERE
            created_at >= '2021-01-01' AND created_at < '2022-01-01'
    )
GROUP BY
	user_id;
