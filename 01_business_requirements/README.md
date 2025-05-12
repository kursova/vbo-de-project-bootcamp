# vbo-de-project-bootcamp
NYC Yellow Taxi Data Analysis and Visualization Project

This project aims to uncover strategic insights into urban mobility by analyzing New York City’s yellow taxi trip data. Using data provided by the NYC Taxi & Limousine Commission (TLC) in Parquet format, we apply core data engineering processes to transform raw data into meaningful and interactive visual outputs.

🚕 Project Scope

The focus of this project is to build a modern data platform and use it to analyze and visualize yellow taxi data from NYC. The key areas of analysis include:
	•	Density Analysis: Identify the most frequent pickup/drop-off zones and peak hours.
	•	Airport Transfer Analysis: Explore trip patterns related to airport rides, including fare, distance, and passenger count.
	•	Time-Based Trends: Analyze daily, weekly, and monthly fluctuations in taxi usage.
	•	Key Performance Indicators (KPIs): Evaluate average trip duration, distance, fare, and other performance metrics.

🧱 Project Stages

1. Project Definition & Requirements
	•	Business Needs: Understand the transportation trends within NYC using TLC data.
	•	Data Sources: NYC TLC yellow taxi trip data (Parquet format).
	•	Stakeholders: Data engineers, analysts, city planners, and developers.

2. Infrastructure Setup
	•	Minikube & kubectl Installation
	•	Deployment of key data platform components:
	•	Object Storage
	•	CI/CD Infrastructure
	•	Apache Spark
	•	Superset
	•	Data Catalog
	•	Apache Airflow
	•	Trino (SQL query engine)

3. Data Modeling

Organizing the data in a multi-layered structure:
	•	Bronze: Raw ingested data
	•	Silver: Cleaned and enriched data
	•	Gold: Aggregated data ready for analysis and visualization

4. Data Ingestion
	•	TLC yellow taxi trip records are downloaded and ingested daily.
	•	Each record includes timestamp, location, fare, passenger count, and trip distance.

5. Data Cleaning & Enrichment
	•	Handle missing, incorrect, and inconsistent records.
	•	Extract new time-based columns (e.g., hour, day, month) from timestamps.
	•	Match pickup and drop-off coordinates to NYC zone maps for location-based analysis.

6. Data Loading
	•	Processed data is stored in the lakehouse architecture.
	•	Data is categorized into Bronze, Silver, and Gold layers for better data governance and performance.

7. Visualization & Reporting

Using Apache Superset and Trino, we create:
	•	Interactive density maps of pickup/drop-off zones
	•	Time-series dashboards showing daily and monthly trends
	•	Custom airport ride analysis dashboards

🎯 Project Outcomes

This project transforms real-world taxi trip data into actionable insights through a complete modern data engineering pipeline. It demonstrates the practical use of tools such as:
	•	Python
	•	Apache Spark
	•	Apache Airflow
	•	Trino
	•	Superset

By completing this project, we build a scalable and interactive analytics environment tailored to urban transportation data.

📁 Data Source

The yellow taxi dataset is provided by the NYC Taxi & Limousine Commission and is publicly available in Parquet format.
NYC TLC Trip Record Data
