# Dashboard Configuration Guide

This guide provides detailed instructions for configuring the NYC Taxi Analytics dashboard in Apache Superset, including layout, filters, and interactivity settings.

## Dashboard Overview

The NYC Taxi Analytics dashboard consists of 12 main charts organized in a 4-row layout, providing comprehensive insights into taxi operations, financial performance, and geographic patterns.

## Dashboard Layout Configuration

### Row 1: Key Performance Indicators (KPIs)

**Layout:** 4 columns, equal width

#### Chart 1: Total Trips (Gauge Chart)
- **Chart Type**: Big Number
- **Dataset**: NYC Taxi Analytics
- **Metric**: `COUNT(tripid)`
- **Subheader**: "Total trips in selected period"
- **Color**: Blue (#1f77b4)
- **Format**: Number with comma separator

#### Chart 2: Total Revenue (Gauge Chart)
- **Chart Type**: Big Number
- **Dataset**: NYC Taxi Analytics
- **Metric**: `SUM(totalamount)`
- **Subheader**: "Total revenue in selected period"
- **Color**: Green (#2ca02c)
- **Format**: Currency ($)

#### Chart 3: Average Fare (Gauge Chart)
- **Chart Type**: Big Number
- **Dataset**: NYC Taxi Analytics
- **Metric**: `AVG(fareamount)`
- **Subheader**: "Average fare per trip"
- **Color**: Orange (#ff7f0e)
- **Format**: Currency ($)

#### Chart 4: Average Tip % (Big Number)
- **Chart Type**: Big Number
- **Dataset**: NYC Taxi Analytics
- **Metric**: `AVG(tip_percentage)`
- **Subheader**: "Average tip percentage"
- **Color**: Purple (#9467bd)
- **Format**: Percentage (%)

### Row 2: Primary Analysis Charts

**Layout:** 3 columns, equal width

#### Chart 5: Daily Trip Trends (Line Chart)
- **Chart Type**: Line Chart
- **Dataset**: NYC Taxi Analytics
- **X-Axis**: `trip_date`
- **Y-Axis**: `trip_count`
- **Color**: None
- **Title**: "Daily Trip Trends"
- **X-Axis Label**: "Date"
- **Y-Axis Label**: "Number of Trips"
- **Show Legend**: No
- **Smooth Line**: Yes

#### Chart 6: Trips by Borough (Bar Chart)
- **Chart Type**: Bar Chart
- **Dataset**: NYC Taxi Analytics
- **X-Axis**: `pickup_borough`
- **Y-Axis**: `trip_count`
- **Color**: `pickup_borough`
- **Title**: "Trips by Borough"
- **X-Axis Label**: "Borough"
- **Y-Axis Label**: "Number of Trips"
- **Show Legend**: Yes
- **Sort**: Descending by trip_count

#### Chart 7: Revenue by Payment Type (Pie Chart)
- **Chart Type**: Pie Chart
- **Dataset**: NYC Taxi Analytics
- **Group By**: `payment_type`
- **Metric**: `SUM(totalamount)`
- **Title**: "Revenue by Payment Type"
- **Show Legend**: Yes
- **Show Labels**: Yes
- **Color Scheme**: Default

### Row 3: Secondary Analysis Charts

**Layout:** 3 columns, equal width

#### Chart 8: Hourly Trip Distribution (Bar Chart)
- **Chart Type**: Bar Chart
- **Dataset**: NYC Taxi Analytics
- **X-Axis**: `trip_hour`
- **Y-Axis**: `trip_count`
- **Color**: None
- **Title**: "Hourly Trip Distribution"
- **X-Axis Label**: "Hour of Day"
- **Y-Axis Label**: "Number of Trips"
- **Show Legend**: No
- **Sort**: Ascending by trip_hour

#### Chart 9: Trip Distance Analysis (Bar Chart)
- **Chart Type**: Bar Chart
- **Dataset**: NYC Taxi Analytics
- **X-Axis**: `distance_category`
- **Y-Axis**: `trip_count`
- **Color**: `distance_category`
- **Title**: "Trips by Distance Category"
- **X-Axis Label**: "Distance Category"
- **Y-Axis Label**: "Number of Trips"
- **Show Legend**: Yes
- **Sort**: Custom order (0-1 mile, 1-3 miles, etc.)

#### Chart 10: Tip Analysis (Bar Chart)
- **Chart Type**: Bar Chart
- **Dataset**: NYC Taxi Analytics
- **X-Axis**: `tip_category`
- **Y-Axis**: `trip_count`
- **Color**: `tip_category`
- **Title**: "Trips by Tip Category"
- **X-Axis Label**: "Tip Category"
- **Y-Axis Label**: "Number of Trips"
- **Show Legend**: Yes
- **Sort**: Custom order (No Tip, 0-2, 2-5, 5-10, 10+)

### Row 4: Advanced Analysis Charts

**Layout:** 3 columns, equal width

#### Chart 11: Trip Duration vs Fare (Scatter Plot)
- **Chart Type**: Scatter Plot
- **Dataset**: NYC Taxi Analytics
- **X-Axis**: `trip_duration_minutes`
- **Y-Axis**: `fareamount`
- **Color**: `pickup_borough`
- **Size**: `tripdistance`
- **Title**: "Trip Duration vs Fare"
- **X-Axis Label**: "Duration (minutes)"
- **Y-Axis Label**: "Fare Amount ($)"
- **Show Legend**: Yes
- **Opacity**: 0.7

#### Chart 12: Heatmap: Trips by Hour and Day (Heatmap)
- **Chart Type**: Heatmap
- **Dataset**: NYC Taxi Analytics
- **X-Axis**: `trip_hour`
- **Y-Axis**: `day_name`
- **Metric**: `COUNT(tripid)`
- **Title**: "Trips by Hour and Day"
- **Color Scheme**: Blues
- **Show Legend**: Yes
- **Sort X-Axis**: Ascending by trip_hour
- **Sort Y-Axis**: Custom order (Monday to Sunday)

#### Chart 13: Year-over-Year Comparison (Line Chart)
- **Chart Type**: Line Chart
- **Dataset**: NYC Taxi Analytics
- **X-Axis**: `trip_month`
- **Y-Axis**: `trip_count`
- **Color**: `trip_year`
- **Title**: "Year-over-Year Trip Comparison"
- **X-Axis Label**: "Month"
- **Y-Axis Label**: "Number of Trips"
- **Show Legend**: Yes
- **Smooth Line**: Yes

## Filter Configuration

### Global Filters

Add these filters to the dashboard for interactive filtering:

#### 1. Year Filter
- **Type**: Filter Box
- **Column**: `trip_year`
- **Default Value**: All years
- **Multiple Selection**: Yes
- **Search**: Yes
- **Title**: "Year"

#### 2. Month Filter
- **Type**: Filter Box
- **Column**: `trip_month`
- **Default Value**: All months
- **Multiple Selection**: Yes
- **Search**: Yes
- **Title**: "Month"

#### 3. Borough Filter
- **Type**: Filter Box
- **Column**: `pickup_borough`
- **Default Value**: All boroughs
- **Multiple Selection**: Yes
- **Search**: Yes
- **Title**: "Borough"

#### 4. Payment Type Filter
- **Type**: Filter Box
- **Column**: `payment_type`
- **Default Value**: All payment types
- **Multiple Selection**: Yes
- **Search**: Yes
- **Title**: "Payment Type"

#### 5. Date Range Filter
- **Type**: Date Range
- **Column**: `trip_date`
- **Default Value**: Last 30 days
- **Title**: "Date Range"

#### 6. Distance Category Filter
- **Type**: Filter Box
- **Column**: `distance_category`
- **Default Value**: All categories
- **Multiple Selection**: Yes
- **Search**: Yes
- **Title**: "Distance Category"

## Interactivity Configuration

### Cross-Filtering

Enable cross-filtering for enhanced interactivity:

1. **Chart-to-Chart Filtering**: When a user clicks on a data point in one chart, it filters all other charts
2. **Filter-to-Chart Filtering**: When a user selects a filter value, it updates all charts
3. **Drill-Down Capability**: Allow users to drill down from borough to zone level

### Chart Interactions

#### Bar Charts
- **Click to Filter**: Enable
- **Hover Tooltip**: Show detailed information
- **Selection Mode**: Single or multiple

#### Line Charts
- **Click to Filter**: Enable
- **Hover Tooltip**: Show exact values
- **Zoom**: Enable for detailed analysis

#### Pie Charts
- **Click to Filter**: Enable
- **Hover Tooltip**: Show percentage and value
- **Explode Slice**: On hover

#### Scatter Plots
- **Click to Filter**: Enable
- **Hover Tooltip**: Show all dimensions
- **Zoom**: Enable for detailed analysis

#### Heatmaps
- **Click to Filter**: Enable
- **Hover Tooltip**: Show exact values
- **Color Scale**: Adjustable

## Dashboard Settings

### General Settings

- **Dashboard Title**: "NYC Taxi Analytics Dashboard"
- **Description**: "Comprehensive analysis of NYC Yellow Taxi trip data from 2022-2024"
- **CSS**: Custom styling for NYC taxi theme (yellow and black colors)
- **Refresh Interval**: 5 minutes
- **Auto-refresh**: Enabled

### Performance Settings

- **Cache Timeout**: 300 seconds (5 minutes)
- **Query Timeout**: 60 seconds
- **Max Rows**: 100,000
- **Row Limit**: 10,000 per chart

### Export Settings

- **Enable Export**: Yes
- **Export Formats**: CSV, Excel, PDF
- **Export Charts**: All charts
- **Export Data**: Raw data and aggregated data

## Custom CSS Styling

Add this custom CSS to the dashboard for NYC taxi branding:

```css
/* NYC Taxi Theme */
.dashboard-header {
    background: linear-gradient(135deg, #ffd700 0%, #ffed4e 100%);
    color: #000;
    border-bottom: 3px solid #000;
}

.filter-container {
    background-color: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 5px;
    padding: 10px;
    margin-bottom: 15px;
}

.chart-container {
    border: 1px solid #e9ecef;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    background: white;
}

.big-number-container {
    background: linear-gradient(135deg, #ffd700 0%, #ffed4e 100%);
    border-radius: 10px;
    padding: 20px;
    text-align: center;
    color: #000;
    font-weight: bold;
}

/* Chart colors */
.chart-color-1 { color: #ffd700; } /* Yellow */
.chart-color-2 { color: #000000; } /* Black */
.chart-color-3 { color: #ff6b35; } /* Orange */
.chart-color-4 { color: #2c3e50; } /* Dark Blue */
```

## Dashboard Permissions

### User Roles

1. **Viewer**: Can view dashboard and export data
2. **Editor**: Can modify charts and filters
3. **Admin**: Full access to dashboard configuration

### Access Control

- **Public Access**: Read-only for all authenticated users
- **Edit Access**: Restricted to dashboard owners and editors
- **Admin Access**: Restricted to administrators

## Maintenance and Updates

### Regular Tasks

1. **Data Refresh**: Monitor data pipeline for new data
2. **Performance Monitoring**: Check query execution times
3. **User Feedback**: Collect and implement user suggestions
4. **Chart Updates**: Update charts based on new requirements

### Backup and Recovery

1. **Dashboard Export**: Export dashboard configuration regularly
2. **Chart Backups**: Save individual chart configurations
3. **Version Control**: Track changes to dashboard configuration

## Troubleshooting

### Common Issues

1. **Slow Loading**: Check query performance and add filters
2. **Missing Data**: Verify data pipeline and table access
3. **Filter Issues**: Check filter column names and data types
4. **Chart Errors**: Verify SQL syntax and column references

### Performance Optimization

1. **Query Optimization**: Use materialized views for complex queries
2. **Caching**: Enable appropriate cache settings
3. **Filtering**: Add filters to reduce data volume
4. **Sampling**: Use data sampling for large datasets

## Conclusion

This comprehensive dashboard configuration provides a powerful analytics platform for NYC taxi data analysis. The combination of KPIs, trend analysis, geographic insights, and advanced analytics enables data-driven decision making for taxi operations and city planning. 