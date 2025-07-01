# Manual Guide: NYC Taxi Analytics Dashboard Setup

This guide provides step-by-step instructions to manually create and configure your NYC Taxi Analytics dashboard in Apache Superset.

**Author:** Erkan Sirin
**Date:** 2025-06-22

---

### **Prerequisites**

Before you begin, ensure you have successfully run the automation script:
```bash
python 06_data_presentation/setup_dashboard.py
```
This script performs the following critical actions:
1.  **Cleans up** any old dashboards, charts, and datasets related to this project.
2.  **Creates a new dataset** named `NYC Taxi Analytics`.
3.  **Creates 8 new charts** based on the new dataset.

You must run this script first to ensure all assets are ready for dashboard assembly.

---

### **Step 1: Create a New Dashboard**

1.  Navigate to your Superset instance (e.g., `http://localhost:30088`).
2.  Click on the **Dashboards** tab in the top navigation bar.
3.  Click the **+ DASHBOARD** button in the top right corner.
4.  In the "Title" field, enter: `NYC Taxi Analytics Dashboard`.
5.  The "URL slug" will auto-populate as `nyc-taxi-analytics-dashboard`. You can leave this as is.
6.  Click **CREATE**.

You will be taken to your new, empty dashboard.

---

### **Step 2: Add Charts to the Dashboard**

1.  From your new dashboard page, click the **Edit dashboard** button (or the pencil icon ✎) in the top right.
2.  You will see a right-hand pane. Click the **Charts** tab.
3.  You should see a list of all available charts, including the 8 new charts created by the script (e.g., "Total Trips", "Total Revenue", etc.).
4.  **Drag and drop** each of the 8 charts from the right-hand pane onto the main dashboard canvas. Don't worry about the exact placement yet.

---

### **Step 3: Arrange the Dashboard Layout**

Now, arrange the charts you just added. Resize and move them to match the intended layout.

**Recommended Layout:**

*   **Row 1 (KPIs):**
    *   `Total Trips` (width: 3, height: 2)
    *   `Total Revenue` (width: 3, height: 2)
*   **Row 2:**
    *   `Daily Trip Trends` (width: 6, height: 4)
*   **Row 3:**
    *   `Trips by Borough` (width: 6, height: 4)
*   **Row 4 (Distributions):**
    *   `Revenue by Payment Type` (width: 4, height: 4)
    *   `Distance Distribution` (width: 4, height: 4)
    *   `Fare Amount Distribution` (width: 4, height: 4)
*   **Row 5:**
    *   `Hourly Trip Patterns` (width: 12, height: 4)

---

### **Step 4: Add Custom Styling (CSS)**

To give your dashboard a professional, themed look, you can add custom CSS.

1.  While in "Edit dashboard" mode, click the **three-dot menu (...)** in the top right.
2.  Select **Edit CSS**.
3.  A code editor will appear. **Copy and paste** the following CSS code into the editor:
    ```css
    .dashboard-header {
        background: linear-gradient(135deg, #ffd700 0%, #ffed4e 100%);
        color: #000;
        border-bottom: 3px solid #000;
        padding: 15px;
        font-weight: bold;
    }

    .chart-header {
        font-weight: bold;
    }

    .chart-container {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    ```
4.  Click **Save**.

---

### **Step 5: (Optional) Convert KPIs to Gauge Charts**

For a more visually appealing dashboard, you can change the "Total Trips" and "Total Revenue" big number charts into gauge charts.

1.  From the dashboard view, click the **three-dot menu (...)** on the "Total Trips" chart and select **Edit chart**.
2.  In the chart editor, under the "Visualization" section, click the `Big Number` icon and select the **Gauge Chart** from the list.
3.  On the **Customize** tab, set the following:
    *   **Min Value:** `0`
    *   **Max Value:** `10000000` (or a number relevant to your data)
4.  Click **Save**.
5.  Repeat the same process for the "Total Revenue" chart, using a **Max Value** like `100000000`.

---

### **Step 6: Save Your Dashboard**

