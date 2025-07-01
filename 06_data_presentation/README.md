# NYC Taxi Data Analytics Dashboard with Apache Superset

## 🎯 Learning Objectives

By the end of this tutorial, you will be able to:
- Connect Apache Superset to a Trino data warehouse
- Create interactive dashboards using SQL queries manually
- Build charts step-by-step in the Superset UI
- Configure filters, charts, and cross-filtering manually
- Demonstrate data analytics capabilities to stakeholders

## 📁 Project Files Overview

This directory contains everything you need to build and demonstrate a complete analytics dashboard manually:

| File | Purpose | When to Use |
|------|---------|-------------|
| **[README.md](./README.md)** | **Main tutorial guide** | **Start here!** Follow this step-by-step manual process |
| **[dashboard_queries.sql](./dashboard_queries.sql)** | SQL queries for all charts | Copy queries from here to create charts manually |
| **[dashboard_configuration.md](./dashboard_configuration.md)** | Dashboard layout and filter setup | Reference for configuring your dashboard |
| **[superset_connection_setup.md](./superset_connection_setup.md)** | Database connection guide with screenshots | Step 2 - Connect Superset to Trino |
| **[manual_setup_guide.md](./manual_setup_guide.md)** | Detailed manual UI setup instructions | Follow this for detailed UI steps |
| **[requirements.txt](./requirements.txt)** | Python dependencies | Not needed for manual approach |

## 📋 How to Use dashboard_queries.sql

The `dashboard_queries.sql` file contains all the SQL queries you need for creating charts in Superset. Here's how to use it:

### **Step-by-Step Manual Chart Creation**

1. **Open Superset** and go to **SQL Lab**
2. **Copy a query** from `dashboard_queries.sql`
3. **Paste it** into SQL Lab and run it
4. **Save as Dataset** if the query works
5. **Create Chart** from that dataset manually

**Example:**
```sql
-- Copy this from dashboard_queries.sql (lines 7-10)
SELECT COUNT(*) as total_trips
FROM iceberg.silver.fact_trip
WHERE quality_issue = 'good';
```

### **Learning Approach**

Study the queries to understand:
- How to join fact and dimension tables
- How to calculate derived fields
- How to filter data properly
- How to structure SQL for different chart types

## 💡 Pro Tips

1. **Always test queries** in SQL Lab before creating charts
2. **Use the quality filter**: `WHERE quality_issue = 'good'`
3. **Start with simple queries** and build complexity
4. **Save working queries** as datasets for reuse
5. **Use the calculated fields** (like `tip_percentage`) in your charts

## 🖼️ How to Configure Each Chart in Superset

This section provides explicit, step-by-step instructions for configuring each main chart in Superset. Use this as a reference when building your dashboard manually.

### Chart Configuration Table

| Chart Name              | X-Axis      | Time Grain | Metrics (Y-Axis)      | Dimensions      | Filters         | Notes                                 |
|------------------------|-------------|------------|-----------------------|-----------------|-----------------|---------------------------------------|
| Daily Trip Trends      | trip_date   | Day        | SUM(trip_count)       | *(empty)*       | trip_date       | Use dataset with trip_count           |
| Trips by Borough       | *(empty)*   | N/A        | SUM(trip_count)       | pickup_borough  | *(optional)*    | Bar chart, group by borough           |
| Revenue by Payment     | *(empty)*   | N/A        | SUM(total_revenue)    | payment_type    | *(optional)*    | Pie chart, group by payment_type      |
| Total Trips KPI        | *(empty)*   | N/A        | SUM(trip_count)       | *(empty)*       | *(optional)*    | Big Number chart                      |

### Step-by-Step Example: Daily Trip Trends (Line Chart)

- save this query as dataset
```sql
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
```
1. **Go to Charts → + Chart**
2. **Select your dataset**: e.g., "Daily Trip Trends"
3. **Chart Type**: Line Chart (Time-series)
4. **X-Axis**: `trip_date`
5. **Time Grain**: Day
6. **Metrics (Y-Axis)**: `SUM(trip_count)` (or just `trip_count` if available)
7. **Dimensions**: *(leave empty)*
8. **Filters**: *(optional, e.g., trip_date)*
9. **Save the chart** with a descriptive name

