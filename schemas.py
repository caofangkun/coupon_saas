from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from models import CouponType, CouponStatus

# 用于请求体 (Request Body)
class CouponTemplateCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    coupon_type: CouponType
    value: float = Field(..., gt=0, description="优惠价值 (百分比或金额)")
    min_spend: float = Field(0.0, ge=0, description="最低消费金额")
    start_time: datetime
    end_time: datetime
    total_quantity: int = Field(0, ge=0, description="总发行数量")
    per_user_limit: int = Field(1, ge=1, description="每用户领取限制")
    is_stackable: bool = False

class CouponTemplateUpdate(BaseModel):
    name: Optional[str] = None
    coupon_type: Optional[CouponType] = None
    value: Optional[float] = None
    min_spend: Optional[float] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    total_quantity: Optional[int] = None
    per_user_limit: Optional[int] = None
    status: Optional[CouponStatus] = None # 允许更新模板状态
    is_stackable: Optional[bool] = None

class CouponRedeemRequest(BaseModel):
    coupon_code: str = Field(..., min_length=4, max_length=20) # 优惠码
    # user_id: Optional[str] = None # 未来可用于核查用户领取限制（MVP不实现）
    # order_amount: Optional[float] = None # 未来可用于核查最低消费金额（MVP核销时不强制传入，在前端提示）

# 用于响应体 (Response Body)
class CouponTemplateResponse(BaseModel):
    id: int
    name: str
    coupon_type: CouponType
    value: float
    min_spend: float
    start_time: datetime
    end_time: datetime
    total_quantity: int
    claimed_quantity: int # 尽管MVP不执行领取，但作为数据库字段保留
    redeemed_quantity: int
    per_user_limit: int
    status: CouponStatus
    created_at: datetime
    updated_at: datetime
    is_stackable: bool

    class Config:
        orm_mode = True # 允许从ORM对象直接创建Pydantic模型

class CouponResponse(BaseModel):
    id: int
    coupon_code: str
    template_id: int
    status: CouponStatus
    redeemed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class RedemptionReportResponse(BaseModel):
    template_id: int
    template_name: str
    total_generated: int
    total_redeemed: int
    redeem_rate: float # 核销率
    # 可添加按时间维度的数据

class DailyRedemptionSummary(BaseModel):
    date: str
    redeem_count: int
    
class RedemptionTrendsResponse(BaseModel):
    total_redeemed_today: int
    total_active_coupons: int
    daily_trend: list[DailyRedemptionSummary] # 按天统计的核销数量
