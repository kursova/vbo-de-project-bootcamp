This guide for **developing, testing, and deploying** your GitHub-to-S3 data ingestion pipeline using **Airflow with KubernetesExecutor**, and **Python 3.12**, including both **local development/testing** and **Kubernetes orchestration**.

---

# ✅ Project Structure

```
project-root/
├── dags/
│   └── github_to_s3_dag.py         # Airflow DAG
├── src/
│   └── highway_ingester/
│       ├── __init__.py
│       ├── github_downloader.py    # download + upload logic
│       └── logs/                   # (optional log output)
├── tests/
│   └── test_github_downloader.py   # pytest tests
├── requirements.txt
├── Dockerfile
├── .env                            # AWS credentials for local dev
└── README.md
```

---

# 🚧 Development Workflow (Locally with Python 3.12)

### 1. ✅ Create virtual environment with Python 3.12

```bash
pyenv install 3.12.3
pyenv virtualenv 3.12.3 github-ingester-env
pyenv activate github-ingester-env
```

### 2. ✅ Install dependencies

```bash
pip install -r requirements.txt
```

- `requirements.txt`:

```txt
boto3
requests
python-dotenv
pytest
```

### 3. ✅ Create a `.env` file

```
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_DEFAULT_REGION=us-east-1
GITHUB_TOKEN=your_github_token
S3_ENDPOINT=minio_adress (dev: localhost:30900, prod: minio...:9000
```

### 4. ✅ Development and local tests
- Develop the code
- Local test
```bash
pytest tests -v
```

---

# 🧪 Test Uploads to S3 (Locally)

Manually call the main:
- main.py
```python
from highway_ingester.github_downloader import download_github_dir, upload_to_s3, get_boto3_client
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

local_downloaded_path = Path(os.getenv('LOCAL_DOWNLOADED_PATH'))  # or wherever your files are
bucket = os.getenv('BUCKET')
s3_path = os.getenv('S3_PATH')
download_github_dir(
    repo_owner=os.getenv('REPO_OWNER'),
    repo_name=os.getenv('REPO_NAME'),
    dir_path=os.getenv('DIR_PATH'),
    branch="master",
    local_dir=local_downloaded_path,
    token=os.getenv('GITHUB_TOKEN')
)

s3_client = get_boto3_client(service_name="s3", aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                             aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'), region_name=os.getenv('REGION_NAME'),
                             endpoint_url=os.getenv('DEV_S3_ENDPOINT'))

upload_to_s3(local_downloaded_path, bucket, s3_path, s3_client)
```

---

# 🚀 Deployment to Airflow on Kubernetes

### Dockerfile (Python 3.12)

```Dockerfile
FROM python:3.12-slim

WORKDIR /app

# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/highway_ingester ./highway_ingester
```

### Build and push Docker image
- One level above the src directory
```bash
YOUR_USERNAME=kursova
docker build -t ghcr.io/$YOUR_USERNAME/github-ingester:latest .
docker push ghcr.io/$YOUR_USERNAME/github-ingester:latest
```

### Write your DAG (`dags/github_to_s3_dag.py`)

docker push ghcr.io/kursova/github-ingester kursova/github-ingester:1.1
docker push kursova/github-ingester:1.1