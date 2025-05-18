import numpy as np
from celery import Celery
from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks
import base64
import tempfile
import os

app = Celery('tasks', broker='redis://localhost:6379/0')

try:
    product_embedding = pipeline(
        Tasks.product_retrieval_embedding,
        model='damo/cv_resnet50_product-bag-embedding-models'
    )
except Exception as e:
    product_embedding = None
    print(f"模型初始化失败: {e}")

@app.task(autoretry_for=(Exception,), retry_kwargs={'max_retries': 3})
def generate_embeddings_task(img_data_b64):
    if product_embedding is None:
        raise RuntimeError("模型未正确初始化")
    img_data = base64.b64decode(img_data_b64)
    with tempfile.NamedTemporaryFile(delete=False) as tmpfile:
        tmpfile.write(img_data)
        tmpfile.flush()
        tmp_path = tmpfile.name
    try:
        result = product_embedding(tmp_path)
        embedding = np.array(result['img_embedding'], dtype='float32').reshape(1, -1)
        return embedding.tolist()
    finally:
        os.unlink(tmp_path)