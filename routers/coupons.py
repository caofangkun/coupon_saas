from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
import crud, schemas

router = APIRouter(
    prefix="/coupons",
    tags=["Coupons"],
)

@router.post("/redeem/", response_model=schemas.CouponResponse)
def redeem_coupon_api(redeem_request: schemas.CouponRedeemRequest, db: Session = Depends(get_db)):
    """
    核销优惠券。根据优惠码进行核销。
    """
    db_coupon, message = crud.redeem_coupon(db=db, coupon_code=redeem_request.coupon_code)
    if not db_coupon:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)
    return db_coupon

# 未来可以添加获取单个优惠码信息等接口，MVP先不实现
