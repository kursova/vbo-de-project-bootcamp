-- NYC Taxi Analytics Dashboard Queries
-- This file contains all SQL queries needed for the Apache Superset dashboard

-- ============================================================================
-- 1. KEY PERFORMANCE INDICATORS (Big Number Charts)
-- ============================================================================

-- Total Trips
SELECT COUNT(*) as total_trips
FROM iceberg.silver.fact_trip
WHERE quality_issue = 'good';

-- Total Revenue
SELECT SUM(totalamount) as total_revenue
FROM iceberg.silver.fact_trip
WHERE quality_issue = 'good';

-- Average Fare
SELECT AVG(fareamount) as avg_fare
FROM iceberg.silver.fact_trip
WHERE quality_issue = 'good';

-- Average Tip Percentage
SELECT AVG(CASE WHEN fareamount > 0 THEN (tipamount / fareamount) * 100 ELSE 0 END) as avg_tip_percentage
FROM iceberg.silver.fact_trip
WHERE quality_issue = 'good';

-- ============================================================================
-- 2. TEMPORAL ANALYSIS CHARTS
-- ============================================================================

-- Daily Trip Trends (Line Chart)
SELECT
    t."Date" as trip_date,
    COUNT(*) as trip_count,
    AVG(ft.fareamount) as avg_fare,
    SUM(ft.totalamount) as daily_revenue
FROM iceberg.silver.fact_trip ft
LEFT JOIN iceberg.silver.dimtime t ON ft.pickupdatetimeid = t.timeid
WHERE ft.quality_issue = 'good'
GROUP BY t."Date"
ORDER BY t."Date";

-- Hourly Trip Distribution (Bar Chart)
SELECT
    t.hour as trip_hour,
    COUNT(*) as trip_count,
    AVG(ft.fareamount) as avg_fare
FROM iceberg.silver.fact_trip ft
LEFT JOIN iceberg.silver.dimtime t ON ft.pickupdatetimeid = t.timeid
WHERE ft.quality_issue = 'good'
GROUP BY t.hour
ORDER BY t.hour;

-- Monthly Trends (Line Chart)
SELECT
    t.year as trip_year,
    t.month as trip_month,
    COUNT(*) as trip_count,
    SUM(ft.totalamount) as monthly_revenue,
    AVG(ft.fareamount) as avg_fare
FROM iceberg.silver.fact_trip ft
LEFT JOIN iceberg.silver.dimtime t ON ft.pickupdatetimeid = t.timeid
WHERE ft.quality_issue = 'good'
GROUP BY t.year, t.month
ORDER BY t.year, t.month;

-- ============================================================================
-- 3. GEOGRAPHIC ANALYSIS CHARTS
-- ============================================================================

-- Trips by Borough (Bar Chart)
SELECT
    pu.borough as pickup_borough,
    COUNT(*) as trip_count,
    SUM(ft.totalamount) as total_revenue,
    AVG(ft.fareamount) as avg_fare
FROM iceberg.silver.fact_trip ft
LEFT JOIN iceberg.silver.dimlocation pu ON ft.pulocationid = pu.locationid
WHERE ft.quality_issue = 'good' AND pu.borough IS NOT NULL
GROUP BY pu.borough
ORDER BY trip_count DESC;

-- Pickup vs Dropoff Analysis (Bar Chart)
SELECT
    'Pickup' as trip_type,
    pu.borough as borough,
    COUNT(*) as trip_count
FROM iceberg.silver.fact_trip ft
LEFT JOIN iceberg.silver.dimlocation pu ON ft.pulocationid = pu.locationid
WHERE ft.quality_issue = 'good' AND pu.borough IS NOT NULL
GROUP BY pu.borough

UNION ALL

SELECT
    'Dropoff' as trip_type,
    do.borough as borough,
    COUNT(*) as trip_count
FROM iceberg.silver.fact_trip ft
LEFT JOIN iceberg.silver.dimlocation do ON ft.dolocationid = do.locationid
WHERE ft.quality_issue = 'good' AND do.borough IS NOT NULL
GROUP BY do.borough;

-- Top Zones by Trip Volume (Bar Chart)
SELECT
    pu.zone as pickup_zone,
    COUNT(*) as trip_count,
    AVG(ft.fareamount) as avg_fare
