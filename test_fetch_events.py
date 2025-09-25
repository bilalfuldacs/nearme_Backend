#!/usr/bin/env python
import os
import sys
import django
import requests
import json

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_api.settings')
django.setup()

from myapp.models import User, Event

def test_fetch_all_events():
    """测试获取所有事件数据"""
    print("=== 测试获取所有事件数据 ===")
    
    base_url = "http://localhost:8000"
    events_url = f"{base_url}/api/events/"
    
    try:
        response = requests.get(events_url)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 成功获取事件数据!")
            print(f"   总数: {data.get('count', 'N/A')}")
            print(f"   成功状态: {data.get('success', 'N/A')}")
            
            events = data.get('results', [])
            print(f"   事件数量: {len(events)}")
            
            for i, event in enumerate(events[:3]):  # Show first 3 events
                print(f"   Event {i+1}:")
                print(f"     ID: {event.get('id')}")
                print(f"     Title: {event.get('title')}")
                print(f"     City: {event.get('city')}")
                print(f"     Start Date: {event.get('start_date')}")
                print(f"     Organizer: {event.get('organizer_name')}")
                print(f"     Is Active: {event.get('is_active')}")
                print(f"     Primary Image: {event.get('primary_image')}")
                print(f"     Image Count: {event.get('image_count')}")
                
                # Show all images if available
                all_images = event.get('all_images', [])
                if all_images:
                    print(f"     All Images ({len(all_images)}):")
                    for j, img in enumerate(all_images[:2]):  # Show first 2 images
                        print(f"       Image {j+1}: {img.get('url')}")
                        print(f"         Caption: {img.get('caption', 'N/A')}")
                        print(f"         Is Primary: {img.get('is_primary')}")
                    if len(all_images) > 2:
                        print(f"       ... and {len(all_images) - 2} more images")
                else:
                    print(f"     No images available")
                print()
            
            if len(events) > 3:
                print(f"   ... 还有 {len(events) - 3} 个事件")
                
        else:
            print(f"❌ 获取事件数据失败! 状态码: {response.status_code}")
            print(f"   响应: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器。请确保Django服务器正在运行 (python manage.py runserver)")
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")

def test_fetch_events_with_filters():
    """测试带过滤条件的事件获取"""
    print("\n=== 测试带过滤条件的事件获取 ===")
    
    base_url = "http://localhost:8000"
    
    # 测试不同的过滤条件
    test_cases = [
        {"name": "获取活跃事件", "params": {"active_only": "true"}},
        {"name": "按城市过滤", "params": {"city": "北京"}},
        {"name": "搜索事件", "params": {"search": "测试"}},
        {"name": "按开始日期排序", "params": {"ordering": "start_date"}},
        {"name": "限制数量", "params": {"page_size": "5"}},
    ]
    
    for test_case in test_cases:
        print(f"测试: {test_case['name']}")
        try:
            response = requests.get(f"{base_url}/api/events/", params=test_case['params'])
            
            if response.status_code == 200:
                data = response.json()
                print(f"  ✅ 成功! 找到 {data.get('count', 0)} 个事件")
            else:
                print(f"  ❌ 失败! 状态码: {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ 错误: {e}")
        print()

