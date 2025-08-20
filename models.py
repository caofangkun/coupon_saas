from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import enum

Base = declarative_base()

class CouponType(enum.Enum):
    percentage_discount = "percentage_discount" # 百分比折扣
    fixed_amount_discount = "fixed_amount_discount" # 固定金额折扣
    full_reduction = "full_reduction" # 满减
    new_user_exclusive = "new_user_exclusive" # 新人专享

class CouponStatus(enum.Enum):
    active = "active"
    paused = "paused"
    expired = "expired"
    redeemed = "redeemed" # 仅针对单个优惠码，模板状态为 active/paused/expired

class CouponTemplate(Base):
    __tablename__ = "coupon_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, comment="优惠券模板名称")
    coupon_type = Column(Enum(CouponType), comment="优惠券类型")
    value = Column(Float, comment="优惠价值 (百分比或金额)") # 例如，0.8 (8折) 或 10.0 (满减10元)
    min_spend = Column(Float, default=0.0, comment="最低消费金额")
    start_time = Column(DateTime(timezone=True), default=func.now(), comment="生效开始时间")
    end_time = Column(DateTime(timezone=True), comment="生效结束时间")
    total_quantity = Column(Integer, default=0, comment="总发行数量")
    claimed_quantity = Column(Integer, default=0, comment="已领取数量") # MVP暂不实现领取功能，直接发券
    redeemed_quantity = Column(Integer, default=0, comment="已核销数量")
    per_user_limit = Column(Integer, default=1, comment="每用户领取限制")
    status = Column(Enum(CouponStatus), default=CouponStatus.active, comment="模板状态")
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    is_stackable = Column(Boolean, default=False, comment="是否可叠加使用") # MVP暂不实现此逻辑

class Coupon(Base):
    __tablename__ = "coupons"

    id = Column(Integer, primary_key=True, index=True)
    coupon_code = Column(String, unique=True, index=True, comment="优惠码")
    template_id = Column(Integer, index=True, comment="引用的优惠券模板ID")
    status = Column(Enum(CouponStatus), default=CouponStatus.active, comment="优惠码实例状态") # active, redeemed, expired
    redeemed_at = Column(DateTime(timezone=True), nullable=True, comment="核销时间")
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