FROM iceberg.silver.fact_trip ft
LEFT JOIN iceberg.silver.dimlocation pu ON ft.pulocationid = pu.locationid
WHERE ft.quality_issue = 'good' AND pu.zone IS NOT NULL
GROUP BY pu.zone
ORDER BY trip_count DESC
LIMIT 20;

-- ============================================================================
-- 4. FINANCIAL ANALYSIS CHARTS
-- ============================================================================

-- Revenue by Payment Type (Pie Chart)
SELECT
    p.paymenttype as payment_type,
    COUNT(*) as trip_count,
    SUM(ft.totalamount) as total_revenue,
    AVG(ft.fareamount) as avg_fare
FROM iceberg.silver.fact_trip ft
LEFT JOIN iceberg.silver.dimpayment p ON ft.paymenttypeid = p.paymenttypeid
WHERE ft.quality_issue = 'good' AND p.paymenttype IS NOT NULL
GROUP BY p.paymenttype
ORDER BY total_revenue DESC;

-- Fare Distribution (Histogram)
SELECT
    CASE
        WHEN ft.fareamount <= 10 THEN '0-10'
        WHEN ft.fareamount <= 20 THEN '10-20'
        WHEN ft.fareamount <= 30 THEN '20-30'
        WHEN ft.fareamount <= 50 THEN '30-50'
        ELSE '50+'
    END as fare_category,
    COUNT(*) as trip_count
FROM iceberg.silver.fact_trip ft
WHERE ft.quality_issue = 'good'
GROUP BY
    CASE
        WHEN ft.fareamount <= 10 THEN '0-10'
        WHEN ft.fareamount <= 20 THEN '10-20'
        WHEN ft.fareamount <= 30 THEN '20-30'
        WHEN ft.fareamount <= 50 THEN '30-50'
        ELSE '50+'
    END
ORDER BY
    CASE fare_category
        WHEN '0-10' THEN 1
        WHEN '10-20' THEN 2
        WHEN '20-30' THEN 3
        WHEN '30-50' THEN 4
        ELSE 5
    END;

-- Tip Analysis (Bar Chart)
SELECT
    CASE
        WHEN ft.tipamount = 0 THEN 'No Tip'
        WHEN ft.tipamount <= 2 THEN '0-2'
        WHEN ft.tipamount <= 5 THEN '2-5'
        WHEN ft.tipamount <= 10 THEN '5-10'
        ELSE '10+'
    END as tip_category,
    COUNT(*) as trip_count,
    AVG(CASE WHEN ft.fareamount > 0 THEN (ft.tipamount / ft.fareamount) * 100 ELSE 0 END) as avg_tip_percentage
FROM iceberg.silver.fact_trip ft
WHERE ft.quality_issue = 'good' AND ft.tipamount > 0
GROUP BY
    CASE
        WHEN ft.tipamount = 0 THEN 'No Tip'
        WHEN ft.tipamount <= 2 THEN '0-2'
        WHEN ft.tipamount <= 5 THEN '2-5'
        WHEN ft.tipamount <= 10 THEN '5-10'
        ELSE '10+'
    END
ORDER BY
    CASE tip_category
        WHEN 'No Tip' THEN 1
        WHEN '0-2' THEN 2
        WHEN '2-5' THEN 3
        WHEN '5-10' THEN 4
        ELSE 5
    END;

-- ============================================================================
-- 5. OPERATIONAL ANALYSIS CHARTS
-- ============================================================================

-- Trip Distance Analysis (Bar Chart)
SELECT
    CASE
        WHEN ft.tripdistance <= 1 THEN '0-1 mile'
        WHEN ft.tripdistance <= 3 THEN '1-3 miles'
        WHEN ft.tripdistance <= 5 THEN '3-5 miles'
        WHEN ft.tripdistance <= 10 THEN '5-10 miles'
        ELSE '10+ miles'
    END as distance_category,
    COUNT(*) as trip_count,
    AVG(ft.fareamount) as avg_fare,
    AVG((ft.dropoffdatetimeid - ft.pickupdatetimeid) / 100) as avg_duration_minutes
FROM iceberg.silver.fact_trip ft
WHERE ft.quality_issue = 'good'
GROUP BY
    CASE
        WHEN ft.tripdistance <= 1 THEN '0-1 mile'
        WHEN ft.tripdistance <= 3 THEN '1-3 miles'
        WHEN ft.tripdistance <= 5 THEN '3-5 miles'
        WHEN ft.tripdistance <= 10 THEN '5-10 miles'
        ELSE '10+ miles'
    END
