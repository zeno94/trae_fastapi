from datetime import datetime
from fastapi import FastAPI
from pydantic import BaseModel
from loguru import logger

app = FastAPI(title="Greeting Service", version="1.0")

# 结构化日志配置
logger.add(lambda msg: print(msg, end=""), format="{time} | {level} | {message}", level="INFO")


class GreetResponse(BaseModel):
    message: str
    timestamp: str


@app.get("/")
def root():
    return {"message": "Welcome to Greeting Service", "docs": "/docs"}


@app.get("/greet/{name}", response_model=GreetResponse)
def greet(name: str):
    hour = datetime.now().hour
    if 6 <= hour < 18:
        msg = f"早安，{name}"
    else:
        msg = f"晚安，{name}"
    logger.info(f"Greeted {name}")
    return GreetResponse(message=msg, timestamp=datetime.now().isoformat())


@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/hello")
def hello():
    return {"msg": "Hello from PR!"}

# Prometheus 监控（可选，如果不安装该库可注释）
# instrumentator = prometheus_fastapi_instrumentator.Instrumentator()
# instrumentator.instrument(app).expose(app)
