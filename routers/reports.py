from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from database import get_db
import crud, schemas

router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
)

@router.get("/coupon_template_stats/", response_model=List[schemas.RedemptionReportResponse])
def get_coupon_template_stats(db: Session = Depends(get_db)):
    """
    获取各优惠券模板的领取和核销统计。
    """
    return crud.get_redemption_stats_by_template(db=db)

@router.get("/dashboard_summary/", response_model=schemas.RedemptionTrendsResponse)
def get_dashboard_summary(db: Session = Depends(get_db)):
    """
    获取仪表板概览数据，包括活跃优惠券模板数量、月核销总量和每日核销趋势。
    """
    summary = crud.get_dashboard_summary(db=db)
    # 使用 RedemptionTrendsResponse 作为通用响应模型，虽然名字不太匹配，但包含我们需要的数据
    return schemas.RedemptionTrendsResponse(
        total_redeemed_today=summary['daily_redeem_trends'][-1]['redeem_count'] if summary['daily_redeem_trends'] else 0,
        total_active_coupons=summary['active_coupon_templates_count'],
        daily_trend=summary['daily_redeem_trends']
    )
