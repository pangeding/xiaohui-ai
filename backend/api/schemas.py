"""
Pydantic 模型定义 - 用于请求和响应验证
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class DeviceHealthReportBase(BaseModel):
    """设备健康报告基础模型"""
    
    device_id: int = Field(default=0, description="设备 ID")
    customer_id: int = Field(default=0, description="客户 ID")
    business_id: int = Field(default=0, description="服务方 ID")
    report_id: str = Field(default='0', max_length=50, description="报告 ID")
    health_report: Optional[Dict[str, Any]] = Field(default=None, description="健康报告数据")
    report_type: Optional[int] = Field(default=1, description="报告类型：1-睡小宝睡眠报告 2-睡小宝生理报告 3-心晓健康报告 4-唉微手表健康报告")
    report_date: Optional[str] = Field(default='', max_length=50, description="报告日期")
    report_status: Optional[str] = Field(default='INIT', max_length=10, description="报告状态")
    parameter: Optional[str] = Field(default='', max_length=300, description="相关参数")


class DeviceHealthReportCreate(DeviceHealthReportBase):
    """创建设备健康报告请求模型"""
    
    device_health_report_id: int = Field(default=0, description="健康报告 ID")


class DeviceHealthReportUpdate(BaseModel):
    """更新设备健康报告请求模型"""
    
    device_id: Optional[int] = Field(default=None, description="设备 ID")
    customer_id: Optional[int] = Field(default=None, description="客户 ID")
    business_id: Optional[int] = Field(default=None, description="服务方 ID")
    report_id: Optional[str] = Field(default=None, max_length=50, description="报告 ID")
    health_report: Optional[Dict[str, Any]] = Field(default=None, description="健康报告数据")
    report_type: Optional[int] = Field(default=None, description="报告类型")
    report_date: Optional[str] = Field(default=None, max_length=50, description="报告日期")
    report_status: Optional[str] = Field(default=None, max_length=10, description="报告状态")
    parameter: Optional[str] = Field(default=None, max_length=300, description="相关参数")


class DeviceHealthReportResponse(DeviceHealthReportBase):
    """设备健康报告响应模型"""
    
    id: int = Field(description="ID")
    device_health_report_id: int = Field(description="健康报告 ID")
    delete_flag: int = Field(default=0, description="删除标志")
    create_time: datetime = Field(description="创建时间")
    update_time: datetime = Field(description="更新时间")
    
    class Config:
        from_attributes = True


class DeviceHealthReportListResponse(BaseModel):
    """设备健康报告列表响应模型"""
    
    items: List[DeviceHealthReportResponse] = Field(description="报告列表")
    total: int = Field(description="总数")
    page: int = Field(description="当前页码")
    page_size: int = Field(description="每页数量")
