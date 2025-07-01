# Apache Superset Connection Setup Guide

This guide provides step-by-step instructions for connecting Apache Superset to the Trino database to access NYC taxi data.

## Prerequisites

- Apache Superset running and accessible
- Trino database running and accessible
- Network connectivity between Superset and Trino

## Step 1: Access Apache Superset

1. Open your web browser and navigate to the Superset URL
2. Log in with your credentials
3. Navigate to **Data → Databases**

## Step 2: Add New Database Connection

1. Click the **+ Database** button
2. Select **Trino** from the database type dropdown
3. Configure the connection with the following parameters:

### Connection Configuration

**Database Name:**
```
NYC Taxi Analytics
```

**SQLAlchemy URI:**
```
trino://trino-coordinator.trino.svc.cluster.local:8080/iceberg/silver
```

**Parameters:**
- **SQL Lab**: ✅ Enabled
- **Allow DML**: ❌ Disabled
- **Allow CTA**: ❌ Disabled
- **Allow CVAS**: ❌ Disabled
- **Cache Timeout**: 300 (5 minutes)

### Advanced Configuration

**Engine Parameters:**
```json
{
  "connect_args": {
    "catalog": "iceberg",
    "schema": "silver"
  }
}
```

## Step 3: Test Connection

1. Click **Test Connection** to verify the setup
2. If successful, you should see a green checkmark
3. Click **Save** to store the connection

## Step 4: Verify Tables

Run this test query in SQL Lab to verify access to all tables:

```sql
-- Test query to verify all tables are accessible
SELECT 
    'fact_trip' as table_name,
    COUNT(*) as row_count,
    MIN(year) as min_year,
    MAX(year) as max_year
FROM iceberg.silver.fact_trip
WHERE quality_issue = 'good'

UNION ALL

SELECT 
    'dimlocation' as table_name,
    COUNT(*) as row_count,
    NULL as min_year,
    NULL as max_year
FROM iceberg.silver.dimlocation

UNION ALL

SELECT 
    'dimpayment' as table_name,
    COUNT(*) as row_count,
    NULL as min_year,
    NULL as max_year
FROM iceberg.silver.dimpayment

UNION ALL

SELECT 
    'dimratecode' as table_name,
    COUNT(*) as row_count,
    NULL as min_year,
    NULL as max_year
FROM iceberg.silver.dimratecode

UNION ALL

SELECT 
    'dimtime' as table_name,
    COUNT(*) as row_count,
    MIN(year) as min_year,
    MAX(year) as max_year
FROM iceberg.silver.dimtime

ORDER BY table_name;
```

## Step 5: Create Dataset

1. Navigate to **Data → Datasets**
2. Click **+ Dataset**
3. Select the **NYC Taxi Analytics** database
4. Choose **Custom SQL** as the table type
5. Use one of the main analytics queries from [`dashboard_queries.sql`](./dashboard_queries.sql):

### Option 1: Simple Fact Table Query
```sql
SELECT 
    ft.*,
    pu.zone as pickup_zone,
    pu.borough as pickup_borough,
    do.zone as dropoff_zone,
    do.borough as dropoff_borough,
    p.paymenttype as payment_type,
    r.ratecode as rate_description,
    t."Date" as trip_date,
    t.hour as trip_hour,
    t.dayofmonth as trip_day,
    t.month as trip_month,
    t.year as trip_year
FROM iceberg.silver.fact_trip ft
LEFT JOIN iceberg.silver.dimlocation pu ON ft.pulocationid = pu.locationid
LEFT JOIN iceberg.silver.dimlocation do ON ft.dolocationid = do.locationid
LEFT JOIN iceberg.silver.dimpayment p ON ft.paymenttypeid = p.paymenttypeid
LEFT JOIN iceberg.silver.dimratecode r ON ft.ratecodeid = r.ratecodeid
LEFT JOIN iceberg.silver.dimtime t ON ft.pickupdatetimeid = t.timeid
WHERE ft.quality_issue = 'good'
```

### Option 2: Use Pre-built Queries
- See [`dashboard_queries.sql`](./dashboard_queries.sql) for all available queries
- Each query is designed for specific chart types (KPIs, line charts, bar charts, etc.)
- Copy the appropriate query based on the chart you want to create

6. Name the dataset: `NYC Taxi Analytics`
7. Click **Create**

## Troubleshooting

### Connection Issues

**Error: "Connection refused"**
- Verify Trino is running: `kubectl get pods -n trino`
- Check network connectivity
- Verify the connection string format

**Error: "Authentication failed"**
- Trino is configured without authentication
- Verify no username/password is required

**Error: "Schema not found"**
- Verify the schema exists: `SHOW SCHEMAS FROM iceberg;`
- Check table existence: `SHOW TABLES FROM iceberg.silver;`

### Performance Issues

**Slow Query Performance:**
- Add appropriate filters to limit data volume
- Use materialized views for complex aggregations
- Monitor query execution plans

**Memory Issues:**
- Reduce the number of rows returned
- Use sampling for large datasets
- Implement proper caching

## Security Considerations

1. **Network Security**: Ensure Superset and Trino are in the same network or properly secured
2. **Access Control**: Configure appropriate user permissions in Superset
3. **Data Privacy**: Be mindful of sensitive data in queries
4. **Audit Logging**: Enable query logging for compliance

## Best Practices

1. **Connection Pooling**: Configure appropriate connection pool settings
2. **Query Timeouts**: Set reasonable timeout values
3. **Caching**: Enable caching for frequently accessed data
4. **Monitoring**: Monitor connection health and performance
5. **Backup**: Keep connection configurations backed up

## Next Steps

After successful connection setup:

1. Create the main analytics dataset using queries from [`dashboard_queries.sql`](./dashboard_queries.sql)
2. Build individual charts as described in the [README](./README.md)
3. Create the dashboard layout following [`dashboard_configuration.md`](./dashboard_configuration.md)
4. Configure filters and cross-filtering
5. Test all functionality
6. Train users on dashboard usage

## Support

If you encounter issues:

1. Check the Superset logs: `kubectl logs -n superset <superset-pod>`
2. Check Trino logs: `kubectl logs -n trino <trino-pod>`
3. Verify network connectivity between services
4. Test queries directly in Trino CLI 