1.  Once you are happy with the layout and styling, click the **Save** button in the top right corner to save all your changes.
2.  Exit the edit mode by clicking the **X** or "Exit edit mode".

**Congratulations! Your NYC Taxi Analytics Dashboard is now complete and ready for use.**

## Prerequisites

- Apache Superset running and accessible
- Trino database connection configured
- Access to Superset web interface

## Step 1: Connect to Superset

1. Open your web browser and navigate to your Superset URL
2. Log in with your credentials
3. Verify you have admin or editor permissions

## Step 2: Add Database Connection

1. Navigate to **Data → Databases → + Database Connection**
2. Select **Trino** from the database type dropdown
3. Configure the connection:

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

4. Click **Test Connection** to verify
5. Click **Save** to store the connection

## Step 3: Test Database Connection

1. Go to **SQL Lab**
2. Select the **NYC Taxi Analytics** database
3. Run this test query:

```sql
SELECT 
    'fact_trip' as table_name,
    COUNT(*) as row_count
FROM iceberg.silver.fact_trip
WHERE quality_issue = 'good'
UNION ALL
SELECT 
    'dimlocation' as table_name,
    COUNT(*) as row_count
FROM iceberg.silver.dimlocation
UNION ALL
SELECT 
    'dimpayment' as table_name,
    COUNT(*) as row_count
FROM iceberg.silver.dimpayment
UNION ALL
SELECT 
    'dimratecode' as table_name,
    COUNT(*) as row_count
FROM iceberg.silver.dimratecode
UNION ALL
SELECT 
    'dimtime' as table_name,
    COUNT(*) as row_count
FROM iceberg.silver.dimtime
ORDER BY table_name;
```

## Step 4: Create Main Analytics Dataset

1. Navigate to **Data → Datasets**
2. Click **+ Dataset**
3. Select the **NYC Taxi Analytics** database
4. Choose **Custom SQL** as the table type
5. Paste the main analytics query from `dashboard_queries.sql`
6. Name the dataset: `NYC Taxi Analytics`
7. Click **Create**

## Step 5: Create Individual Charts

### Chart 1: Total Trips (Big Number)