ORDER BY
    CASE distance_category
        WHEN '0-1 mile' THEN 1
        WHEN '1-3 miles' THEN 2
        WHEN '3-5 miles' THEN 3
        WHEN '5-10 miles' THEN 4
        ELSE 5
    END;

-- Passenger Count Distribution (Pie Chart)
SELECT
    ft.passengercount,
    COUNT(*) as trip_count,
    AVG(ft.fareamount) as avg_fare
FROM iceberg.silver.fact_trip ft
WHERE ft.quality_issue = 'good'
GROUP BY ft.passengercount
ORDER BY ft.passengercount;

-- Rate Code Analysis (Bar Chart)
SELECT
    r.ratecode as rate_description,
    COUNT(*) as trip_count,
    SUM(ft.totalamount) as total_revenue,
    AVG(ft.fareamount) as avg_fare
FROM iceberg.silver.fact_trip ft
LEFT JOIN iceberg.silver.dimratecode r ON ft.ratecodeid = r.ratecodeid
WHERE ft.quality_issue = 'good' AND r.ratecode IS NOT NULL
GROUP BY r.ratecode
ORDER BY total_revenue DESC;

-- ============================================================================
-- 6. ADVANCED ANALYTICS CHARTS
-- ============================================================================

-- Trip Duration vs Fare (Scatter Plot)
SELECT
    (ft.dropoffdatetimeid - ft.pickupdatetimeid) / 100 as trip_duration_minutes,
    ft.fareamount,
    pu.borough as pickup_borough,
    CASE
        WHEN ft.tripdistance <= 1 THEN '0-1 mile'
        WHEN ft.tripdistance <= 3 THEN '1-3 miles'
        WHEN ft.tripdistance <= 5 THEN '3-5 miles'
        WHEN ft.tripdistance <= 10 THEN '5-10 miles'
        ELSE '10+ miles'
    END as distance_category
FROM iceberg.silver.fact_trip ft
LEFT JOIN iceberg.silver.dimlocation pu ON ft.pulocationid = pu.locationid
WHERE ft.quality_issue = 'good'
  AND (ft.dropoffdatetimeid - ft.pickupdatetimeid) / 100 > 0
  AND (ft.dropoffdatetimeid - ft.pickupdatetimeid) / 100 < 120
  AND ft.fareamount > 0
  AND ft.fareamount < 100;

-- Heatmap: Trips by Hour and Day (Heatmap)
SELECT
    t.hour as trip_hour,
    CASE EXTRACT(DOW FROM t."Date")
        WHEN 0 THEN 'Sunday'
        WHEN 1 THEN 'Monday'
        WHEN 2 THEN 'Tuesday'
        WHEN 3 THEN 'Wednesday'
        WHEN 4 THEN 'Thursday'
        WHEN 5 THEN 'Friday'
        WHEN 6 THEN 'Saturday'
    END as day_name,
    COUNT(*) as trip_count
FROM iceberg.silver.fact_trip ft
LEFT JOIN iceberg.silver.dimtime t ON ft.pickupdatetimeid = t.timeid
WHERE ft.quality_issue = 'good'
GROUP BY t.hour,
    CASE EXTRACT(DOW FROM t."Date")
        WHEN 0 THEN 'Sunday'
        WHEN 1 THEN 'Monday'
        WHEN 2 THEN 'Tuesday'
        WHEN 3 THEN 'Wednesday'
        WHEN 4 THEN 'Thursday'
        WHEN 5 THEN 'Friday'
        WHEN 6 THEN 'Saturday'
    END
ORDER BY
    CASE day_name
        WHEN 'Monday' THEN 1
        WHEN 'Tuesday' THEN 2
        WHEN 'Wednesday' THEN 3
        WHEN 'Thursday' THEN 4
        WHEN 'Friday' THEN 5
        WHEN 'Saturday' THEN 6
        WHEN 'Sunday' THEN 7
    END,
    t.hour;

-- Year-over-Year Comparison (Line Chart)
SELECT
    t.month as trip_month,
    t.year as trip_year,
    COUNT(*) as trip_count,
    SUM(ft.totalamount) as revenue
