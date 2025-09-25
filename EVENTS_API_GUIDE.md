# 事件API使用指南

## 获取所有事件数据

### 基本端点
```
GET /api/events/
```

### 响应格式
```json
{
  "success": true,
  "count": 25,
  "results": [
    {
      "id": 1,
      "title": "技术交流会",
      "description": "分享最新的技术趋势和开发经验",
      "max_attendees": 100,
      "start_date": "2024-02-15",
      "end_date": "2024-02-15",
      "start_time": "09:00:00",
      "end_time": "17:00:00",
      "city": "北京",
      "state": "北京",
      "organizer_name": "活动组织者",
      "is_active": true,
      "created_at": "2024-01-15T10:00:00Z",
      "primary_image": "http://localhost:8000/media/event_images/2024/01/15/image.jpg",
      "image_count": 3,
      "full_address": "中关村大街1号, 北京, 北京 100000",
      "is_upcoming": true
    }
  ]
}
```

## 过滤和搜索功能

### 1. 按城市过滤
```
GET /api/events/?city=北京
```

### 2. 按省份过滤
```
GET /api/events/?state=北京
```

### 3. 按组织者过滤
```
GET /api/events/?organizer=1
```

### 4. 按活跃状态过滤
```
GET /api/events/?is_active=true
```

### 5. 按开始日期过滤
```
GET /api/events/?start_date=2024-02-15
```

### 6. 搜索事件
```
GET /api/events/?search=技术
```
搜索字段包括：标题、描述、城市、省份

### 7. 排序
```
GET /api/events/?ordering=start_date          # 按开始日期升序
GET /api/events/?ordering=-start_date         # 按开始日期降序
GET /api/events/?ordering=title                # 按标题升序
GET /api/events/?ordering=-created_at          # 按创建时间降序（默认）
```

### 8. 组合过滤
```
GET /api/events/?city=北京&is_active=true&ordering=start_date
```

## 特殊端点

### 1. 即将到来的事件
```
GET /api/events/upcoming/
```

### 2. 过去的事件
```
GET /api/events/past/
```

### 3. 按位置筛选
```
GET /api/events/by_location/?city=北京
GET /api/events/by_location/?state=北京
GET /api/events/by_location/?city=北京&state=北京
```

## 分页

### 基本分页
```
GET /api/events/?page=1&page_size=10
```

### 响应格式（带分页）
```json
{
  "count": 25,
  "next": "http://localhost:8000/api/events/?page=2",
  "previous": null,
  "results": [...]
}
```

## 使用示例

### JavaScript/Fetch API
```javascript
// 获取所有事件
const fetchAllEvents = async () => {
  try {
    const response = await fetch('/api/events/');
    const data = await response.json();
    
    if (data.success) {
      console.log(`找到 ${data.count} 个事件`);
      return data.results;
    } else {
      console.error('获取事件失败:', data.message);
    }
  } catch (error) {
    console.error('请求错误:', error);
  }
};

// 搜索事件
const searchEvents = async (searchTerm) => {
  try {
    const response = await fetch(`/api/events/?search=${encodeURIComponent(searchTerm)}`);
    const data = await response.json();
    return data.results;
  } catch (error) {
    console.error('搜索错误:', error);
  }
};

// 按城市过滤
const getEventsByCity = async (city) => {
  try {
    const response = await fetch(`/api/events/?city=${encodeURIComponent(city)}`);
    const data = await response.json();
    return data.results;
  } catch (error) {
    console.error('过滤错误:', error);
  }
};

// 获取即将到来的事件
const getUpcomingEvents = async () => {
  try {
    const response = await fetch('/api/events/upcoming/');
    const data = await response.json();
    return data.results;
  } catch (error) {
    console.error('获取即将到来事件错误:', error);
  }
};
```

### cURL 示例
```bash
# 获取所有事件
curl -X GET "http://localhost:8000/api/events/"

# 按城市过滤
curl -X GET "http://localhost:8000/api/events/?city=北京"

# 搜索事件
curl -X GET "http://localhost:8000/api/events/?search=技术"

# 获取即将到来的事件
curl -X GET "http://localhost:8000/api/events/upcoming/"

# 分页获取
curl -X GET "http://localhost:8000/api/events/?page=1&page_size=5"
```

### Python requests 示例
```python
import requests

# 获取所有事件
response = requests.get('http://localhost:8000/api/events/')
data = response.json()

if data['success']:
    events = data['results']
    print(f"找到 {data['count']} 个事件")
    
    for event in events:
        print(f"- {event['title']} ({event['city']})")
else:
    print(f"错误: {data['message']}")

# 搜索事件
search_response = requests.get('http://localhost:8000/api/events/', 
                              params={'search': '技术'})
search_data = search_response.json()

# 按城市过滤
city_response = requests.get('http://localhost:8000/api/events/', 
                            params={'city': '北京'})
city_data = city_response.json()
```

## 错误处理

### 常见错误响应
```json
{
  "success": false,
  "message": "An error occurred while fetching events",
  "error": "具体错误信息"
}
```

### HTTP 状态码
- `200 OK`: 成功获取事件
- `400 Bad Request`: 请求参数错误
- `500 Internal Server Error`: 服务器内部错误

## 性能优化

### 数据库查询优化
- 使用 `select_related` 预加载组织者信息
- 使用 `prefetch_related` 预加载图片信息
- 默认按创建时间降序排列

### 缓存建议
- 对于频繁访问的事件列表，建议使用 Redis 缓存
- 缓存时间建议设置为 5-10 分钟

## 测试

运行测试脚本：
```bash
python test_fetch_events.py
```

这将测试：
1. 基本的事件获取功能
2. 各种过滤和搜索功能
3. 特殊端点
4. 错误处理


