### 1. device_health_report

#### 1.1 model

设备健康报告表，用于存储各类设备产生的健康报告数据。

| 字段名 | 类型 | 长度 | 默认值 | 允许 NULL | 注释 |
|--------|------|------|--------|---------|------|
| id | BIGINT UNSIGNED | - | AUTO_INCREMENT | NO | 主键 ID |
| device_health_report_id | BIGINT UNSIGNED | - | 0 | NO | 健康报告 Id（业务主键） |
| device_id | BIGINT UNSIGNED | - | 0 | NO | 设备 Id（逻辑主键） |
| customer_id | BIGINT UNSIGNED | - | 0 | NO | 客户 Id |
| business_id | BIGINT UNSIGNED | - | 0 | NO | 服务方 Id |
| report_id | VARCHAR | 50 | '0' | NO | 报告 Id |
| health_report | JSON | - | NULL | YES | 设备健康报告信息（JSON 格式） |
| report_type | INT | - | 1 | YES | 报告类型：1-睡小宝睡眠报告 2-睡小宝生理报告 3-心晓健康报告 4-唉微手表健康报告 |
| report_date | VARCHAR | 50 | '' | YES | 报告日期 |
| report_status | VARCHAR | 10 | '' | NO | 报告状态：INIT-初始 |
| parameter | VARCHAR | 300 | '' | NO | 相关参数 |
| delete_flag | INT UNSIGNED | - | 0 | NO | 删除标志：不启用，用历史表 |
| create_time | TIMESTAMP | - | CURRENT_TIMESTAMP | NO | 创建时间 |
| update_time | TIMESTAMP | - | CURRENT_TIMESTAMP | NO | 更新时间（自动更新） |

**索引设计：**
- 主键索引：`id`
- 唯一索引：`device_health_report_id`
- 普通索引：`customer_id`, `device_id`, `report_date + device_id` (联合索引), `parameter`, `report_id`

#### 1.2 sql

```mysql
CREATE TABLE `device_health_report` (
	`id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'ID Id',
	`device_health_report_id` BIGINT UNSIGNED NOT NULL DEFAULT '0' COMMENT '健康报告 Id',
	`device_id` BIGINT UNSIGNED NOT NULL DEFAULT '0' COMMENT '设备_id_逻辑主键',
	`customer_id` BIGINT UNSIGNED NOT NULL DEFAULT '0' COMMENT '客户 id',
	`business_id` BIGINT UNSIGNED NOT NULL DEFAULT '0' COMMENT '服务方_id',
	`report_id` VARCHAR(50) NOT NULL DEFAULT '0' COMMENT '报告 id' COLLATE 'utf8mb4_general_ci',
	`health_report` JSON NULL DEFAULT NULL COMMENT '设备健康报告信息',
	`report_type` INT NULL DEFAULT '1' COMMENT '报告类型 1-睡小宝睡眠报告 2-睡小宝生理报告 3-心晓健康报告 4-唉微手表健康报告',
	`report_date` VARCHAR(50) NULL DEFAULT '' COMMENT '报告日期' COLLATE 'utf8mb4_general_ci',
	`report_status` VARCHAR(10) NOT NULL DEFAULT '' COMMENT '报告状态  INIT: 初始' COLLATE 'utf8mb4_general_ci',
	`parameter` VARCHAR(300) NOT NULL DEFAULT '' COMMENT '相关参数' COLLATE 'utf8mb4_general_ci',
	`delete_flag` INT UNSIGNED NOT NULL DEFAULT '0' COMMENT '删除标志 不启用，用历史表',
	`create_time` TIMESTAMP NOT NULL DEFAULT (CURRENT_TIMESTAMP) COMMENT '创建时间',
	`update_time` TIMESTAMP NOT NULL DEFAULT (CURRENT_TIMESTAMP) ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
	PRIMARY KEY (`id`) USING BTREE,
	UNIQUE INDEX `unqi_device_health_report_device_health_report_id` (`device_health_report_id`) USING BTREE,
	INDEX `customer_id` (`customer_id`) USING BTREE,
	INDEX `device_id` (`device_id`) USING BTREE,
	INDEX `idx_report_date_device_id` (`report_date`, `device_id`) USING BTREE,
	INDEX `fk_parameter` (`parameter`) USING BTREE,
	INDEX `fk_report_id` (`report_id`) USING BTREE
)
COMMENT='设备健康报告'
COLLATE='utf8mb4_general_ci'
ENGINE=InnoDB
AUTO_INCREMENT=5473699
;
```

#### 1.3 python peewee example

```python
from peewee import Model, BigIntegerField, IntegerField, CharField, TextField, DateTimeField, SQL
from playhouse.mysql_ext import JSONField
from datetime import datetime

