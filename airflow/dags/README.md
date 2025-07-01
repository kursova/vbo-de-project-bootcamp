# NYC Taxi Data Ingestion - Airflow DAG

Bu proje, NYC Taxi verilerini GitHub'dan MinIO S3'e otomatik olarak aktaran bir Apache Airflow DAG'ı içerir. DAG, günlük olarak çalışarak verileri güvenilir bir şekilde ingest eder.

## 📋 Proje Özeti

- **Kaynak**: GitHub Repository (`erkansirin78/datasets`)
- **Hedef**: MinIO S3 Bucket (bronze katmanı)
- **Veri Formatı**: Parquet dosyaları
- **Çalışma Zamanı**: Her gün 02:00
- **Tarih Mantığı**: 2 gün geriye (veri kullanılabilirliği için)

## 🏗️ Mimari

```
GitHub Repository → Airflow DAG → MinIO S3
     (Kaynak)         (ETL)        (Hedef)
```

### Bileşenler
- **Airflow**: Workflow orchestration
- **MinIO**: S3 compatible object storage
- **Kubernetes**: Container orchestration
- **Python**: ETL mantığı

## 📂 Dizin Yapısı

### GitHub Kaynak Yapısı
```
yellow_tripdata_partitioned_by_day/
├── year=2024/
│   ├── month=5/
│   │   ├── day=1/
│   │   │   ├── part-0001.parquet
│   │   │   └── part-0002.parquet
│   │   ├── day=2/
│   │   └── day=3/
│   └── month=6/
```

### S3 Hedef Yapısı
```
s3://bronze/yellow_tripdata_partitioned_by_day/
├── year=2024/
│   ├── month=5/
│   │   ├── day=1/
│   │   │   ├── part-0001.parquet
│   │   │   └── part-0002.parquet
│   │   ├── day=2/
│   │   └── day=3/
```

## 🔄 DAG Workflow

### Task Sequence
1. **get_target_date**: Hedef tarihi hesapla (execution_date - 2 gün)
2. **check_github_data**: GitHub'da veri varlığını kontrol et
3. **check_s3_data**: S3'te veri varlığını kontrol et
4. **download_and_upload**: Dosyaları indir ve S3'e yükle
5. **log_summary**: İşlem özetini logla

### Task Dependencies
```
get_target_date → [check_github_data, check_s3_data] → download_and_upload → log_summary
```

## ⚙️ Konfigürasyon

### DAG Parametreleri
```python
- owner: 'data-team'
- start_date: datetime(2024, 5, 1)
- schedule_interval: '0 2 * * *'  # Her gün 02:00
- max_active_runs: 1
- retries: 2
- retry_delay: 5 dakika
```

### S3/MinIO Ayarları
```python
S3_CONFIG = {
    'aws_access_key_id': 'minioadmin',
    'aws_secret_access_key': 'minioadmin123',
    'endpoint_url': 'http://minio.minio.svc.cluster.local:9000',
    'region_name': 'us-east-1'
}
```

## 🚀 Kullanım Kılavuzu

### 1. Normal Otomatik Çalışma
DAG varsayılan olarak her gün 02:00'da çalışır ve 2 gün öncesinin verisini çeker.

**Örnek**: 5 Mayıs 2024 02:00'da çalışan DAG → 3 Mayıs 2024 verisini çeker

### 2. Manual Trigger (Belirli Tarih)

#### Airflow UI Üzerinden:
1. Airflow Web UI'ya gidin
2. `nyc_taxi_data_ingestion_simple` DAG'ını bulun
3. **"Trigger DAG"** butonuna tıklayın
4. **"Logical Date"** seçin (istediğiniz execution date)
5. **"Trigger"** butonuna tıklayın

**Örnekler**:
- 20 Mayıs verisini çekmek için: `execution_date = 2024-05-22`
- 15 Mayıs verisini çekmek için: `execution_date = 2024-05-17`
- Bugünkü veriyi çekmek için: `execution_date = bugün + 2 gün`

#### CLI Üzerinden:
```bash
# Belirli bir tarih için
kubectl exec -it airflow-scheduler-xxx -n airflow -- \
  airflow dags trigger nyc_taxi_data_ingestion_simple \
  --execution-date 2024-05-30

# Bu komut 2024-05-28 verisini çekecek
```

