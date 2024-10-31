SELECT
    reports.barcode,
    reports.price,
    pos.title
FROM
    reports
JOIN
    pos ON reports.pos_id = pos.id
GROUP BY
    reports.barcode,
    reports.price,
    pos.title
HAVING
    COUNT(pos.title) > 1;
