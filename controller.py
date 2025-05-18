# controller.py

import os
import base64
import numpy as np
import faiss
from tasks.interfaces import generate_embeddings_task

# 初始化 FAISS 索引
dimension = 512
index = faiss.IndexFlatL2(dimension)
id_map = {}

# 数据集路径
base_dir = os.path.join(os.path.dirname(__file__), 'datasets')
img_exts = ('.jpg', '.jpeg', '.png', '.bmp')
db_img_paths = [
    os.path.join(base_dir, fname)
    for fname in os.listdir(base_dir)
    if fname.lower().endswith(img_exts) and fname != 'query.jpg'
]

# 分发任务并构建索引
task_futures = []
for idx, path in enumerate(db_img_paths):
    with open(path, 'rb') as f:
        img_data = f.read()
    img_data_b64 = base64.b64encode(img_data).decode('utf-8')
    future = generate_embeddings_task.delay(img_data_b64)
    task_futures.append((idx, path, future))

# 收集结果并构建索引
for idx, path, future in task_futures:
    try:
        embedding_list = future.get(timeout=30)
        embedding = np.array(embedding_list, dtype='float32')
        index.add(embedding)
        id_map[idx] = path
    except Exception as e:
        print(f"处理图片 {path} 时发生错误: {e}")

# 查询函数
def search_image(query_img_path, topk=3):
    with open(query_img_path, 'rb') as f:
        img_data = f.read()
    img_data_b64 = base64.b64encode(img_data).decode('utf-8')
    future = generate_embeddings_task.delay(img_data_b64)
    try:
        embedding_list = future.get(timeout=30)
        query_embedding = np.array(embedding_list, dtype='float32')
        D, I = index.search(query_embedding, k=topk)
        results = [id_map.get(int(i), 'Unknown') for i in I[0]]
        return results
    except Exception as e:
        print(f"生成查询嵌入失败: {e}")
        return []

if __name__ == '__main__':
    query_path = os.path.join(base_dir, 'query.jpg')
    if not os.path.exists(query_path):
        print("未找到查询图片 datasets/query.jpg，程序退出。")
        exit(0)
    result = search_image(query_path, topk=3)
    print('检索结果:', result)