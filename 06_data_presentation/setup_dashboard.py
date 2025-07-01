#!/usr/bin/env python3
"""
NYC Taxi Analytics Dashboard Setup Script

This script helps automate the setup of the NYC Taxi Analytics dashboard in Apache Superset.
It provides utility functions for creating datasets, charts, and dashboards.

Prerequisites:
- Apache Superset running and accessible
- Trino database connection configured
- Required Python packages installed
"""

import requests
import json
import time
import re
from typing import Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SupersetClient:
    """Helper class for setting up NYC Taxi Analytics dashboard in Superset"""

    def __init__(self, superset_url: str, username: str, password: str):
        """
        Initialize the Superset dashboard setup

        Args:
            superset_url: Base URL of Apache Superset
            username: Superset username
            password: Superset password
        """
        self.superset_url = superset_url.rstrip('/')
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.csrf_token = None

    def extract_csrf_token(self, html_content: str) -> Optional[str]:
        """Extract CSRF token from HTML content"""
        try:
            # Look for CSRF token in meta tag
            csrf_pattern = r'<meta[^>]*name=["\']csrf-token["\'][^>]*content=["\']([^"\']+)["\']'
            match = re.search(csrf_pattern, html_content)
            if match:
                return match.group(1)

            # Look for CSRF token in script tag
            csrf_pattern = r'csrf_token["\']?\s*:\s*["\']([^"\']+)["\']'
            match = re.search(csrf_pattern, html_content)
            if match:
                return match.group(1)

            # Look for CSRF token in form input
            csrf_pattern = r'<input[^>]*name=["\']csrf_token["\'][^>]*value=["\']([^"\']+)["\']'
            match = re.search(csrf_pattern, html_content)
            if match:
                return match.group(1)

            return None
        except Exception as e:
            logger.error(f"Error extracting CSRF token: {str(e)}")
            return None

    def login(self) -> bool:
        """Login to Superset and get CSRF token"""
        try:
            # Get login page to extract CSRF token
            login_url = f"{self.superset_url}/login/"
            response = self.session.get(login_url)

            if response.status_code != 200:
                logger.error(f"Failed to access login page: {response.status_code}")
                return False

            # Extract CSRF token from the page
            self.csrf_token = self.extract_csrf_token(response.text)

            if not self.csrf_token:
                logger.warning("Could not extract CSRF token, trying alternative method...")
                # Try to get CSRF token from the session
                csrf_response = self.session.get(f"{self.superset_url}/api/v1/security/csrf_token/")
                if csrf_response.status_code == 200:
                    self.csrf_token = csrf_response.json().get('result')

            if not self.csrf_token:
                logger.error("Failed to extract CSRF token")
                return False

            logger.info(f"Extracted CSRF token: {self.csrf_token[:10]}...")

            # Perform login
            login_data = {
                'username': self.username,
                'password': self.password,
                'csrf_token': self.csrf_token
            }

            response = self.session.post(login_url, data=login_data, allow_redirects=True)

            if response.status_code in [200, 302]:
                logger.info("Successfully logged in to Superset")
                return True
            else:
                logger.error(f"Login failed: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return False

    def get_databases(self) -> List[Dict]:
        """Get list of available databases"""
        try:
            url = f"{self.superset_url}/api/v1/database/"
            headers = {
                'X-CSRFToken': self.csrf_token,
                'Content-Type': 'application/json'
            }

            response = self.session.get(url, headers=headers)

            if response.status_code == 200:
                data = response.json()
                return data.get('result', [])
            else:
                logger.error(f"Failed to get databases: {response.status_code}")
                return []

        except Exception as e:
            logger.error(f"Error getting databases: {str(e)}")
            return []

    def create_dataset(self, database_id: int, sql_query: str, dataset_name: str) -> Optional[int]:
        """
        Create a dataset in Superset

        Args:
            database_id: ID of the database
            sql_query: SQL query for the dataset
            dataset_name: Name of the dataset

        Returns:
            Dataset ID if successful, None otherwise
        """
        try:
            dataset_url = f"{self.superset_url}/api/v1/dataset/"

            # Simplified payload with only required fields
            dataset_data = {
                "database": database_id,
                "table_name": dataset_name,
                "sql": sql_query
            }

            headers = {
                'Content-Type': 'application/json',
                'X-CSRFToken': self.csrf_token
            }

            # Debug: Log the request details
            logger.info(f"Creating dataset with URL: {dataset_url}")
            logger.info(f"Database ID: {database_id}")
            logger.info(f"Dataset name: {dataset_name}")
            logger.info(f"SQL query length: {len(sql_query)} characters")
            logger.debug(f"SQL query preview: {sql_query[:200]}...")

            response = self.session.post(
                dataset_url,
                json=dataset_data,
                headers=headers
            )

            if response.status_code == 201:
                dataset_id = response.json()['id']
                logger.info(f"Successfully created dataset '{dataset_name}' with ID {dataset_id}")
                return dataset_id
            else:
                logger.error(f"Failed to create dataset: {response.status_code} - {response.text}")
                # Debug: Log the full response for 500 errors
                if response.status_code == 500:
                    logger.error(f"Full response headers: {dict(response.headers)}")
                    logger.error(f"Response content: {response.content}")
                return None

        except Exception as e:
            logger.error(f"Error creating dataset: {str(e)}")
            return None

    def create_chart(self, dataset_id: int, chart_config: Dict) -> Optional[int]:
        """
        Create a chart in Superset

        Args:
            dataset_id: ID of the dataset
            chart_config: Chart configuration

        Returns:
            Chart ID if successful, None otherwise
        """
        try:
            chart_url = f"{self.superset_url}/api/v1/chart/"

            # Build chart configuration
            chart_data = {
                "slice_name": chart_config["name"],
                "datasource_id": dataset_id,
                "datasource_type": "table",
                "viz_type": chart_config["type"],
                "params": json.dumps(chart_config["params"]),  # Convert to JSON string
                "query_context": "{}",
                "cache_timeout": 300,
                "dashboards": []
            }

            headers = {
                'Content-Type': 'application/json',
                'X-CSRFToken': self.csrf_token
            }

            logger.info(f"Creating chart: {chart_config['name']}")

            response = self.session.post(
                chart_url,
                json=chart_data,
                headers=headers
            )

            if response.status_code == 201:
                chart_id = response.json()['id']
                logger.info(f"Successfully created chart '{chart_config['name']}' with ID {chart_id}")
                return chart_id
            else:
                logger.error(f"Failed to create chart: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            logger.error(f"Error creating chart: {str(e)}")
            return None

    def get_dashboards(self) -> List[Dict]:
        """
        Get all dashboards

        Returns:
            List of dashboards
        """
        try:
            dashboards_url = f"{self.superset_url}/api/v1/dashboard/"

            headers = {
                'X-CSRFToken': self.csrf_token
            }

            response = self.session.get(dashboards_url, headers=headers)

            if response.status_code == 200:
                dashboards = response.json()['result']
                logger.info(f"Found {len(dashboards)} dashboards")
                return dashboards
            else:
                logger.error(f"Failed to get dashboards: {response.status_code} - {response.text}")
                return []

        except Exception as e:
            logger.error(f"Error getting dashboards: {str(e)}")
            return []

    def delete_dashboard(self, dashboard_id: int) -> bool:
        """
        Delete a dashboard

        Args:
            dashboard_id: ID of the dashboard to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            delete_url = f"{self.superset_url}/api/v1/dashboard/{dashboard_id}"

            headers = {
                'X-CSRFToken': self.csrf_token
            }

            response = self.session.delete(delete_url, headers=headers)

            if response.status_code == 200:
                logger.info(f"Successfully deleted dashboard with ID {dashboard_id}")
                return True
            else:
                logger.error(f"Failed to delete dashboard: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            logger.error(f"Error deleting dashboard: {str(e)}")
            return False

    def create_dashboard(self, dashboard_config: Dict) -> Optional[int]:
        """
        Create a dashboard in Superset

        Args:
            dashboard_config: Dashboard configuration, including position_json with chart IDs

        Returns:
            Dashboard ID if successful, None otherwise
        """
        try:
            dashboard_url = f"{self.superset_url}/api/v1/dashboard/"

            dashboard_data = {
                "dashboard_title": dashboard_config["title"],
                "slug": dashboard_config["slug"],
                "position_json": dashboard_config["position_json"],
                "css": dashboard_config.get("css", ""),
                "json_metadata": "{}",
                "published": True
            }

            headers = {
                'Content-Type': 'application/json',
                'X-CSRFToken': self.csrf_token
            }

            logger.info(f"Creating dashboard: {dashboard_config['title']}")

            response = self.session.post(
                dashboard_url,
                json=dashboard_data,
                headers=headers
            )

            if response.status_code == 201:
                dashboard_id = response.json()['id']
                logger.info(f"Successfully created dashboard '{dashboard_config['title']}' with ID {dashboard_id}")
                return dashboard_id
            else:
                logger.error(f"Failed to create dashboard: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            logger.error(f"Error creating dashboard: {str(e)}")
            return None

    def get_charts(self) -> List[Dict]:
        """Get all charts"""
        try:
            charts_url = f"{self.superset_url}/api/v1/chart/"
            headers = {'X-CSRFToken': self.csrf_token}
            response = self.session.get(charts_url, headers=headers)
            if response.status_code == 200:
                charts = response.json()['result']
                logger.info(f"Found {len(charts)} existing charts")
                return charts
            else:
                logger.error(f"Failed to get charts: {response.status_code} - {response.text}")
                return []
        except Exception as e:
            logger.error(f"Error getting charts: {str(e)}")
            return []

    def delete_chart(self, chart_id: int) -> bool:
        """Delete a chart"""
        try:
            delete_url = f"{self.superset_url}/api/v1/chart/{chart_id}"
            headers = {'X-CSRFToken': self.csrf_token}
            response = self.session.delete(delete_url, headers=headers)
            if response.status_code == 200:
                logger.info(f"Successfully deleted chart with ID {chart_id}")
                return True
            else:
                logger.error(f"Failed to delete chart: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logger.error(f"Error deleting chart: {str(e)}")
            return False

    def get_datasets(self, database_id: int) -> List[Dict]:
        """
        Get all datasets for a database

        Args:
            database_id: ID of the database

        Returns:
            List of datasets
        """
        try:
            datasets_url = f"{self.superset_url}/api/v1/dataset/"
            params = {"filters": f"[('database', 'eq', {database_id})]"}

            headers = {
                'X-CSRFToken': self.csrf_token
            }

            response = self.session.get(datasets_url, params=params, headers=headers)

            if response.status_code == 200:
                datasets = response.json()['result']
                logger.info(f"Found {len(datasets)} datasets")
                return datasets
            else:
                logger.error(f"Failed to get datasets: {response.status_code} - {response.text}")
                return []

        except Exception as e:
            logger.error(f"Error getting datasets: {str(e)}")
            return []

    def delete_dataset(self, dataset_id: int) -> bool:
        """
        Delete a dataset

        Args:
            dataset_id: ID of the dataset to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            delete_url = f"{self.superset_url}/api/v1/dataset/{dataset_id}"

            headers = {
                'X-CSRFToken': self.csrf_token
            }

            response = self.session.delete(delete_url, headers=headers)

            if response.status_code == 200:
                logger.info(f"Successfully deleted dataset with ID {dataset_id}")
                return True
            else:
                logger.error(f"Failed to delete dataset: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            logger.error(f"Error deleting dataset: {str(e)}")
            return False


def get_minimal_working_query() -> str:
    """Get a minimal working query with only essential fields for the dashboard"""
    return """
    SELECT 
        ft.tripid,
        ft.pickupdatetimeid,
        ft.dropoffdatetimeid,
        ft.passengercount,
        ft.tripdistance,
        ft.fareamount,
        ft.tipamount,
        ft.totalamount,

        -- Location dimensions (essential)
        pu.borough as pickup_borough,
        do.borough as dropoff_borough,

        -- Payment dimension
        p.paymenttype as payment_type,

        -- Rate code dimension
        r.ratecode as rate_description,

        -- Time dimensions (essential)
        t."Date" as trip_date,
        t.year as trip_year,
        t.month as trip_month,
        t.hour as trip_hour,

        -- Simple calculated fields
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
        END as fare_category

    FROM iceberg.silver.fact_trip ft
    LEFT JOIN iceberg.silver.dimlocation pu ON ft.pulocationid = pu.locationid
    LEFT JOIN iceberg.silver.dimlocation do ON ft.dolocationid = do.locationid
    LEFT JOIN iceberg.silver.dimpayment p ON ft.paymenttypeid = p.paymenttypeid
    LEFT JOIN iceberg.silver.dimratecode r ON ft.ratecodeid = r.ratecodeid
    LEFT JOIN iceberg.silver.dimtime t ON ft.pickupdatetimeid = t.timeid
    WHERE ft.quality_issue = 'good'
    """


def get_working_main_query() -> str:
    """Get a working version of the main analytics query with simplified complex parts"""
    return """
    SELECT 
        ft.tripid,
        ft.pickupdatetimeid,
        ft.dropoffdatetimeid,
        ft.passengercount,
        ft.tripdistance,
        ft.fareamount,
        ft.tipamount,
        ft.totalamount,

        -- Location dimensions
        pu.borough as pickup_borough,
        pu.zone as pickup_zone,
        pu.servicezone as pickup_service_zone,
        do.borough as dropoff_borough,
        do.zone as dropoff_zone,
        do.servicezone as dropoff_service_zone,

        -- Payment dimension
        p.paymenttype as payment_type,

        -- Rate code dimension
        r.ratecode as rate_description,

        -- Time dimensions
        t."Date" as trip_date,
        t.year as trip_year,
        t.month as trip_month,
        t.dayofmonth as trip_day,
        t.hour as trip_hour,
        EXTRACT(DOW FROM t."Date") as day_of_week,

        -- Simplified day name (shorter CASE statement)
        CASE EXTRACT(DOW FROM t."Date")
            WHEN 0 THEN 'Sun'
            WHEN 1 THEN 'Mon'
            WHEN 2 THEN 'Tue'
            WHEN 3 THEN 'Wed'
            WHEN 4 THEN 'Thu'
            WHEN 5 THEN 'Fri'
            WHEN 6 THEN 'Sat'
        END as day_name,

        -- Simplified month name (shorter CASE statement)
        CASE t.month
            WHEN 1 THEN 'Jan'
            WHEN 2 THEN 'Feb'
            WHEN 3 THEN 'Mar'
            WHEN 4 THEN 'Apr'
            WHEN 5 THEN 'May'
            WHEN 6 THEN 'Jun'
            WHEN 7 THEN 'Jul'
            WHEN 8 THEN 'Aug'
            WHEN 9 THEN 'Sep'
            WHEN 10 THEN 'Oct'
            WHEN 11 THEN 'Nov'
            WHEN 12 THEN 'Dec'
        END as month_name,

        -- Simplified quarter
        CASE 
            WHEN t.month <= 3 THEN 1
            WHEN t.month <= 6 THEN 2
            WHEN t.month <= 9 THEN 3
            ELSE 4
        END as quarter,

        -- Simplified weekend detection
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

        -- Simplified tip category
        CASE 
            WHEN ft.tipamount = 0 THEN 'No Tip'
            WHEN ft.tipamount <= 5 THEN '0-5'
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
    """


def get_complex_test_query() -> str:
    """Get a test query with complex date functions and calculations"""
    return """
    SELECT 
        ft.tripid,
        ft.pickupdatetimeid,
        ft.dropoffdatetimeid,
        ft.passengercount,
        ft.tripdistance,
        ft.fareamount,
        ft.tipamount,
        ft.totalamount,

        -- Location dimensions
        pu.borough as pickup_borough,
        pu.zone as pickup_zone,
        do.borough as dropoff_borough,
        do.zone as dropoff_zone,

        -- Payment dimension
        p.paymenttype as payment_type,

        -- Rate code dimension
        r.ratecode as rate_description,

        -- Time dimensions (basic)
        t."Date" as trip_date,
        t.year as trip_year,
        t.month as trip_month,
        t.hour as trip_hour,

        -- Simple calculated fields
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

        -- Complex date functions (test these)
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

        -- Mathematical calculations (test these)
        (ft.dropoffdatetimeid - ft.pickupdatetimeid) / 100 as trip_duration_minutes,

        -- Division operations (test these)
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
    LIMIT 1000
    """


def get_progressive_test_query() -> str:
    """Get a progressive test query that builds complexity step by step"""
    return """
    SELECT 
        ft.tripid,
        ft.pickupdatetimeid,
        ft.dropoffdatetimeid,
        ft.passengercount,
        ft.tripdistance,
        ft.fareamount,
        ft.tipamount,
        ft.totalamount,

        -- Location dimensions
        pu.borough as pickup_borough,
        pu.zone as pickup_zone,
        do.borough as dropoff_borough,
        do.zone as dropoff_zone,

        -- Payment dimension
        p.paymenttype as payment_type,

        -- Rate code dimension
        r.ratecode as rate_description,

        -- Time dimensions (basic)
        t."Date" as trip_date,
        t.year as trip_year,
        t.month as trip_month,
        t.hour as trip_hour,

        -- Simple calculated fields (test these first)
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
        END as fare_category

    FROM iceberg.silver.fact_trip ft
    LEFT JOIN iceberg.silver.dimlocation pu ON ft.pulocationid = pu.locationid
    LEFT JOIN iceberg.silver.dimlocation do ON ft.dolocationid = do.locationid
    LEFT JOIN iceberg.silver.dimpayment p ON ft.paymenttypeid = p.paymenttypeid
    LEFT JOIN iceberg.silver.dimratecode r ON ft.ratecodeid = r.ratecodeid
    LEFT JOIN iceberg.silver.dimtime t ON ft.pickupdatetimeid = t.timeid
    WHERE ft.quality_issue = 'good'
    LIMIT 1000
    """


def get_simplified_main_query() -> str:
    """Get a simplified version of the main analytics query for testing"""
    return """
    SELECT 
        ft.tripid,
        ft.pickupdatetimeid,
        ft.dropoffdatetimeid,
        ft.passengercount,
        ft.tripdistance,
        ft.fareamount,
        ft.tipamount,
        ft.totalamount,

        -- Location dimensions (simplified)
        pu.borough as pickup_borough,
        pu.zone as pickup_zone,
        do.borough as dropoff_borough,
        do.zone as dropoff_zone,

        -- Payment dimension
        p.paymenttype as payment_type,

        -- Rate code dimension
        r.ratecode as rate_description,

        -- Time dimensions (simplified)
        t."Date" as trip_date,
        t.year as trip_year,
        t.month as trip_month,
        t.hour as trip_hour

    FROM iceberg.silver.fact_trip ft
    LEFT JOIN iceberg.silver.dimlocation pu ON ft.pulocationid = pu.locationid
    LEFT JOIN iceberg.silver.dimlocation do ON ft.dolocationid = do.locationid
    LEFT JOIN iceberg.silver.dimpayment p ON ft.paymenttypeid = p.paymenttypeid
    LEFT JOIN iceberg.silver.dimratecode r ON ft.ratecodeid = r.ratecodeid
    LEFT JOIN iceberg.silver.dimtime t ON ft.pickupdatetimeid = t.timeid
    WHERE ft.quality_issue = 'good'
    LIMIT 1000
    """


def get_main_analytics_query() -> str:
    """Get the main analytics SQL query"""
    return """
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
        pu.servicezone as pickup_service_zone,
        do.zone as dropoff_zone,
        do.borough as dropoff_borough,
        do.servicezone as dropoff_service_zone,

        -- Payment dimension
        p.paymenttype as payment_type,

        -- Rate code dimension
        r.ratecode as rate_description,

        -- Time dimensions
        t."Date" as trip_date,
        t.year as trip_year,
        t.month as trip_month,
        t.dayofmonth as trip_day,
        t.hour as trip_hour,
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
    """


def get_chart_configs() -> List[Dict]:
    """Get chart configurations for the NYC Taxi Analytics dashboard"""
    return [
        {
            "name": "Total Trips",
            "type": "big_number_total",
            "params": {
                "metric": {"expressionType": "SQL", "sqlExpression": "COUNT(tripid)", "label": "Total Trips"},
                "subheader": "Total trips in selected period",
            }
        },
        {
            "name": "Total Revenue",
            "type": "big_number_total",
            "params": {
                "metric": {"expressionType": "SQL", "sqlExpression": "SUM(totalamount)", "label": "Total Revenue"},
                "subheader": "Total revenue in selected period",
            }
        },
        {
            "name": "Daily Trip Trends",
            "type": "echarts_timeseries_line",
            "params": {
                "x_axis": "trip_date",
                "time_grain_sqla": "P1D",
                "metrics": [{"expressionType": "SQL", "sqlExpression": "COUNT(tripid)", "label": "Number of Trips"}],
                "y_axis_title": "Number of Trips",
                "x_axis_title": "Date",
            }
        },
        {
            "name": "Trips by Borough",
            "type": "echarts_bar",
            "params": {
                "groupby": ["pickup_borough"],
                "metrics": [{"expressionType": "SQL", "sqlExpression": "COUNT(tripid)", "label": "Number of Trips"}],
                "x_axis_title": "Borough",
                "y_axis_title": "Number of Trips",
                "rich_tooltip": True,
            }
        },
        {
            "name": "Revenue by Payment Type",
            "type": "pie",
            "params": {
                "groupby": ["payment_type"],
                "metric": {"expressionType": "SQL", "sqlExpression": "SUM(totalamount)", "label": "Total Revenue"},
                "show_legend": True,
            }
        },
        {
            "name": "Distance Distribution",
            "type": "histogram",
            "params": {
                "all_columns": ["tripdistance"],
                "number_of_bins": 20,
                "x_axis_label": "Distance (miles)",
                "y_axis_label": "Number of Trips"
            }
        },
        {
            "name": "Fare Amount Distribution",
            "type": "histogram",
            "params": {
                "all_columns": ["fareamount"],
                "number_of_bins": 20,
                "x_axis_label": "Fare Amount ($)",
                "y_axis_label": "Number of Trips"
            }
        },
        {
            "name": "Hourly Trip Patterns",
            "type": "echarts_timeseries_line",
            "params": {
                "x_axis": "trip_date",
                "time_grain_sqla": "PT1H",
                "metrics": [{"expressionType": "SQL", "sqlExpression": "COUNT(tripid)", "label": "Number of Trips"}],
                "y_axis_title": "Number of Trips",
                "x_axis_title": "Time"
            }
        }
    ]


def get_dashboard_config() -> Dict:
    """Get dashboard configuration for NYC Taxi Analytics"""
    return {
        "title": "NYC Taxi Analytics Dashboard",
        "slug": "nyc-taxi-analytics",
        "position_json": json.dumps({
            "CHART-1": {"x": 0, "y": 0, "w": 3, "h": 2},
            "CHART-2": {"x": 3, "y": 0, "w": 3, "h": 2},
            "CHART-3": {"x": 6, "y": 0, "w": 6, "h": 4},
            "CHART-4": {"x": 0, "y": 2, "w": 6, "h": 4},
            "CHART-5": {"x": 0, "y": 6, "w": 4, "h": 4},
            "CHART-6": {"x": 4, "y": 6, "w": 4, "h": 4},
            "CHART-7": {"x": 8, "y": 6, "w": 4, "h": 4},
            "CHART-8": {"x": 0, "y": 10, "w": 12, "h": 4}
        }),
        "css": """
        .dashboard-header {
            background: linear-gradient(135deg, #ffd700 0%, #ffed4e 100%);
            color: #000;
            border-bottom: 3px solid #000;
            padding: 15px;
            font-weight: bold;
        }
        """
    }


def main():
    """Main function to set up the NYC Taxi Analytics Dashboard assets."""
    logger.info("Starting NYC Taxi Analytics Asset Setup")

    superset = SupersetClient("http://localhost:30088", "admin", "admin")

    if not superset.login():
        logger.error("Failed to login to Superset. Exiting.")
        return

    # --- Full Cleanup of Existing Assets ---
    logger.info("--- Starting Cleanup of Existing Assets ---")

    dashboard_slug = "nyc-taxi-analytics"
    existing_dashboards = superset.get_dashboards()
    for dashboard in existing_dashboards:
        if dashboard.get('slug') == dashboard_slug:
            logger.info(
                f"Found and deleting existing dashboard: '{dashboard['dashboard_title']}' (ID: {dashboard['id']})")
            superset.delete_dashboard(dashboard['id'])
            break

    chart_configs = get_chart_configs()
    chart_names_to_delete = {c['name'] for c in chart_configs}
    existing_charts = superset.get_charts()
    for chart in existing_charts:
        if chart.get('slice_name') in chart_names_to_delete:
            logger.info(f"Found and deleting existing chart: '{chart['slice_name']}' (ID: {chart['id']})")
            superset.delete_chart(chart['id'])

    main_dataset_name = "NYC Taxi Analytics"
    databases = superset.get_databases()
    if databases:
        database_id = databases[0]['id']
        existing_datasets = superset.get_datasets(database_id)
        for dataset in existing_datasets:
            if dataset.get('table_name') == main_dataset_name:
                logger.info(f"Found and deleting existing dataset: '{dataset['table_name']}' (ID: {dataset['id']})")
                superset.delete_dataset(dataset['id'])
                break

    logger.info("--- Cleanup Complete ---")

    # --- Asset Creation ---
    logger.info("--- Starting Fresh Asset Creation ---")

    databases = superset.get_databases()
    if not databases:
        logger.error("No databases found. Cannot create dataset. Exiting.")
        return

    database_id = databases[0]['id']
    logger.info(f"Using database: '{databases[0].get('database_name', 'Unknown')}' (ID: {database_id})")

    main_query = get_minimal_working_query()
    main_dataset_id = superset.create_dataset(database_id, main_query, main_dataset_name)

    if not main_dataset_id:
        logger.error("Failed to create main dataset. Exiting.")
        return

    logger.info("Creating fresh charts...")
    chart_info = []
    for config in chart_configs:
        chart_id = superset.create_chart(main_dataset_id, config)
        if chart_id:
            chart_info.append({'name': config['name'], 'id': chart_id})
        else:
            logger.warning(f"Failed to create chart: {config['name']}")

    if not chart_info:
        logger.error("No charts were created. Exiting.")
        return

    logger.info("--- Asset Creation Completed Successfully! ---")
    logger.info(f"Dataset '{main_dataset_name}' created with ID: {main_dataset_id}")
    logger.info("The following charts were created and are ready for use:")
    for chart in chart_info:
        logger.info(f"  - {chart['name']} (ID: {chart['id']})")
    logger.info("")
    logger.info(
        "NEXT STEP: Please follow the instructions in '06_data_presentation/manual_setup_guide.md' to create the dashboard.")


if __name__ == "__main__":
    main()