1. Go to **Charts → + Chart**
2. Select the **NYC Taxi Analytics** dataset
3. Choose **Big Number** as chart type
4. Configure:
   - **Metric**: `COUNT(tripid)`
   - **Subheader**: "Total trips in selected period"
   - **Color**: Blue (#1f77b4)
5. Click **Create Chart**

### Chart 2: Total Revenue (Big Number)

1. Create new chart
2. Choose **Big Number** chart type
3. Configure:
   - **Metric**: `SUM(totalamount)`
   - **Subheader**: "Total revenue in selected period"
   - **Color**: Green (#2ca02c)
   - **Format**: Currency ($)
4. Click **Create Chart**

### Chart 3: Daily Trip Trends (Line Chart)

1. Create new chart
2. Choose **Line Chart** chart type
3. Configure:
   - **X-Axis**: `trip_date`
   - **Y-Axis**: `COUNT(tripid)`
   - **Title**: "Daily Trip Trends"
4. Click **Create Chart**

### Chart 4: Trips by Borough (Bar Chart)

1. Create new chart
2. Choose **Bar Chart** chart type
3. Configure:
   - **X-Axis**: `pickup_borough`
   - **Y-Axis**: `COUNT(tripid)`
   - **Title**: "Trips by Borough"
   - **Sort**: Descending by trip_count
4. Click **Create Chart**

### Chart 5: Revenue by Payment Type (Pie Chart)

1. Create new chart
2. Choose **Pie Chart** chart type
3. Configure:
   - **Group By**: `payment_type`
   - **Metric**: `SUM(totalamount)`
   - **Title**: "Revenue by Payment Type"
4. Click **Create Chart**

### Chart 6: Hourly Trip Distribution (Bar Chart)

1. Create new chart
2. Choose **Bar Chart** chart type
3. Configure:
   - **X-Axis**: `trip_hour`
   - **Y-Axis**: `COUNT(tripid)`
   - **Title**: "Hourly Trip Distribution"
   - **Sort**: Ascending by trip_hour
4. Click **Create Chart**

### Chart 7: Trip Distance Analysis (Bar Chart)

1. Create new chart
2. Choose **Bar Chart** chart type
3. Configure:
   - **X-Axis**: `distance_category`
   - **Y-Axis**: `COUNT(tripid)`
   - **Title**: "Trips by Distance Category"
4. Click **Create Chart**

### Chart 8: Tip Analysis (Bar Chart)

1. Create new chart
2. Choose **Bar Chart** chart type
3. Configure:
   - **X-Axis**: `tip_category`
   - **Y-Axis**: `COUNT(tripid)`
   - **Title**: "Trips by Tip Category"
4. Click **Create Chart**

### Chart 9: Trip Duration vs Fare (Scatter Plot)

1. Create new chart
2. Choose **Scatter Plot** chart type
3. Configure:
   - **X-Axis**: `trip_duration_minutes`
   - **Y-Axis**: `fareamount`
   - **Color**: `pickup_borough`
   - **Title**: "Trip Duration vs Fare"
4. Click **Create Chart**

### Chart 10: Heatmap: Trips by Hour and Day

1. Create new chart
2. Choose **Heatmap** chart type
3. Configure:
   - **X-Axis**: `trip_hour`
   - **Y-Axis**: `day_name`
   - **Metric**: `COUNT(tripid)`
   - **Title**: "Trips by Hour and Day"
4. Click **Create Chart**

## Step 6: Create Dashboard

1. Navigate to **Dashboards → + Dashboard**
2. Set dashboard title: `NYC Taxi Analytics Dashboard`
3. Click **Save**

## Step 7: Add Charts to Dashboard

1. In the dashboard editor, click **+ Add Chart**
2. Select each chart you created
3. Arrange them in the layout as described in the dashboard configuration guide
4. Click **Save** when done

## Step 8: Configure Filters

1. In the dashboard editor, click **+ Filter**
2. Add the following filters:

### Year Filter
- **Type**: Filter Box
- **Column**: `trip_year`
- **Default**: All years

### Month Filter
- **Type**: Filter Box
- **Column**: `trip_month`
- **Default**: All months

### Borough Filter
- **Type**: Filter Box
- **Column**: `pickup_borough`
- **Default**: All boroughs

### Payment Type Filter
- **Type**: Filter Box
- **Column**: `payment_type`
- **Default**: All payment types

### Date Range Filter
- **Type**: Date Range
- **Column**: `trip_date`
- **Default**: Last 30 days

## Step 9: Configure Dashboard Settings

1. Click the dashboard settings icon (gear icon)
2. Configure:
   - **Refresh Interval**: 5 minutes
   - **Auto-refresh**: Enabled
   - **Cache Timeout**: 300 seconds

## Step 10: Apply Custom CSS

1. In dashboard settings, go to **CSS** tab
2. Add the NYC taxi theme CSS:

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
```

3. Click **Save**

## Step 11: Test Dashboard

1. Navigate to the dashboard
2. Test all filters and interactions
3. Verify charts are displaying correctly
4. Test cross-filtering between charts

## Troubleshooting

### Common Issues

**Charts not loading:**
- Check dataset permissions
- Verify SQL queries are correct
- Check database connection

**Filters not working:**
- Verify column names match dataset
- Check filter configuration
- Test filters individually

**Performance issues:**
- Add appropriate filters to reduce data volume
- Check query execution time
- Consider using materialized views

### Getting Help

1. Check Superset logs for errors
2. Verify database connectivity
3. Test queries in SQL Lab first
4. Check Superset documentation

## Next Steps

After successful setup:

1. Share dashboard with team members
2. Set up regular data refreshes
3. Monitor dashboard performance
4. Collect user feedback and iterate

## Dashboard URL

Once created, your dashboard will be available at:
```
http://your-superset-url/superset/dashboard/nyc-taxi-analytics
``` 