def test_specific_event_endpoints():
    """Test specific event endpoints"""
    print("\n=== Testing Specific Event Endpoints ===")
    
    base_url = "http://localhost:8000"
    
    endpoints = [
        {"name": "Upcoming Events", "url": f"{base_url}/api/events/upcoming/"},
        {"name": "Past Events", "url": f"{base_url}/api/events/past/"},
        {"name": "Events by Location", "url": f"{base_url}/api/events/by_location/?city=北京"},
    ]
    
    for endpoint in endpoints:
        print(f"Testing: {endpoint['name']}")
        try:
            response = requests.get(endpoint['url'])
            
            if response.status_code == 200:
                data = response.json()
                print(f"  ✅ Success! Found {data.get('count', 0)} events")
            else:
                print(f"  ❌ Failed! Status code: {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
        print()

def test_image_handling():
    """Test comprehensive image handling in event responses"""
    print("\n=== Testing Image Handling ===")
    
    base_url = "http://localhost:8000"
    
    try:
        # Get all events
        response = requests.get(f"{base_url}/api/events/")
        
        if response.status_code == 200:
            data = response.json()
            events = data.get('results', [])
            
            print(f"✅ Retrieved {len(events)} events")
            
            # Check image handling for each event
            events_with_images = 0
            total_images = 0
            
            for event in events:
                event_id = event.get('id')
                title = event.get('title')
                image_count = event.get('image_count', 0)
                primary_image = event.get('primary_image')
                all_images = event.get('all_images', [])
                
                print(f"\nEvent: {title} (ID: {event_id})")
                print(f"  Image Count: {image_count}")
                print(f"  Primary Image: {primary_image}")
                print(f"  All Images Count: {len(all_images)}")
                
                if image_count > 0:
                    events_with_images += 1
                    total_images += image_count
                    
                    # Verify image data structure
                    for img in all_images:
                        if 'url' in img and 'is_primary' in img:
                            print(f"    ✅ Image URL: {img['url']}")
                            print(f"    ✅ Is Primary: {img['is_primary']}")
                        else:
                            print(f"    ❌ Invalid image data structure")
            
            print(f"\n📊 Summary:")
            print(f"  Events with images: {events_with_images}")
            print(f"  Total images: {total_images}")
            
        else:
            print(f"❌ Failed to retrieve events. Status: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing image handling: {e}")

def create_sample_events():
    """创建一些示例事件用于测试"""
    print("=== 创建示例事件 ===")
    
    # 创建测试用户
    user, created = User.objects.get_or_create(
        email="organizer@example.com",
        defaults={
            'name': "活动组织者",
            'password': "password123"
        }
    )
    
    if created:
        print(f"✅ 创建用户: {user.name}")
    else:
        print(f"✅ 使用现有用户: {user.name}")
    
    # 创建示例事件
    sample_events = [
        {
            'title': '技术交流会',
            'description': '分享最新的技术趋势和开发经验',
            'max_attendees': 100,
            'start_date': '2024-02-15',
            'end_date': '2024-02-15',
            'start_time': '09:00:00',
            'end_time': '17:00:00',
            'street': '中关村大街1号',
            'city': '北京',
            'state': '北京',
            'postal_code': '100000',
            'organizer': user
        },
        {
            'title': '创业分享会',
            'description': '成功创业者分享创业经验和心得',
            'max_attendees': 50,
            'start_date': '2024-02-20',
            'end_date': '2024-02-20',
            'start_time': '14:00:00',
            'end_time': '18:00:00',
            'street': '浦东新区陆家嘴环路1000号',
            'city': '上海',
            'state': '上海',
            'postal_code': '200000',
            'organizer': user
        },
        {
            'title': '艺术展览',
            'description': '当代艺术家的作品展览',
            'max_attendees': 200,
            'start_date': '2024-01-10',
            'end_date': '2024-01-10',
            'start_time': '10:00:00',
            'end_time': '20:00:00',
            'street': '天河区珠江新城花城大道',
            'city': '广州',
            'state': '广东',
            'postal_code': '510000',
            'organizer': user
        }
    ]
    
    created_count = 0
    for event_data in sample_events:
        event, created = Event.objects.get_or_create(
            title=event_data['title'],
            start_date=event_data['start_date'],
            defaults=event_data
        )
        if created:
            created_count += 1
            print(f"✅ 创建事件: {event.title}")
    
    print(f"✅ 总共创建了 {created_count} 个新事件")

if __name__ == "__main__":
    print("🚀 开始测试事件获取功能...")
    
    try:
        # 创建示例事件
        create_sample_events()
        
        # 测试获取所有事件
        test_fetch_all_events()
        
        # 测试带过滤条件的事件获取
        test_fetch_events_with_filters()
        
        # Test specific endpoints
        test_specific_event_endpoints()
        
        # Test image handling
        test_image_handling()
        
        print("\n🎉 All tests completed!")
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
