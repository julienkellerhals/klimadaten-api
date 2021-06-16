SELECT
	ratio.station
FROM (
	SELECT
		filtered.station
		,filtered.meas_name
		,(extract(year from CURRENT_DATE) - 1 - filtered.min_year) AS nr_years
		,filtered.cnt_years / (extract(year from CURRENT_DATE) - 1 - filtered.min_year) AS ratio
	FROM (
		SELECT
			min(yearly.meas_year) AS min_year
			,yearly.station
			,yearly.meas_name
			,COUNT(*) AS cnt_years
		FROM (
			SELECT
				extract(year from meas.meas_date) as meas_year
				,meas.station
				,meas.meas_name
			FROM core.measurements_t AS meas
			WHERE meas.meas_name IN (
				'rhh150mx',
				'hns000y0',
				'tre200y0',
				'rre150y0'
			)
			GROUP BY
				meas_year
				,meas.station
				,meas.meas_name
		) AS yearly
		GROUP BY 
			yearly.station
			,yearly.meas_name
		HAVING COUNT(*) >= 30
	) AS filtered
) AS ratio
WHERE ratio.ratio >= 0.9
GROUP BY ratio.station
HAVING COUNT(*) = 4
