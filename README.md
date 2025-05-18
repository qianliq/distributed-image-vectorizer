# distributed-image-
### 启动流程

#### 1. 启动 Redis 服务  
```bash
redis-server
```

---

#### 2. 启动 Worker 节点  
在 Worker 节点执行以下命令（支持多个节点并行）：  
```bash
cd distributed-image-vectorizer
celery -A tasks.workers worker --loglevel=info --pool=solo
```

---

#### 3. 运行控制端程序  
在控制端节点执行以下命令：  
```bash
cd distributed-image-vectorizer
python controller.py
```