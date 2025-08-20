from fastapi import FastAPI
from database import init_db
from routers import coupon_templates, coupons, reports
from fastapi.middleware.cors import CORSMiddleware # 新增CORS

app = FastAPI(
    title="券管家 SaaS API",
    description="为中小型零售商提供智能优惠券创建、管理、核销和数据分析功能。",
    version="0.1.0"
)

# 新增CORS中间件以允许前端请求，在开发阶段通常设为允许所有来源
origins = [
    "http://localhost",
    "http://localhost:8000", # 后端默认端口
    "http://localhost:3000", # 常见前端开发端口
    "http://localhost:8080", # 常见前端开发端口
    "http://127.0.0.1:8000"
    # 未来部署后，这里需要添加您的前端域名
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # 允许所有HTTP方法
    allow_headers=["*"], # 允许所有头部
)


# 在应用启动时初始化数据库
@app.on_event("startup")
def on_startup():
    init_db()

# 注册路由器
app.include_router(coupon_templates.router, prefix="/api")
app.include_router(coupons.router, prefix="/api")
app.include_router(reports.router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Welcome to 券管家 SaaS API!"}