### 3. Backfill (Tarih Aralığı)

Birden fazla günün verisini toplu olarak çekmek için:

```bash
kubectl exec -it airflow-scheduler-xxx -n airflow -- \
  airflow dags backfill nyc_taxi_data_ingestion_simple \
  --start-date 2024-05-01 \
  --end-date 2024-05-31
```

## 🔍 Monitoring ve Troubleshooting

### Logları Kontrol Etme
```bash
# Scheduler logları
kubectl logs -f airflow-scheduler-xxx -n airflow

# Worker logları
kubectl logs -f airflow-worker-xxx -n airflow
```

### S3'teki Verileri Kontrol Etme
```bash
# MinIO CLI ile
mc ls minio/bronze/yellow_tripdata_partitioned_by_day/

# Specific date için
mc ls minio/bronze/yellow_tripdata_partitioned_by_day/year=2024/month=5/day=3/
```

### Common Issues ve Çözümleri

#### 1. GitHub API Rate Limit
**Hata**: `403 API rate limit exceeded`
**Çözüm**: DAG'ı daha seyrek çalıştırın veya GitHub token kullanın

#### 2. S3 Connection Error
**Hata**: `Unable to connect to MinIO`
**Çözüm**: 
- MinIO servisinin çalıştığını kontrol edin
- Network connectivity'yi test edin

#### 3. Missing Data
**Hata**: `No parquet files found`
**Çözüm**: 
- GitHub'da hedef tarihin verisinin mevcut olduğunu kontrol edin
- Tarih formatını doğrulayın

## 📊 Performans Metrikleri

### Başarılı Çalışma Örneği (4 Mayıs 2024'e kadar)
- **İşlenen Günler**: 2 Mayıs - 4 Mayıs 2024
- **Başarı Oranı**: %100
- **Ortalama İşlem Süresi**: ~10-15 dakika/gün
- **İşlenen Dosya Sayısı**: Gün başına 20-50 parquet dosyası

### DAG Durumu Kontrolü
```bash
# DAG durumu
kubectl exec -it airflow-scheduler-xxx -n airflow -- \
  airflow dags state nyc_taxi_data_ingestion_simple 2024-05-04

# Task durumları
kubectl exec -it airflow-scheduler-xxx -n airflow -- \
  airflow tasks state nyc_taxi_data_ingestion_simple download_and_upload 2024-05-04
```

## 🔐 Güvenlik

### Credential Management
- MinIO credentials DAG içinde hardcoded (development ortamı için)
- Production için Kubernetes secrets kullanılması önerilir:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: minio-credentials
data:
  access-key: <base64-encoded-key>
  secret-key: <base64-encoded-secret>
```

## 🚧 Gelecek Geliştirmeler

### Önerilen İyileştirmeler
1. **Configuration Management**: Airflow Variables/Connections kullanımı
2. **Data Quality Checks**: Dosya boyutu ve format validasyonu
3. **Alerting**: Slack/Email notification ekleme
4. **Metrics**: Prometheus/Grafana integration
5. **Data Cataloging**: Metadata management ekleme

### Kod Örneği - Configuration ile Flexible Date
```python
def get_target_date(**context):
    dag_run = context.get('dag_run')
    if dag_run and dag_run.conf:
        custom_date = dag_run.conf.get('target_date')
        if custom_date:
            return datetime.strptime(custom_date, '%Y-%m-%d')
    
    # Default: 2 gün geriye
    execution_date = context['execution_date']
    return execution_date - timedelta(days=2)
```

## 📞 Support

**Geliştirici**: Data Team  
**Proje**: NYC Taxi Data Ingestion  
**Version**: 1.0  
**Son Güncelleme**: Mayıs 2024

### Quick Commands Cheat Sheet
```bash
# DAG durumu
airflow dags state nyc_taxi_data_ingestion_simple <date>

# Manuel trigger
airflow dags trigger nyc_taxi_data_ingestion_simple --execution-date <date>

# Logları görüntüle
airflow tasks log nyc_taxi_data_ingestion_simple <task_id> <date>

# S3 içeriği
mc ls minio/bronze/yellow_tripdata_partitioned_by_day/
```

---

**Not**: Bu DAG development ortamında test edilmiştir. Production kullanımı için güvenlik ve monitoring iyileştirmeleri yapılması önerilir.