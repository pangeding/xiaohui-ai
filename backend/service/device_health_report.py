"""
设备健康报告服务层
提供业务逻辑处理
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from db.models import DeviceHealthReport
from peewee import DoesNotExist


class DeviceHealthReportService:
    """设备健康报告服务类"""
    
    @staticmethod
    def create(
        device_health_report_id: int,
        device_id: int,
        customer_id: int,
        business_id: int,
        report_id: str,
        health_report: Optional[Dict] = None,
        report_type: int = 1,
        report_date: str = '',
        report_status: str = 'INIT',
        parameter: str = ''
    ) -> DeviceHealthReport:
        """
        创建设备健康报告
        
        Args:
            device_health_report_id: 健康报告 ID
            device_id: 设备 ID
            customer_id: 客户 ID
            business_id: 服务方 ID
            report_id: 报告 ID
            health_report: 健康报告数据 (JSON)
            report_type: 报告类型
            report_date: 报告日期
            report_status: 报告状态
            parameter: 相关参数
            
        Returns:
            DeviceHealthReport: 创建的报告对象
        """
        return DeviceHealthReport.create(
            device_health_report_id=device_health_report_id,
            device_id=device_id,
            customer_id=customer_id,
            business_id=business_id,
            report_id=report_id,
            health_report=health_report,
            report_type=report_type,
            report_date=report_date,
            report_status=report_status,
            parameter=parameter
        )
    
    @staticmethod
    def get_by_id(report_id: int) -> Optional[DeviceHealthReport]:
        """
        根据 ID 获取报告
        
        Args:
            report_id: 报告 ID
            
        Returns:
            Optional[DeviceHealthReport]: 报告对象，不存在则返回 None
        """
        try:
            return DeviceHealthReport.get(DeviceHealthReport.id == report_id)
        except DoesNotExist:
            return None
    
    @staticmethod
    def get_by_device_health_report_id(device_health_report_id: int) -> Optional[DeviceHealthReport]:
        """
        根据业务主键获取报告
        
        Args:
            device_health_report_id: 健康报告 ID
            
        Returns:
            Optional[DeviceHealthReport]: 报告对象，不存在则返回 None
        """
        try:
            return DeviceHealthReport.get(DeviceHealthReport.device_health_report_id == device_health_report_id)
        except DoesNotExist:
            return None
    
    @staticmethod
    def get_by_device_id(device_id: int) -> List[DeviceHealthReport]:
        """
        根据设备 ID 获取报告列表
        
        Args:
            device_id: 设备 ID
            
        Returns:
            List[DeviceHealthReport]: 报告列表
        """
        return list(DeviceHealthReport.select().where(DeviceHealthReport.device_id == device_id))
    
    @staticmethod
    def get_by_customer_id(customer_id: int) -> List[DeviceHealthReport]:
        """
        根据客户 ID 获取报告列表
        
        Args:
            customer_id: 客户 ID
            
        Returns:
            List[DeviceHealthReport]: 报告列表
        """
        return list(DeviceHealthReport.select().where(DeviceHealthReport.customer_id == customer_id))
    
    @staticmethod
    def get_by_date_range(device_id: int, start_date: str, end_date: str) -> List[DeviceHealthReport]:
        """
        根据日期范围获取报告
        
        Args:
            device_id: 设备 ID
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            List[DeviceHealthReport]: 报告列表
        """
        return list(DeviceHealthReport.select().where(
            (DeviceHealthReport.device_id == device_id) &
            (DeviceHealthReport.report_date >= start_date) &
            (DeviceHealthReport.report_date <= end_date)
        ))
    
    @staticmethod
    def update(
        report_id: int,
        **kwargs
    ) -> Optional[DeviceHealthReport]:
        """
        更新报告信息
        
        Args:
            report_id: 报告 ID
            **kwargs: 需要更新的字段
            
        Returns:
            Optional[DeviceHealthReport]: 更新后的报告对象，不存在则返回 None
        """
        report = DeviceHealthReportService.get_by_id(report_id)
        if not report:
            return None
        
        # 过滤无效字段
        valid_fields = [
            'device_health_report_id', 'device_id', 'customer_id', 
            'business_id', 'report_id', 'health_report', 'report_type',
            'report_date', 'report_status', 'parameter'
        ]
        
        for key, value in kwargs.items():
            if key in valid_fields and hasattr(report, key):
                setattr(report, key, value)
        
        report.update_time = datetime.now()
        report.save()
        return report
    
    @staticmethod
    def delete(report_id: int) -> bool:
        """
        删除报告（软删除，设置 delete_flag）
        
        Args:
            report_id: 报告 ID
            
        Returns:
            bool: 是否删除成功
        """
        report = DeviceHealthReportService.get_by_id(report_id)
        if not report:
            return False
        
        report.delete_flag = 1
        report.update_time = datetime.now()
        report.save()
        return True
    
    @staticmethod
    def hard_delete(report_id: int) -> bool:
        """
        物理删除报告
        
        Args:
            report_id: 报告 ID
            
        Returns:
            bool: 是否删除成功
        """
        report = DeviceHealthReportService.get_by_id(report_id)
        if not report:
            return False
        
        report.delete_instance()
        return True
    
    @staticmethod
    def get_list(
        page: int = 1,
        page_size: int = 10,
        device_id: Optional[int] = None,
        customer_id: Optional[int] = None,
        report_type: Optional[int] = None,
        report_status: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        分页获取报告列表
        
        Args:
            page: 页码
            page_size: 每页数量
            device_id: 设备 ID（可选过滤条件）
            customer_id: 客户 ID（可选过滤条件）
            report_type: 报告类型（可选过滤条件）
            report_status: 报告状态（可选过滤条件）
            
        Returns:
            Dict[str, Any]: 包含列表和总数的字典
        """
        query = DeviceHealthReport.select()
        
        # 添加过滤条件
        if device_id is not None:
            query = query.where(DeviceHealthReport.device_id == device_id)
        if customer_id is not None:
            query = query.where(DeviceHealthReport.customer_id == customer_id)
        if report_type is not None:
            query = query.where(DeviceHealthReport.report_type == report_type)
        if report_status is not None:
            query = query.where(DeviceHealthReport.report_status == report_status)
        
        # 获取总数
        total = query.count()
        
        # 分页查询
        reports = query.order_by(DeviceHealthReport.create_time.desc()).paginate(page, page_size)
        
        return {
            'list': [report.to_dict() for report in reports],
            'total': total,
            'page': page,
            'page_size': page_size
        }
