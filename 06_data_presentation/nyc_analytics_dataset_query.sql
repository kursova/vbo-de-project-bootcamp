SELECT
        ft.tripid,
        ft.pickupdatetimeid,
        ft.dropoffdatetimeid,
        ft.pulocationid,
        ft.dolocationid,
        ft.ratecodeid,
        ft.paymenttypeid,
        ft.passengercount,
        ft.tripdistance,
        ft.fareamount,
        ft.tipamount,
        ft.tollsamount,
        ft.airportamount,
        ft.totalamount,
        ft.extra,
        ft.mtatax,
        ft.congestionsurcharge,
        ft.quality_issue,
        ft.year,
        ft.month,
        ft.day,

        -- Location dimensions
        pu.zone as pickup_zone,
        pu.borough as pickup_borough,
        pu.service_zone as pickup_service_zone,
        do.zone as dropoff_zone,
        do.borough as dropoff_borough,
        do.service_zone as dropoff_service_zone,

        -- Payment dimension
        p.paymenttype as payment_type,

        -- Rate code dimension
        r.ratedescription as rate_description,

        -- Time dimensions
        t."Date" as trip_date,
        t.year as trip_year,
        t.month as trip_month,
        t.dayofmonth as trip_day,
        hour(
         parse_datetime(CAST(t.timeid AS VARCHAR), 'yyyyMMddHHmm')
       ) AS trip_hour,
        EXTRACT(DOW FROM t."Date") as day_of_week,
        CASE EXTRACT(DOW FROM t."Date")
            WHEN 0 THEN 'Sunday'
            WHEN 1 THEN 'Monday'
            WHEN 2 THEN 'Tuesday'
            WHEN 3 THEN 'Wednesday'
            WHEN 4 THEN 'Thursday'
            WHEN 5 THEN 'Friday'
            WHEN 6 THEN 'Saturday'
        END as day_name,
        CASE t.month
            WHEN 1 THEN 'January'
            WHEN 2 THEN 'February'
            WHEN 3 THEN 'March'
            WHEN 4 THEN 'April'
            WHEN 5 THEN 'May'
            WHEN 6 THEN 'June'
            WHEN 7 THEN 'July'
            WHEN 8 THEN 'August'
            WHEN 9 THEN 'September'
            WHEN 10 THEN 'October'
            WHEN 11 THEN 'November'
            WHEN 12 THEN 'December'
        END as month_name,
        CASE
            WHEN t.month IN (1, 2, 3) THEN 1
            WHEN t.month IN (4, 5, 6) THEN 2
            WHEN t.month IN (7, 8, 9) THEN 3
            ELSE 4
        END as quarter,
        CASE
            WHEN EXTRACT(DOW FROM t."Date") IN (0, 6) THEN true
            ELSE false
        END as is_weekend,

        -- Calculated fields
        CASE
            WHEN ft.tripdistance <= 1 THEN '0-1 mile'
            WHEN ft.tripdistance <= 3 THEN '1-3 miles'
            WHEN ft.tripdistance <= 5 THEN '3-5 miles'
            WHEN ft.tripdistance <= 10 THEN '5-10 miles'
            ELSE '10+ miles'
        END as distance_category,

        CASE
            WHEN ft.fareamount <= 10 THEN '0-10'
            WHEN ft.fareamount <= 20 THEN '10-20'
            WHEN ft.fareamount <= 30 THEN '20-30'
            WHEN ft.fareamount <= 50 THEN '30-50'
            ELSE '50+'
        END as fare_category,

        CASE
            WHEN ft.tipamount = 0 THEN 'No Tip'
            WHEN ft.tipamount <= 2 THEN '0-2'
            WHEN ft.tipamount <= 5 THEN '2-5'
            WHEN ft.tipamount <= 10 THEN '5-10'
            ELSE '10+'
        END as tip_category,

        -- Trip duration in minutes
        (ft.dropoffdatetimeid - ft.pickupdatetimeid) / 100 as trip_duration_minutes,

        -- Tip percentage
        CASE
            WHEN ft.fareamount > 0 THEN (ft.tipamount / ft.fareamount) * 100
            ELSE 0
        END as tip_percentage

    FROM iceberg.silver.fact_trip ft
    LEFT JOIN iceberg.silver.dimlocation pu ON ft.pulocationid = pu.locationid
    LEFT JOIN iceberg.silver.dimlocation do ON ft.dolocationid = do.locationid
    LEFT JOIN iceberg.silver.dimpayment p ON ft.paymenttypeid = p.paymenttypeid
    LEFT JOIN iceberg.silver.dimratecode r ON ft.ratecodeid = r.ratecodeid
    LEFT JOIN iceberg.silver.dimtime t ON ft.pickupdatetimeid = t.timeid
    WHERE ft.quality_issue = 'good'