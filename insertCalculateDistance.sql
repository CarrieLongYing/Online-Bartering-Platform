USE cs6400_summer22_team040;

INSERT INTO Distance (postal_code_from, postal_code_to, distance)
SELECT 
	postal_code_from,
    postal_code_to,
    IFNULL(2 * ATAN2(SQRT(a), SQRT(1-a)) * 3958.75,0) as distance
FROM
	(SELECT 
		p.postal_code_from,
		p.postal_code_to,
		SIN(delta_lat/2) * SIN(delta_lat/2) + COS(lat1) * COS(lat2) * SIN(delta_long/2)*SIN(delta_long/2) AS a
	FROM 
		(SELECT
			p1.postal_code as postal_code_from,
			p2.postal_code as postal_code_to,
			p1.latitude AS lat1,
			p2.latitude AS lat2,
			(p1.latitude - p2.latitude) * PI()/180 AS delta_lat,
			(p1.longitude - p2.longitude) *PI()/180 AS delta_long
		FROM (SELECT 
					distinct pc.*
				FROM PostalCode AS pc
				INNER JOIN User
				ON pc.postal_code = User.postal_code) as p1
		CROSS JOIN (SELECT 
						distinct pc.*
					FROM PostalCode AS pc
					INNER JOIN User
					ON pc.postal_code = User.postal_code) as p2) p) dis;
							

