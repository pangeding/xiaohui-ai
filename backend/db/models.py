"""
数据模型定义
"""
from peewee import Model, BigIntegerField, IntegerField, CharField, DateTimeField, SQL
from playhouse.mysql_ext import JSONField
from datetime import datetime
from db import db

class BaseModel(Model):
    """基础模型类"""
    
    class Meta:
        database = db

class DeviceHealthReport(BaseModel):
    """设备健康报告模型"""
    
    # 主键
    id = BigIntegerField(primary_key=True, help_text='ID Id')
    
    # 业务字段
    device_health_report_id = BigIntegerField(default=0, help_text='健康报告 Id')
    device_id = BigIntegerField(default=0, help_text='设备 id_逻辑主键')
    customer_id = BigIntegerField(default=0, help_text='客户 id')
    business_id = BigIntegerField(default=0, help_text='服务方_id')
    report_id = CharField(max_length=50, default='0', help_text='报告 id')
    health_report = JSONField(null=True, help_text='设备健康报告信息')
    
    # 报告类型和状态
    report_type = IntegerField(default=1, null=True, help_text='报告类型 1-睡小宝睡眠报告 2-睡小宝生理报告 3-心晓健康报告 4-唉微手表健康报告')
    report_date = CharField(max_length=50, default='', help_text='报告日期')
    report_status = CharField(max_length=10, default='', help_text='报告状态 INIT: 初始')
    parameter = CharField(max_length=300, default='', help_text='相关参数')
    
    # 删除标志
    delete_flag = BigIntegerField(default=0, help_text='删除标志 不启用，用历史表')
    
    # 时间字段
    create_time = DateTimeField(default=datetime.now, help_text='创建时间')
    update_time = DateTimeField(default=datetime.now, help_text='更新时间')
    
    class Meta:
        table_name = 'device_health_report'
        indexes = (
            (('device_health_report_id',), True),  # 唯一索引
            (('customer_id',), False),
            (('device_id',), False),
            (('report_date', 'device_id'), False),  # 联合索引
            (('parameter',), False),
            (('report_id',), False),
        )
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'device_health_report_id': self.device_health_report_id,
            'device_id': self.device_id,
            'customer_id': self.customer_id,
            'business_id': self.business_id,
            'report_id': self.report_id,
            'health_report': self.health_report,
            'report_type': self.report_type,
            'report_date': self.report_date,
            'report_status': self.report_status,
            'parameter': self.parameter,
            'delete_flag': self.delete_flag,
            'create_time': self.create_time.isoformat() if self.create_time else None,
            'update_time': self.update_time.isoformat() if self.update_time else None,
        }
