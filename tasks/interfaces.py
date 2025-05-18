# tasks/interfaces.py

from celery import Celery

# 初始化 Celery 应用
app = Celery('interfaces', broker='redis://localhost:6379/0')

# 添加 Result Backend 配置（使用 Redis）
app.conf.update(
    result_backend='redis://localhost:6379/0',
    task_default_queue='default',
)

# 定义任务签名（接口）
generate_embeddings_task = app.signature('workers.generate_embeddings_task')