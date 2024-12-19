# Лабораторная работа №10. Time Series база данных Prometheus

## Требования
- **Python 3.11**
- **Prometheus**
- Установленные зависимости (указаны в `requirements.txt`):
  - prometheus_client
  - psutil
  - python-dotenv

## Установка

1. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   
2. Настройте переменные окружения в файле .env (если требуется):
- EXPORTER_HOST=0.0.0.0
- EXPORTER_PORT=8000

3. Добавьте экспортер в конфигурацию Prometheus: В файле prometheus.yml добавьте следующее в секцию scrape_configs:
   ```bash
   - job_name: 'my_exporter'
     metrics_path: '/'
     static_configs:
       - targets: ['localhost:8000']
4. Перезапустите Prometheus:
   ```bash
   systemctl restart prometheus
5. Запустите экспортер:
   ```bash
   python main.py
6. Откройте приложение
   ```bash
   http://localhost:8000/

# Примеры PromQL-запросов

1. Использование процессоров:
- Для конкретного ядра
   ```bash
  cpu_core_0_usage_percent
- Среднее использование всех ядер:
   ```bash
  avg({__name__=~"cpu_core_.*_usage_percent"})

2. Память:
- Общий объём памяти:
   ```bash
  memory_total_bytes
- Используемая память:
   ```bash
  memory_used_bytes

3. Диск:
- Общий объём диска:
   ```bash
  disk_total_bytes

- Используемое дисковое пространство:
   ```bash
  disk_used_bytes

 