### Step-by-Step Example: Trips by Borough (Bar Chart)
- query
```sql
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
```
1. **Go to Charts → + Chart**
2. **Select your dataset**: e.g., "Trips by Borough"
3. **Chart Type**: Bar Chart
4. **X-Axis**: pickup_borough
5. **Metrics (Y-Axis)**: SUM(trip_count)
6. **Dimensions**: (leave empty)
7. **Title**: Trips by Borough
8. **Save the chart**

### Step-by-Step Example: Revenue by Payment Type (Pie Chart)
- query
```sql
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

```
1. **Go to Charts → + Chart**
2. **Select your dataset**: e.g., "Revenue by Payment Type"
3. **Chart Type**: Pie Chart
4. **Metrics (Y-Axis)**: `SUM(total_revenue)`
5. **Dimensions**: `payment_type`
6. **Filters**: *(optional)*
7. **Save the chart**

### Step-by-Step Example: Total Trips KPI (Big Number)
- query
```sql
SELECT COUNT(*) as total_trips
FROM iceberg.silver.fact_trip
WHERE quality_issue = 'good';
```
1. **Go to Charts → + Chart**
2. **Select your dataset**: e.g., "Total Trips Dataset"
3. **Chart Type**: Big Number
4. **Metrics (Y-Axis)**: `SUM(trip_count)`
5. **Dimensions**: *(leave empty)*
6. **Save the chart**

---

**Tips:**
- The **Y-axis** is always defined by the **Metrics** field in Superset.
- For time series charts, set the **X-Axis** to your date column and choose the appropriate **Time Grain**.
- For bar and pie charts, use **Dimensions** to group by a column (e.g., borough, payment type).
- If you don't see the metric you want, you can create a custom metric (e.g., `SUM(trip_count)` or `COUNT(*)`).
- Always test your dataset in SQL Lab first to ensure the columns exist.

Now, follow the manual step-by-step flow below to build your dashboard!

---

## 🚀 Manual Step-by-Step Demonstration Flow

### Prerequisites Checklist
Before starting, ensure you have:
- [ ] Kubernetes cluster running with all services (Trino, Superset, etc.)
- [ ] Silver layer data loaded (fact_trip, dimlocation, dimpayment, dimratecode, dimtime)
- [ ] Access to Superset web interface

---

## Step 1: Connect Superset to Trino 🔗

**Goal**: Establish connection between Superset and your data warehouse

**Action**: Follow the detailed guide in **[superset_connection_setup.md](./superset_connection_setup.md)**

**Key Steps**:
1. Open Superset web interface
2. Go to **Data → Databases → + Database Connection**
3. Use connection string: `trino://trino-coordinator.trino.svc.cluster.local:8080/iceberg/silver`
4. Test the connection

**Expected Outcome**: Connection successful, you can see the silver schema tables

**Verification Query** (run in Superset SQL Lab):
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
FROM iceberg.silver.dimlocation;
```

**Troubleshooting**: If connection fails, check that Trino service is running and accessible

---

## Step 2: Explore Available Data 📊

**Goal**: Understand the data structure and available tables

**Action**: Review the SQL queries in **[dashboard_queries.sql](./dashboard_queries.sql)**

**Key Tables to Explore**:
- `fact_trip`: Main transaction data (trips, fares, distances)
- `dimlocation`: Geographic data (boroughs, zones)
- `dimpayment`: Payment types (credit card, cash, etc.)
- `dimratecode`: Rate codes (standard, JFK, etc.)
- `dimtime`: Time dimensions (dates, hours, etc.)

**Test Query** (run in Superset SQL Lab):
```sql
-- Quick overview of available data
SELECT 
    t.year,
    t.month,
    COUNT(*) as trip_count,
    AVG(ft.fareamount) as avg_fare
