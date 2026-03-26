"""
API 模块初始化
"""
from api.routes import router
from api.schemas import (
    DeviceHealthReportCreate,
    DeviceHealthReportUpdate,
    DeviceHealthReportResponse,
    DeviceHealthReportListResponse
)

__all__ = ['router', 'DeviceHealthReportCreate', 'DeviceHealthReportUpdate', 
           'DeviceHealthReportResponse', 'DeviceHealthReportListResponse']