FROM iceberg.silver.fact_trip ft
LEFT JOIN iceberg.silver.dimtime t ON ft.pickupdatetimeid = t.timeid
WHERE ft.quality_issue = 'good'
GROUP BY t.month, t.year
ORDER BY t.month, t.year;

-- ============================================================================
-- 7. SEASONAL AND PATTERN ANALYSIS
-- ============================================================================

-- Seasonal Analysis
SELECT
    CASE
        WHEN t.month IN (12, 1, 2) THEN 'Winter'
        WHEN t.month IN (3, 4, 5) THEN 'Spring'
        WHEN t.month IN (6, 7, 8) THEN 'Summer'
        ELSE 'Fall'
    END as season,
    COUNT(*) as trip_count,
    AVG(ft.fareamount) as avg_fare,
    SUM(ft.totalamount) as total_revenue
FROM iceberg.silver.fact_trip ft
LEFT JOIN iceberg.silver.dimtime t ON ft.pickupdatetimeid = t.timeid
WHERE ft.quality_issue = 'good'
GROUP BY
    CASE
        WHEN t.month IN (12, 1, 2) THEN 'Winter'
        WHEN t.month IN (3, 4, 5) THEN 'Spring'
        WHEN t.month IN (6, 7, 8) THEN 'Summer'
        ELSE 'Fall'
    END
ORDER BY
    CASE season
        WHEN 'Winter' THEN 1
        WHEN 'Spring' THEN 2
        WHEN 'Summer' THEN 3
        ELSE 4
    END;

-- Peak Hour Analysis
SELECT
    CASE EXTRACT(DOW FROM t."Date")
        WHEN 0 THEN 'Sunday'
        WHEN 1 THEN 'Monday'
        WHEN 2 THEN 'Tuesday'
        WHEN 3 THEN 'Wednesday'
        WHEN 4 THEN 'Thursday'
        WHEN 5 THEN 'Friday'
        WHEN 6 THEN 'Saturday'
    END as day_name,
    t.hour as trip_hour,
    COUNT(*) as trip_count,
    AVG(ft.fareamount) as avg_fare
FROM iceberg.silver.fact_trip ft
LEFT JOIN iceberg.silver.dimtime t ON ft.pickupdatetimeid = t.timeid
WHERE ft.quality_issue = 'good'
GROUP BY
    CASE EXTRACT(DOW FROM t."Date")
        WHEN 0 THEN 'Sunday'
        WHEN 1 THEN 'Monday'
        WHEN 2 THEN 'Tuesday'
        WHEN 3 THEN 'Wednesday'
        WHEN 4 THEN 'Thursday'
        WHEN 5 THEN 'Friday'
        WHEN 6 THEN 'Saturday'
    END,
    t.hour
ORDER BY
    CASE day_name
        WHEN 'Monday' THEN 1
        WHEN 'Tuesday' THEN 2
        WHEN 'Wednesday' THEN 3
        WHEN 'Thursday' THEN 4
        WHEN 'Friday' THEN 5
        WHEN 'Saturday' THEN 6
        WHEN 'Sunday' THEN 7
    END,
    t.hour;

-- Revenue by Hour and Borough
SELECT
    pu.borough as pickup_borough,
    t.hour as trip_hour,
    COUNT(*) as trip_count,
    SUM(ft.totalamount) as total_revenue,
    AVG(ft.totalamount) as avg_revenue_per_trip
FROM iceberg.silver.fact_trip ft
LEFT JOIN iceberg.silver.dimlocation pu ON ft.pulocationid = pu.locationid
LEFT JOIN iceberg.silver.dimtime t ON ft.pickupdatetimeid = t.timeid
WHERE ft.quality_issue = 'good' AND pu.borough IS NOT NULL
GROUP BY pu.borough, t.hour
ORDER BY pu.borough, t.hour;

-- ============================================================================
-- 8. PERFORMANCE OPTIMIZATION QUERIES
-- ============================================================================

-- Daily Aggregations (Materialized View)
CREATE MATERIALIZED VIEW iceberg.silver.daily_aggregations AS
SELECT
    t."Date" as trip_date,
    COUNT(*) as trip_count,
    SUM(ft.totalamount) as daily_revenue,
    AVG(ft.fareamount) as avg_fare,
    AVG(CASE WHEN ft.fareamount > 0 THEN (ft.tipamount / ft.fareamount) * 100 ELSE 0 END) as avg_tip_percentage