FROM iceberg.silver.fact_trip ft
LEFT JOIN iceberg.silver.dimtime t ON ft.pickupdatetimeid = t.timeid
WHERE ft.quality_issue = 'good'
GROUP BY t.year, t.month
ORDER BY t.year, t.month;
```

**Expected Outcome**: You see trip data across different time periods

---

## Step 3: Create Your First Dataset 📋

**Goal**: Create a dataset from a SQL query

**Action**: Follow these steps manually

1. **Go to SQL Lab** in Superset
2. **Copy this query** from `dashboard_queries.sql`:

```sql
-- Total Trips KPI
SELECT COUNT(*) as total_trips
FROM iceberg.silver.fact_trip
WHERE quality_issue = 'good';
```

3. **Run the query** to verify it works
4. **Click "Save"** button
5. **Name it**: "Total Trips Dataset"
6. **Save as Dataset**

**Expected Outcome**: Dataset created and visible in Data → Datasets

---

## Step 4: Create Your First Chart 📈

**Goal**: Create a Big Number chart from your dataset

**Action**: Follow these steps manually

1. **Go to Charts** → **+ Chart**
2. **Select your dataset**: "Total Trips Dataset"
3. **Choose chart type**: "Big Number"
4. **Configure the chart**:
   - **Metric**: `total_trips`
   - **Subheader**: "Total trips in selected period"
   - **Title**: "Total Trips"
5. **Click "Create Chart"**
6. **Save the chart** with name "Total Trips KPI"

**Expected Outcome**: Your first chart is created and saved

---

## Step 5: Create More Charts Manually 🎨

**Goal**: Build a collection of different chart types

**Action**: Create these charts one by one using queries from `dashboard_queries.sql`

### **Chart 2: Daily Trip Trends (Line Chart)**

1. **Go to SQL Lab**
2. **Copy this query** from `dashboard_queries.sql` (lines 25-32):

```sql
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
```

3. **Run and save as dataset**: "Daily Trip Trends"
4. **Create chart**:
   - **Type**: Line Chart (Time-series)
   - **X-axis**: `trip_date`
   - **Time Grain**: Day
   - **Metrics**: `SUM(trip_count)`
   - **Dimensions**: *(leave empty)*
   - **Title**: "Daily Trip Trends"

### **Chart 3: Trips by Borough (Bar Chart)**

1. **Go to SQL Lab**
2. **Copy this query** from `dashboard_queries.sql` (lines 50-57):

```sql
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
```

3. **Run and save as dataset**: "Trips by Borough"
4. **Create chart**:
   - **Type**: Bar Chart
   - **X-axis**: pickup_borough
   - **Metrics**: SUM(trip_count)
   - **Dimensions**: (leave empty)
   - **Title**: Trips by Borough

### **Chart 4: Revenue by Payment Type (Pie Chart)**

1. **Go to SQL Lab**
2. **Copy this query** from `dashboard_queries.sql` (lines 80-87):

```sql
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
```

3. **Run and save as dataset**: "Revenue by Payment Type"
4. **Create chart**:
   - **Type**: Pie Chart
   - **Group by**: `payment_type`
   - **Metric**: `SUM(total_revenue)`
   - **Title**: "Revenue by Payment Type"

---

## Step 6: Create the Dashboard 🎯

**Goal**: Combine all your charts into a dashboard

**Action**: Follow these steps manually

1. **Go to Dashboards** → **+ Dashboard**
2. **Name it**: "NYC Taxi Analytics"
3. **Add your charts**:
   - Click "Add Chart" for each chart you created
   - Select your saved charts
4. **Arrange the layout**:
   - Drag and drop charts to position them
   - Resize charts as needed
5. **Save the dashboard**

**Expected Outcome**: A complete dashboard with all your charts

---

## Step 7: Add Filters and Interactivity 🔧

**Goal**: Make your dashboard interactive with filters

**Action**: Follow these steps manually

1. **Edit your dashboard**
2. **Add filters**:
   - **Year Filter**: Add filter for `trip_year`
   - **Borough Filter**: Add filter for `pickup_borough`
   - **Payment Type Filter**: Add filter for `payment_type`
3. **Configure cross-filtering**:
   - Enable cross-filtering between charts
   - Test by clicking on different values
4. **Save the dashboard**

**Expected Outcome**: Interactive dashboard with working filters

---

## Step 8: Customize and Polish ✨

**Goal**: Make your dashboard look professional

**Action**: Follow the guide in **[dashboard_configuration.md](./dashboard_configuration.md)**

**Key Customizations**:
- Dashboard title and description
- Chart colors and styling
- Filter default values
- Chart titles and labels
- Dashboard layout and spacing

**Expected Outcome**: Professional-looking dashboard ready for presentation

---

## 🎤 Manual Demonstration Script for Students

### Opening (2 minutes)
"Today we'll build a complete analytics dashboard for NYC taxi data manually. We'll start with raw data in our silver layer and end with an interactive dashboard that business users can use for decision making."

### Step-by-Step Walkthrough (20 minutes)

**1. Show the Data Structure (3 minutes)**
```sql
-- Run this in Superset SQL Lab
SELECT 
    'fact_trip' as table_name,
    COUNT(*) as row_count
