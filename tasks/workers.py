# tasks/workers.py

import numpy as np
import base64
import os
import tempfile
from celery import Celery
from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks

# 初始化 Celery 应用
app = Celery('workers', broker='redis://localhost:6379/0')

# 添加 Result Backend 配置（使用 Redis）
app.conf.update(
    result_backend='redis://localhost:6379/0',
    task_default_queue='default',
)

# 初始化模型（仅在 Worker 节点上执行）
try:
    product_embedding = pipeline(
        task=Tasks.product_retrieval_embedding,
        model='damo/cv_resnet50_product-bag-embedding-models'
    )
except Exception as e:
    product_embedding = None
    print(f"模型初始化失败: {e}")

@app.task(name='workers.generate_embeddings_task')
def generate_embeddings_task(img_data_b64):
    if product_embedding is None:
        raise RuntimeError("模型未正确初始化（请检查是否已安装 modelscope 并能访问模型）")
    try:
        img_data = base64.b64decode(img_data_b64)
        with tempfile.NamedTemporaryFile(delete=False) as tmpfile:
            tmpfile.write(img_data)
            tmpfile.flush()
            tmp_path = tmpfile.name
        result = product_embedding(tmp_path)
        return np.array(result['img_embedding'], dtype='float32').reshape(1, -1).tolist()
    except Exception as e:
        print(f"生成嵌入失败: {e}")
        raise
    finally:
        os.unlink(tmp_path)