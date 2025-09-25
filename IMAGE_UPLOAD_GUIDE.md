# 图片上传功能使用指南

## 问题解决

您遇到的错误：
```json
{
    "success": false,
    "message": "Validation failed",
    "errors": {
        "images": {
            "0": [
                "The submitted data was not a file. Check the encoding type on the form."
            ]
        }
    }
}
```

这个错误已经通过以下方式解决：

## 解决方案

### 1. 分离事件创建和图片上传

- **事件创建**：使用 `EventCreateSerializer`，不包含图片字段
- **图片上传**：使用专门的 `upload_images` 端点

### 2. 新的API端点

#### 创建事件（不带图片）
```
POST /api/events/
Content-Type: application/json

{
    "title": "事件标题",
    "description": "事件描述",
    "max_attendees": 50,
    "start_date": "2024-01-15",
    "end_date": "2024-01-15",
    "start_time": "10:00:00",
    "end_time": "12:00:00",
    "street": "街道地址",
    "city": "城市",
    "state": "省份",
    "postal_code": "邮政编码",
    "organizer": 1
}
```

#### 上传图片到事件
```
POST /api/events/{event_id}/upload_images/
Content-Type: multipart/form-data

# 表单数据：
images: [图片文件1]
images: [图片文件2]
# 或者
image: [图片文件]
```

## 使用方法

### 1. 创建事件
首先创建一个不带图片的事件：

```bash
curl -X POST http://localhost:8000/api/events/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "我的活动",
    "description": "这是一个很棒的活动",
    "max_attendees": 100,
    "start_date": "2024-01-15",
    "end_date": "2024-01-15",
    "start_time": "10:00:00",
    "end_time": "18:00:00",
    "street": "123 Main St",
    "city": "北京",
    "state": "北京",
    "postal_code": "100000",
    "organizer": 1
  }'
```

### 2. 上传图片
然后为事件上传图片：

```bash
curl -X POST http://localhost:8000/api/events/1/upload_images/ \
  -F "images=@image1.jpg" \
  -F "images=@image2.jpg"
```

### 3. 前端JavaScript示例

```javascript
// 创建事件
const createEvent = async (eventData) => {
  const response = await fetch('/api/events/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(eventData)
  });
  return response.json();
};

// 上传图片
const uploadImages = async (eventId, imageFiles) => {
  const formData = new FormData();
  
  // 添加图片文件
  imageFiles.forEach((file, index) => {
    formData.append('images', file);
  });
  
  const response = await fetch(`/api/events/${eventId}/upload_images/`, {
    method: 'POST',
    body: formData
  });
  return response.json();
};

// 使用示例
const eventData = {
  title: "我的活动",
  description: "活动描述",
  max_attendees: 100,
  start_date: "2024-01-15",
  end_date: "2024-01-15",
  start_time: "10:00:00",
  end_time: "18:00:00",
  street: "123 Main St",
  city: "北京",
  state: "北京",
  postal_code: "100000",
  organizer: 1
};

// 创建事件
const event = await createEvent(eventData);
console.log('事件创建成功:', event);

// 上传图片
const imageFiles = document.getElementById('imageInput').files;
const uploadResult = await uploadImages(event.event.id, imageFiles);
console.log('图片上传成功:', uploadResult);
```

## 图片验证规则

- **文件类型**：只允许 JPEG, PNG, GIF, WebP
- **文件大小**：最大 10MB
- **数量限制**：每个事件最多 10 张图片
- **主图片**：第一张上传的图片自动设为主图片

## 响应格式

### 成功响应
```json
{
  "success": true,
  "message": "Successfully uploaded 2 images",
  "images": [
    {
      "id": 1,
      "image_url": "http://localhost:8000/media/event_images/2024/01/15/image1.jpg",
      "is_primary": true,
      "uploaded_at": "2024-01-15T10:00:00Z"
    },
    {
      "id": 2,
      "image_url": "http://localhost:8000/media/event_images/2024/01/15/image2.jpg",
      "is_primary": false,
      "uploaded_at": "2024-01-15T10:00:01Z"
    }
  ]
}
```

### 错误响应
```json
{
  "success": false,
  "message": "Image validation failed",
  "errors": {
    "images": {
      "0": ["Image size cannot exceed 10MB."]
    }
  }
}
```

## 测试

运行测试脚本：
```bash
python test_image_upload.py
```

这将测试：
1. 不带图片的事件创建
2. 图片上传功能
3. 数据清理