FROM iceberg.silver.fact_trip ft
LEFT JOIN iceberg.silver.dimtime t ON ft.pickupdatetimeid = t.timeid
WHERE ft.quality_issue = 'good'
GROUP BY t."Date";

-- Borough Aggregations (Materialized View)
CREATE MATERIALIZED VIEW iceberg.silver.borough_aggregations AS
SELECT
    pu.borough as pickup_borough,
    COUNT(*) as trip_count,
    SUM(ft.totalamount) as total_revenue,
    AVG(ft.fareamount) as avg_fare
FROM iceberg.silver.fact_trip ft
LEFT JOIN iceberg.silver.dimlocation pu ON ft.pulocationid = pu.locationid
WHERE ft.quality_issue = 'good' AND pu.borough IS NOT NULL
GROUP BY pu.borough;

-- ============================================================================
-- 9. DATA QUALITY AND VALIDATION QUERIES
-- ============================================================================

-- Data Quality Check
SELECT
    'Total Records' as metric,
    COUNT(*) as value
FROM iceberg.silver.fact_trip

UNION ALL

SELECT
    'Good Quality Records' as metric,
    COUNT(*) as value
FROM iceberg.silver.fact_trip
WHERE quality_issue = 'good'

UNION ALL

SELECT
    'Corrupted Records' as metric,
    COUNT(*) as value
FROM iceberg.silver.fact_trip
WHERE quality_issue = 'corrupted'

UNION ALL

SELECT
    'Data Completeness %' as metric,
    ROUND((COUNT(CASE WHEN quality_issue = 'good' THEN 1 END) * 100.0 / COUNT(*)), 2) as value
FROM iceberg.silver.fact_trip;

-- Year Distribution
SELECT
    t.year,
    COUNT(*) as trip_count,
    ROUND((COUNT(*) * 100.0 / SUM(COUNT(*)) OVER ()), 2) as percentage
FROM iceberg.silver.fact_trip ft
LEFT JOIN iceberg.silver.dimtime t ON ft.pickupdatetimeid = t.timeid
WHERE ft.quality_issue = 'good'
GROUP BY t.year
ORDER BY t.year;

-- ============================================================================
-- 10. BUSINESS INTELLIGENCE QUERIES
-- ============================================================================

-- Revenue Trends by Year and Month
SELECT
    t.year,
    t.month,
    COUNT(*) as trip_count,
    SUM(ft.totalamount) as revenue,
    AVG(ft.fareamount) as avg_fare,
    AVG(ft.tripdistance) as avg_distance
FROM iceberg.silver.fact_trip ft
LEFT JOIN iceberg.silver.dimtime t ON ft.pickupdatetimeid = t.timeid
WHERE ft.quality_issue = 'good'
GROUP BY t.year, t.month
ORDER BY t.year, t.month;

-- Top Revenue Generating Boroughs
SELECT
    pu.borough,
    COUNT(*) as trip_count,
    SUM(ft.totalamount) as total_revenue,
    AVG(ft.totalamount) as avg_revenue_per_trip,
    ROUND((SUM(ft.totalamount) * 100.0 / SUM(SUM(ft.totalamount)) OVER ()), 2) as revenue_percentage
FROM iceberg.silver.fact_trip ft
LEFT JOIN iceberg.silver.dimlocation pu ON ft.pulocationid = pu.locationid
WHERE ft.quality_issue = 'good' AND pu.borough IS NOT NULL
GROUP BY pu.borough
ORDER BY total_revenue DESC;

-- Payment Method Analysis
SELECT
    p.paymenttype,
    COUNT(*) as trip_count,
    SUM(ft.totalamount) as total_revenue,
    AVG(ft.totalamount) as avg_revenue_per_trip,
    AVG(CASE WHEN ft.fareamount > 0 THEN (ft.tipamount / ft.fareamount) * 100 ELSE 0 END) as avg_tip_percentage
FROM iceberg.silver.fact_trip ft
LEFT JOIN iceberg.silver.dimpayment p ON ft.paymenttypeid = p.paymenttypeid
WHERE ft.quality_issue = 'good' AND p.paymenttype IS NOT NULL
GROUP BY p.paymenttype
ORDER BY total_revenue DESC;