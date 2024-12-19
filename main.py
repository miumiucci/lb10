import os
import time
import psutil
from prometheus_client import start_http_server, Gauge
from dotenv import load_dotenv

# Загрузка переменных окружения из файла .env
load_dotenv()

# Читаем переменные окружения, если не найдены – берем значения по умолчанию
exporter_host = os.environ.get('EXPORTER_HOST', '0.0.0.0')
exporter_port = int(os.environ.get('EXPORTER_PORT', '8000'))

# Создаем метрики
cpu_usage_gauges = []
num_cores = psutil.cpu_count(logical=True)
for i in range(num_cores):
    g = Gauge(f'cpu_core_{i}_usage_percent', f'CPU usage percentage for core {i}')
    cpu_usage_gauges.append(g)

memory_total_gauge = Gauge('memory_total_bytes', 'Total memory in bytes')
memory_used_gauge = Gauge('memory_used_bytes', 'Used memory in bytes')

disk_total_gauge = Gauge('disk_total_bytes', 'Total disk size in bytes')
disk_used_gauge = Gauge('disk_used_bytes', 'Used disk size in bytes')


def collect_metrics():
    # CPU usage
    cpu_usages = psutil.cpu_percent(interval=1, percpu=True)
    for i, usage in enumerate(cpu_usages):
        cpu_usage_gauges[i].set(usage)

    # Memory info
    mem = psutil.virtual_memory()
    memory_total_gauge.set(mem.total)
    memory_used_gauge.set(mem.used)

    # Disk info
    disk = psutil.disk_usage('/')
    disk_total_gauge.set(disk.total)
    disk_used_gauge.set(disk.used)


if __name__ == '__main__':
    # Запускаем HTTP-сервер с метриками
    # По умолчанию prometheus_client отдаёт метрики по /metrics
    # Задание требует отдавать метрики на корневом пути /.
    # Для этого нужно создать свой HTTP-сервер. Пример:
    from prometheus_client import make_wsgi_app
    from wsgiref.simple_server import make_server

    app = make_wsgi_app()

    # При желании можно сделать так, чтобы корневой путь / отдавал те же данные, что и /metrics:
    # Для этого достаточно не использовать отдельный путь, т.к. make_wsgi_app по умолчанию /metrics отдаёт на /
    # Но по умолчанию make_wsgi_app делает /metrics. Для строгости можно просто переопределить роутинг.
    # Самый простой вариант: Prometheus умеет скрапить метрики по /metrics. Если лаба строго требует '/', можно:
    # - Патчить маршруты или
    # - Поднять собственный HTTPServer, который всегда возвращает результаты make_wsgi_app().
    # Например:
    # httpd = make_server(exporter_host, exporter_port, app)
    # httpd.serve_forever()

    # Если требуется именно '/', то можно сделать простой подход:
    # Но make_wsgi_app отдает метрики на /metrics, а не на /. Если задание строго это требует,
    # придется использовать другую библиотеку или вручную написать обработчик.
    # Ниже пример с ручным обработчиком (минимальный):

    from wsgiref.simple_server import make_server


    def simple_app(environ, start_response):
        if environ['PATH_INFO'] == '/':
            # Возвращаем метрики из make_wsgi_app() при запросе на '/'
            status, headers, body = '200 OK', [('Content-Type', 'text/plain')], []
            # make_wsgi_app возвращает WSGI-приложение. Можно вызвать его вручную:
            # Но удобнее переопределить PATH_INFO на /metrics:
            environ['PATH_INFO'] = '/metrics'
            return app(environ, start_response)
        else:
            # Любой другой путь – 404
            start_response('404 Not Found', [('Content-Type', 'text/plain')])
            return [b'Not Found']


    # Запускаем сервер:
    httpd = make_server(exporter_host, exporter_port, simple_app)
    print(f"Exporter is running on http://{exporter_host}:{exporter_port}/")


    # Периодически собираем метрики
    def loop_collect():
        while True:
            collect_metrics()
            time.sleep(5)


    # Запускаем сбор метрик в фоне
    import threading

    threading.Thread(target=loop_collect, daemon=True).start()

    # Запускаем сервер в основном потоке
    httpd.serve_forever()
