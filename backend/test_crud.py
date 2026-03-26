"""
设备健康报告 API 测试脚本
用于测试基本的 CRUD 功能
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"


def test_create_report():
    """测试创建报告"""
    print("\n=== 测试创建报告 ===")
    
    data = {
        "device_health_report_id": 12345,
        "device_id": 1001,
        "customer_id": 2001,
        "business_id": 3001,
        "report_id": "RPT20240101001",
        "health_report": {
            "sleep_score": 85,
            "duration": 7.5,
            "deep_sleep": 2.5,
            "light_sleep": 5.0
        },
        "report_type": 1,
        "report_date": "2024-01-01",
        "report_status": "INIT",
        "parameter": "test_parameter"
    }
    
    response = requests.post(f"{BASE_URL}/device-health-reports", json=data)
    print(f"状态码：{response.status_code}")
    print(f"响应：{json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    return response.json()


def test_get_report(report_id: int):
    """测试获取报告详情"""
    print(f"\n=== 测试获取报告 (ID={report_id}) ===")
    
    response = requests.get(f"{BASE_URL}/device-health-reports/{report_id}")
    print(f"状态码：{response.status_code}")
    print(f"响应：{json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    return response.json()


def test_update_report(report_id: int):
    """测试更新报告"""
    print(f"\n=== 测试更新报告 (ID={report_id}) ===")
    
    data = {
        "report_status": "COMPLETED",
        "parameter": "updated_parameter"
    }
    
    response = requests.put(f"{BASE_URL}/device-health-reports/{report_id}", json=data)
    print(f"状态码：{response.status_code}")
    print(f"响应：{json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    return response.json()


def test_get_reports_by_device(device_id: int):
    """测试根据设备 ID 获取报告列表"""
    print(f"\n=== 测试根据设备 ID 获取报告 (device_id={device_id}) ===")
    
    response = requests.get(f"{BASE_URL}/device-health-reports/device/{device_id}")
    print(f"状态码：{response.status_code}")
    print(f"响应：{json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    return response.json()


def test_get_reports_list(page: int = 1, page_size: int = 10):
    """测试分页获取报告列表"""
    print(f"\n=== 测试分页获取报告列表 (page={page}, page_size={page_size}) ===")
    
    params = {"page": page, "page_size": page_size}
    response = requests.get(f"{BASE_URL}/device-health-reports", params=params)
    print(f"状态码：{response.status_code}")
    print(f"响应：{json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    return response.json()


def test_delete_report(report_id: int):
    """测试删除报告（软删除）"""
    print(f"\n=== 测试删除报告 (ID={report_id}) ===")
    
    response = requests.delete(f"{BASE_URL}/device-health-reports/{report_id}")
    print(f"状态码：{response.status_code}")
    print(f"响应：{json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    return response.json()


if __name__ == "__main__":
    print("开始运行设备健康报告 CRUD 测试...")
    print(f"API 地址：{BASE_URL}")
    
    try:
        # 1. 创建报告
        created = test_create_report()
        
        # 获取创建的报告 ID
        report_id = created.get('id')
        
        if report_id:
            # 2. 获取报告详情
            test_get_report(report_id)
            
            # 3. 更新报告
            test_update_report(report_id)
            
            # 4. 根据设备 ID 获取报告
            test_get_reports_by_device(1001)
            
            # 5. 分页获取报告列表
            test_get_reports_list()
            
            # 6. 删除报告
            test_delete_report(report_id)
            
            # 7. 再次获取已删除的报告（应该显示 delete_flag=1）
            print("\n=== 验证软删除后的报告 ===")
            test_get_report(report_id)
        
        print("\n✅ 所有测试完成！")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ 错误：无法连接到服务器，请确保服务已启动")
        print("运行命令：python main.py")
    except Exception as e:
        print(f"\n❌ 测试失败：{e}")
