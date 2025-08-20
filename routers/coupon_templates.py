from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
import crud, schemas

router = APIRouter(
    prefix="/coupon_templates",
    tags=["Coupon Templates"],
)

@router.post("/", response_model=schemas.CouponTemplateResponse, status_code=status.HTTP_201_CREATED)
def create_template(template: schemas.CouponTemplateCreate, db: Session = Depends(get_db)):
    """
    创建新的优惠券模板，并生成对应数量的优惠码。
    """
    return crud.create_coupon_template(db=db, template=template)

@router.get("/", response_model=List[schemas.CouponTemplateResponse])
def read_templates(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    获取所有优惠券模板列表。
    """
    templates = crud.get_coupon_templates(db=db, skip=skip, limit=limit)
    return templates

@router.get("/{template_id}", response_model=schemas.CouponTemplateResponse)
def read_template(template_id: int, db: Session = Depends(get_db)):
    """
    获取单个优惠券模板详情。
    """
    db_template = crud.get_coupon_template(db=db, template_id=template_id)
    if db_template is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Coupon template not found")
    return db_template

@router.put("/{template_id}", response_model=schemas.CouponTemplateResponse)
def update_template(template_id: int, template: schemas.CouponTemplateUpdate, db: Session = Depends(get_db)):
    """
    更新优惠券模板信息。
    """
    db_template = crud.update_coupon_template(db=db, template_id=template_id, template_update=template)
    if not db_template:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Coupon template not found")
    return db_template

@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_template(template_id: int, db: Session = Depends(get_db)):
    """
    删除优惠券模板（以及其关联的优惠码实例）。
    """
    if not crud.delete_coupon_template(db=db, template_id=template_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Coupon template not found")
    return {"ok": True}