FROM iceberg.silver.fact_trip
WHERE quality_issue = 'good';
```
*"Here we have our fact table with millions of trip records, joined with dimension tables for location, time, payment, and rate information."*

**2. Create First Chart Manually (5 minutes)**
- Show SQL Lab
- Copy query from `dashboard_queries.sql`
- Run query and save as dataset
- Create chart manually
- *"This is how you create charts step by step in Superset."*

**3. Build Multiple Charts (8 minutes)**
- Create 3-4 different chart types
- Show different SQL queries
- Demonstrate chart configuration
- *"Each chart type requires different SQL structure and configuration."*

**4. Create Dashboard (4 minutes)**
- Combine all charts into dashboard
- Add filters and interactivity
- Show final result
- *"This is how you build a complete analytics dashboard manually."*

### Key Talking Points

**Manual Process Benefits**:
- "You understand every step of the process"
- "You can customize each chart individually"
- "You learn SQL and Superset UI thoroughly"
- "You can troubleshoot issues more easily"

**Data Architecture**:
- "Silver layer contains cleaned, validated data"
- "Star schema optimizes for analytical queries"
- "Quality filtering ensures only good data is analyzed"

**Dashboard Features**:
- "Real-time filtering and cross-filtering"
- "Multiple chart types for different insights"
- "Professional appearance suitable for business users"

---

## 🔧 Troubleshooting Guide

### Common Issues and Solutions

**1. Connection Failed**
- **Problem**: Can't connect to Trino
- **Solution**: Check if Trino service is running: `kubectl get pods -n default | grep trino`

**2. No Data in Tables**
- **Problem**: Tables exist but are empty
- **Solution**: Run data transformation jobs first: `kubectl apply -f ../05_data_transformation/load_facts/load_facts_sparkApplication.yaml`

**3. SQL Query Errors**
- **Problem**: Query fails in SQL Lab
- **Solution**: Check table names, column names, and syntax. Verify tables exist.

**4. Charts Not Loading**
- **Problem**: Chart shows errors after creation
- **Solution**: Verify SQL queries work in SQL Lab first, check dataset permissions

**5. Performance Issues**
- **Problem**: Dashboard loads slowly
- **Solution**: Add date filters to limit data volume, use appropriate chart types

---

## 📈 Advanced Manual Techniques

### For Advanced Students

**1. Custom SQL Queries**
- Modify existing queries from `dashboard_queries.sql`
- Add your own calculated fields
- Create complex aggregations
- Build custom filters

**2. Advanced Chart Types**
- Create heatmaps for time patterns
- Build scatter plots for correlations
- Design custom visualizations
- Add drill-down capabilities

**3. Dashboard Optimization**
- Optimize SQL queries for performance
- Add caching strategies
- Implement dynamic filters
- Create responsive layouts

---

## 🎯 Success Criteria

You've successfully completed this tutorial when you can:

✅ **Connect Superset to Trino** and access silver layer tables  
✅ **Create datasets manually** from SQL queries  
✅ **Build charts step-by-step** in the Superset UI  
✅ **Create a complete dashboard** with multiple chart types  
✅ **Add filters and interactivity** to your dashboard  
✅ **Explain the data architecture** and star schema design  
✅ **Troubleshoot common issues** and provide solutions  
✅ **Customize charts and dashboards** for specific needs  

---

## 📚 Additional Resources

- **[Apache Superset Documentation](https://superset.apache.org/docs/intro)**
- **[Trino Documentation](https://trino.io/docs/)**
- **[Iceberg Documentation](https://iceberg.apache.org/docs/)**
- **[Star Schema Design](https://en.wikipedia.org/wiki/Star_schema)**

---

## 🚀 Next Steps

After completing this tutorial, consider:

1. **Extending the Dashboard**: Add more charts and analytics
2. **Custom Queries**: Create queries for specific business questions
3. **Advanced Visualizations**: Implement complex chart types
4. **Performance Tuning**: Optimize queries and dashboard performance
5. **User Training**: Teach business users how to use the dashboard

---

*This tutorial provides a complete foundation for building data analytics dashboards manually. The step-by-step approach ensures deep understanding of both SQL and Superset UI.* 