class DeviceHealthReport(Model):
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
    
    @classmethod
    def create_report(cls, device_health_report_id, device_id, customer_id, 
                     business_id, report_id, health_report=None, report_type=1,
                     report_date='', report_status='INIT', parameter=''):
        """创建设备健康报告"""
        return cls.create(
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
    
    @classmethod
    def get_by_device_id(cls, device_id):
        """根据设备 ID 获取报告列表"""
        return cls.select().where(cls.device_id == device_id)
    
    @classmethod
    def get_by_date_range(cls, device_id, start_date, end_date):
        """根据日期范围获取报告"""
        return cls.select().where(
            (cls.device_id == device_id) &
            (cls.report_date >= start_date) &
            (cls.report_date <= end_date)
        )
    
    def update_report(self, **kwargs):
        """更新报告信息"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.update_time = datetime.now()
        self.save()
```

### 2. health_report_middle 中间

#### 2.1 model

#### 2.2 sql

```mysql
CREATE TABLE `device_health_report` (
	`id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'ID Id',
	`device_health_report_id` BIGINT UNSIGNED NOT NULL DEFAULT '0' COMMENT '健康报告 Id',
	`device_id` BIGINT UNSIGNED NOT NULL DEFAULT '0' COMMENT '设备_id_逻辑主键',
	`customer_id` BIGINT UNSIGNED NOT NULL DEFAULT '0' COMMENT '客户 id',
	`business_id` BIGINT UNSIGNED NOT NULL DEFAULT '0' COMMENT '服务方_id',
	`report_id` VARCHAR(50) NOT NULL DEFAULT '0' COMMENT '报告 id' COLLATE 'utf8mb4_general_ci',
	`health_report` JSON NULL DEFAULT NULL COMMENT '设备健康报告信息',
	`report_type` INT NULL DEFAULT '1' COMMENT '报告类型 1-睡小宝睡眠报告 2-睡小宝生理报告 3-心晓健康报告 4-唉微手表健康报告',
	`report_date` VARCHAR(50) NULL DEFAULT '' COMMENT '报告日期' COLLATE 'utf8mb4_general_ci',
	`report_status` VARCHAR(10) NOT NULL DEFAULT '' COMMENT '报告状态  INIT: 初始' COLLATE 'utf8mb4_general_ci',
	`parameter` VARCHAR(300) NOT NULL DEFAULT '' COMMENT '相关参数' COLLATE 'utf8mb4_general_ci',
	`delete_flag` INT UNSIGNED NOT NULL DEFAULT '0' COMMENT '删除标志 不启用，用历史表',
	`create_time` TIMESTAMP NOT NULL DEFAULT (CURRENT_TIMESTAMP) COMMENT '创建时间',
	`update_time` TIMESTAMP NOT NULL DEFAULT (CURRENT_TIMESTAMP) ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
	PRIMARY KEY (`id`) USING BTREE,
	UNIQUE INDEX `unqi_device_health_report_device_health_report_id` (`device_health_report_id`) USING BTREE,
	INDEX `customer_id` (`customer_id`) USING BTREE,
	INDEX `device_id` (`device_id`) USING BTREE,
	INDEX `idx_report_date_device_id` (`report_date`, `device_id`) USING BTREE,
	INDEX `fk_parameter` (`parameter`) USING BTREE,
	INDEX `fk_report_id` (`report_id`) USING BTREE
)
COMMENT='设备中间信息'
COLLATE='utf8mb4_general_ci'
ENGINE=InnoDB
AUTO_INCREMENT=5473699
;
```
#### 2.3 python peewee example

### 3. health_report_result

#### 3.1 model

#### 3.2 sql

#### 3.3 python peewee example

### 4. 