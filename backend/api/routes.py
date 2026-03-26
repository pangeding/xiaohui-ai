"""
设备健康报告 API 路由
"""
from fastapi import APIRouter, HTTPException, Query, Path
from typing import Optional, List
from api.schemas import (
    DeviceHealthReportCreate,
    DeviceHealthReportUpdate,
    DeviceHealthReportResponse,
    DeviceHealthReportListResponse
)
from service.device_health_report import DeviceHealthReportService

router = APIRouter(prefix="/device-health-reports", tags=["设备健康报告"])


@router.post("", response_model=DeviceHealthReportResponse, summary="创建设备健康报告")
async def create_device_health_report(report: DeviceHealthReportCreate):
    """
    创建新的设备健康报告
    
    - **device_health_report_id**: 健康报告 ID（业务主键）
    - **device_id**: 设备 ID
    - **customer_id**: 客户 ID
    - **business_id**: 服务方 ID
    - **report_id**: 报告 ID
    - **health_report**: 健康报告数据（JSON 格式）
    - **report_type**: 报告类型
    - **report_date**: 报告日期
    - **report_status**: 报告状态
    - **parameter**: 相关参数
    """
    try:
        db_report = DeviceHealthReportService.create(
            device_health_report_id=report.device_health_report_id,
            device_id=report.device_id,
            customer_id=report.customer_id,
            business_id=report.business_id,
            report_id=report.report_id,
            health_report=report.health_report,
            report_type=report.report_type,
            report_date=report.report_date,
            report_status=report.report_status,
            parameter=report.parameter
        )
        return DeviceHealthReportResponse.model_validate(db_report)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建失败：{str(e)}")


@router.get("/{report_id}", response_model=DeviceHealthReportResponse, summary="根据 ID 获取报告")
async def get_device_health_report(report_id: int = Path(..., description="报告 ID")):
    """
    根据报告 ID 获取详细信息
    
    - **report_id**: 报告 ID
    """
    report = DeviceHealthReportService.get_by_id(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="报告不存在")
    
    return DeviceHealthReportResponse.model_validate(report)


@router.get("/biz/{device_health_report_id}", response_model=DeviceHealthReportResponse, summary="根据业务 ID 获取报告")
async def get_by_biz_id(device_health_report_id: int = Path(..., description="健康报告 ID")):
    """
    根据业务主键获取报告详情
    
    - **device_health_report_id**: 健康报告 ID（业务主键）
    """
    report = DeviceHealthReportService.get_by_device_health_report_id(device_health_report_id)
    if not report:
        raise HTTPException(status_code=404, detail="报告不存在")
    
    return DeviceHealthReportResponse.model_validate(report)


@router.get("/device/{device_id}", response_model=List[DeviceHealthReportResponse], summary="根据设备 ID 获取报告列表")
async def get_reports_by_device(device_id: int = Path(..., description="设备 ID")):
    """
    根据设备 ID 获取所有报告
    
    - **device_id**: 设备 ID
    """
    reports = DeviceHealthReportService.get_by_device_id(device_id)
    return [DeviceHealthReportResponse.model_validate(report) for report in reports]


@router.get("/customer/{customer_id}", response_model=List[DeviceHealthReportResponse], summary="根据客户 ID 获取报告列表")
async def get_reports_by_customer(customer_id: int = Path(..., description="客户 ID")):
    """
    根据客户 ID 获取所有报告
    
    - **customer_id**: 客户 ID
    """
    reports = DeviceHealthReportService.get_by_customer_id(customer_id)
    return [DeviceHealthReportResponse.model_validate(report) for report in reports]


@router.get("/date-range", response_model=List[DeviceHealthReportResponse], summary="根据日期范围获取报告")
async def get_reports_by_date_range(
    device_id: int = Query(..., description="设备 ID"),
    start_date: str = Query(..., description="开始日期"),
    end_date: str = Query(..., description="结束日期")
):
    """
    根据日期范围查询报告
    
    - **device_id**: 设备 ID
    - **start_date**: 开始日期（格式：YYYY-MM-DD）
    - **end_date**: 结束日期（格式：YYYY-MM-DD）
    """
    reports = DeviceHealthReportService.get_by_date_range(device_id, start_date, end_date)
    return [DeviceHealthReportResponse.model_validate(report) for report in reports]


@router.put("/{report_id}", response_model=DeviceHealthReportResponse, summary="更新报告")
async def update_device_health_report(
    report_id: int = Path(..., description="报告 ID"),
    report: DeviceHealthReportUpdate = None
):
    """
    更新设备健康报告信息
    
    - **report_id**: 报告 ID
    - **device_id**: 设备 ID（可选）
    - **customer_id**: 客户 ID（可选）
    - **business_id**: 服务方 ID（可选）
    - **report_id**: 报告 ID（可选）
    - **health_report**: 健康报告数据（可选）
    - **report_type**: 报告类型（可选）
    - **report_date**: 报告日期（可选）
    - **report_status**: 报告状态（可选）
    - **parameter**: 相关参数（可选）
    """
    updated_report = DeviceHealthReportService.update(report_id, **report.model_dump(exclude_unset=True))
    if not updated_report:
        raise HTTPException(status_code=404, detail="报告不存在")
    
    return DeviceHealthReportResponse.model_validate(updated_report)


@router.delete("/{report_id}", summary="删除报告（软删除）")
async def delete_device_health_report(report_id: int = Path(..., description="报告 ID")):
    """
    软删除设备健康报告（设置 delete_flag=1）
    
    - **report_id**: 报告 ID
    """
    success = DeviceHealthReportService.delete(report_id)
    if not success:
        raise HTTPException(status_code=404, detail="报告不存在")
    
    return {"message": "删除成功"}


@router.delete("/{report_id}/hard", summary="物理删除报告")
async def hard_delete_device_health_report(report_id: int = Path(..., description="报告 ID")):
    """
    物理删除设备健康报告（不可恢复）
    
    - **report_id**: 报告 ID
    """
    success = DeviceHealthReportService.hard_delete(report_id)
    if not success:
        raise HTTPException(status_code=404, detail="报告不存在")
    
    return {"message": "删除成功"}


@router.get("", response_model=DeviceHealthReportListResponse, summary="分页获取报告列表")
async def get_device_health_report_list(
    page: int = Query(default=1, ge=1, description="页码"),
    page_size: int = Query(default=10, ge=1, le=100, description="每页数量"),
    device_id: Optional[int] = Query(default=None, description="设备 ID（过滤条件）"),
    customer_id: Optional[int] = Query(default=None, description="客户 ID（过滤条件）"),
    report_type: Optional[int] = Query(default=None, description="报告类型（过滤条件）"),
    report_status: Optional[str] = Query(default=None, description="报告状态（过滤条件）")
):
    """
    分页查询设备健康报告列表，支持多种过滤条件
    
    - **page**: 页码
    - **page_size**: 每页数量
    - **device_id**: 设备 ID（可选过滤）
    - **customer_id**: 客户 ID（可选过滤）
    - **report_type**: 报告类型（可选过滤）
    - **report_status**: 报告状态（可选过滤）
    """
    result = DeviceHealthReportService.get_list(
        page=page,
        page_size=page_size,
        device_id=device_id,
        customer_id=customer_id,
        report_type=report_type,
        report_status=report_status
    )
    
    return DeviceHealthReportListResponse(**result)
