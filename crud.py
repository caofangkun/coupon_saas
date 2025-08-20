from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Date
from datetime import datetime, timedelta
import random
import string

from models import CouponTemplate, Coupon, CouponStatus, CouponType
from schemas import CouponTemplateCreate, CouponTemplateUpdate

# --- Coupon Template CRUD ---
def create_coupon_template(db: Session, template: CouponTemplateCreate):
    db_template = CouponTemplate(**template.dict())
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    # 立即生成对应的优惠码实例
    generate_coupons_for_template(db, db_template)
    return db_template

def get_coupon_templates(db: Session, skip: int = 0, limit: int = 100):
    return db.query(CouponTemplate).offset(skip).limit(limit).all()

def get_coupon_template(db: Session, template_id: int):
    return db.query(CouponTemplate).filter(CouponTemplate.id == template_id).first()

def update_coupon_template(db: Session, template_id: int, template_update: CouponTemplateUpdate):
    db_template = db.query(CouponTemplate).filter(CouponTemplate.id == template_id).first()
    if not db_template:
        return None
    for key, value in template_update.dict(exclude_unset=True).items():
        setattr(db_template, key, value)
    db_template.updated_at = func.now()
    db.commit()
    db.refresh(db_template)
    return db_template

def delete_coupon_template(db: Session, template_id: int):
    db_template = db.query(CouponTemplate).filter(CouponTemplate.id == template_id).first()
    if db_template:
        # 软删除 (如果需要，可改为更新状态为 'deleted')
        db.delete(db_template)
        db.commit()
        return True
    return False

# --- Coupon (instance) Generation ---
def generate_unique_coupon_code(length=12):
    """生成一个随机的、唯一的优惠码"""
    characters = string.ascii_uppercase + string.digits
    while True:
        code = ''.join(random.choice(characters) for i in range(length))
        # 在实际应用中，这里需要检查数据库中是否已存在，但SQLite简单应用可先忽略重复码可能性
        # 如果是生产环境，这里需要添加从数据库查询验证码是否唯一的逻辑
        return code

def generate_coupons_for_template(db: Session, template: CouponTemplate):
    """为新创建的优惠券模板生成对应的优惠码实例"""
    # 假设每次创建模板都生成所有指定数量的优惠码
    existing_coupons_count = db.query(Coupon).filter(Coupon.template_id == template.id).count()
    
    # 确保不会生成超过总数量的码，或者已有的不再重新生成
    num_to_generate = template.total_quantity - existing_coupons_count
    
    if num_to_generate <= 0:
        return []

    new_coupons = []
    for _ in range(num_to_generate):
        coupon_code = generate_unique_coupon_code()
        db_coupon = Coupon(
            coupon_code=coupon_code,
            template_id=template.id,
            status=CouponStatus.active # 初始状态为活跃
        )
        new_coupons.append(db_coupon)
        db.add(db_coupon)
    
    db.commit()
    for coupon in new_coupons:
        db.refresh(coupon)
    return new_coupons

# --- Coupon Redemption ---
def redeem_coupon(db: Session, coupon_code: str):
    db_coupon = db.query(Coupon).filter(Coupon.coupon_code == coupon_code).first()
    if not db_coupon:
        return None, "优惠码不存在"

    # 获取对应的优惠券模板，检查其状态和有效期
    db_template = db.query(CouponTemplate).filter(CouponTemplate.id == db_coupon.template_id).first()
    if not db_template:
        return None, "对应的优惠券模板不存在"
    
    now = datetime.now()
    if db_template.status != CouponStatus.active:
        return None, "优惠券模板未激活或已暂停"
    if now < db_template.start_time:
        return None, "优惠券尚未生效"
    if now > db_template.end_time:
        return None, "优惠券已过期"
    
    if db_coupon.status == CouponStatus.redeemed:
        return None, "优惠码已被核销"
    if db_coupon.status == CouponStatus.expired: # 理论上上面已过期判断会比这个先触发
        return None, "优惠码已过期"

    # 执行核销
    db_coupon.status = CouponStatus.redeemed
    db_coupon.redeemed_at = func.now()
    db_template.redeemed_quantity += 1 # 更新模板的核销数量
    
    db.commit()
    db.refresh(db_coupon)
    db.refresh(db_template)
    return db_coupon, "核销成功"

# --- Report Generation ---
def get_redemption_stats_by_template(db: Session):
    templates = db.query(CouponTemplate).all()
    results = []
    for t in templates:
        redeem_rate = (t.redeemed_quantity / t.total_quantity * 100) if t.total_quantity > 0 else 0
        results.append({
            "template_id": t.id,
            "template_name": t.name,
            "total_generated": t.total_quantity, # 在MVP中，相当于已发行的数量
            "total_redeemed": t.redeemed_quantity,
            "redeem_rate": round(redeem_rate, 2)
        })
    return results

def get_daily_redeem_trends(db: Session, days_ago: int = 7):
    """获取过去X天的每日核销趋势"""
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days_ago)

    trends = (
        db.query(
            cast(Coupon.redeemed_at, Date).label("date"),
            func.count(Coupon.id).label("redeem_count")
        )
        .filter(Coupon.status == CouponStatus.redeemed, Coupon.redeemed_at.between(start_date, end_date))
        .group_by(cast(Coupon.redeemed_at, Date))
        .order_by(cast(Coupon.redeemed_at, Date))
        .all()
    )

    result = []
    current_date = start_date
    trend_map = {str(r.date): r.redeem_count for r in trends}

    while current_date <= end_date:
        date_str = current_date.isoformat()
        result.append({"date": date_str, "redeem_count": trend_map.get(date_str, 0)})
        current_date += timedelta(days=1)
    
    return result

def get_dashboard_summary(db: Session):
    total_active_templates = db.query(CouponTemplate).filter(CouponTemplate.status == CouponStatus.active).count()
    
    one_month_ago = datetime.now() - timedelta(days=30)
    monthly_redeemed = db.query(Coupon).filter(
        Coupon.status == CouponStatus.redeemed,
        Coupon.redeemed_at >= one_month_ago
    ).count()

    # 获取过去7天的核销趋势
    daily_trend_data = get_daily_redeem_trends(db, days_ago=6) # 包含今天在内的7天

    return {
        "active_coupon_templates_count": total_active_templates,
        "monthly_redeemed_count": monthly_redeemed,
        "daily_redeem_trends": daily_trend_data
    }
