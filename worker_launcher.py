# worker_launcher.py

from celery import Celery
from celery.bin import worker as celery_worker

# 初始化 Celery 应用
app = Celery('workers', broker='redis://localhost:6379/0')

# 加载任务模块
app.config_from_object('tasks.workers')

# 启动 Worker
if __name__ == '__main__':
    celery_worker.worker(app=app).run(
        loglevel='INFO',
        concurrency=4,
        pool='prefork'
    )