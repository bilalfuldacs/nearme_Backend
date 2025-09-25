# Enhanced Events API with Image Handling

## Overview

The Events API has been enhanced to provide comprehensive image handling capabilities. All endpoints now include detailed image information with absolute URLs, making it easy for frontend applications to display event images.

## Main Endpoint

### Get All Events with Images
```
GET /api/events/
```

### Enhanced Response Format
```json
{
  "success": true,
  "count": 25,
  "results": [
    {
      "id": 1,
      "title": "Tech Conference 2024",
      "description": "Annual technology conference featuring the latest innovations",
      "max_attendees": 500,
      "start_date": "2024-03-15",
      "end_date": "2024-03-15",
      "start_time": "09:00:00",
      "end_time": "18:00:00",
      "city": "San Francisco",
      "state": "California",
      "organizer_name": "Tech Events Inc",
      "organizer_email": "organizer@techevents.com",
      "is_active": true,
      "created_at": "2024-01-15T10:00:00Z",
      "primary_image": "http://localhost:8000/media/event_images/2024/01/15/conference_main.jpg",
      "image_count": 3,
      "all_images": [
        {
          "id": 1,
          "url": "http://localhost:8000/media/event_images/2024/01/15/conference_main.jpg",
          "caption": "Main conference hall",
          "is_primary": true,
          "uploaded_at": "2024-01-15T10:00:00Z"
        },
        {
          "id": 2,
          "url": "http://localhost:8000/media/event_images/2024/01/15/speakers.jpg",
          "caption": "Featured speakers",
          "is_primary": false,
          "uploaded_at": "2024-01-15T10:01:00Z"
        },
        {
          "id": 3,
          "url": "http://localhost:8000/media/event_images/2024/01/15/venue.jpg",
          "caption": "Conference venue",
          "is_primary": false,
          "uploaded_at": "2024-01-15T10:02:00Z"
        }
      ],
      "full_address": "123 Tech Street, San Francisco, California 94105",
      "is_upcoming": true,
      "is_past": false
    }
  ]
}
```

## Image Fields Explained

### Primary Image
- **`primary_image`**: Direct URL to the main/primary image for the event
- **`image_count`**: Total number of images associated with the event
- **`all_images`**: Array containing all images with detailed information

### Image Object Structure
Each image in the `all_images` array contains:
- **`id`**: Unique identifier for the image
- **`url`**: Absolute URL to access the image
- **`caption`**: Optional caption/description for the image
- **`is_primary`**: Boolean indicating if this is the primary image
- **`uploaded_at`**: Timestamp when the image was uploaded

## Filtering and Search with Images

All filtering and search capabilities work with the enhanced image data:

### Filter by Events with Images
```bash
# Get events that have images
curl "http://localhost:8000/api/events/?image_count__gt=0"
```

### Search Events with Images
```bash
# Search for events and include image data
curl "http://localhost:8000/api/events/?search=conference"
```

### Filter by Location with Images
```bash
# Get events in a specific city with image data
curl "http://localhost:8000/api/events/?city=San Francisco"
```

## Special Endpoints with Images

### Upcoming Events with Images
```
GET /api/events/upcoming/
```
Returns upcoming events with complete image information.

### Past Events with Images
```
GET /api/events/past/
```
Returns past events with complete image information.

### Events by Location with Images
```
GET /api/events/by_location/?city=San Francisco&state=California
```
Returns events filtered by location with complete image information.

## Frontend Integration Examples

### JavaScript/React Example
```javascript
import React, { useState, useEffect } from 'react';

const EventsList = () => {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchEvents = async () => {
      try {
        const response = await fetch('/api/events/');
        const data = await response.json();
        
        if (data.success) {
          setEvents(data.results);
        }
      } catch (error) {
        console.error('Error fetching events:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchEvents();
  }, []);

  if (loading) return <div>Loading...</div>;

  return (
    <div className="events-grid">
      {events.map(event => (
        <div key={event.id} className="event-card">
          {/* Primary Image */}
          {event.primary_image && (
            <img 
              src={event.primary_image} 
              alt={event.title}
              className="event-primary-image"
            />
          )}
          
          <div className="event-info">
            <h3>{event.title}</h3>
            <p>{event.description}</p>
            <p>📍 {event.full_address}</p>
            <p>📅 {event.start_date} at {event.start_time}</p>
            <p>👤 Organizer: {event.organizer_name}</p>
            
            {/* Image Gallery */}
            {event.all_images && event.all_images.length > 0 && (
              <div className="image-gallery">
                <h4>Event Images ({event.image_count})</h4>
                <div className="images-grid">
                  {event.all_images.map(image => (
                    <div key={image.id} className="image-item">
                      <img 
                        src={image.url} 
                        alt={image.caption || event.title}
                        className={image.is_primary ? 'primary-image' : 'secondary-image'}
                      />
                      {image.caption && (
                        <p className="image-caption">{image.caption}</p>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
};

export default EventsList;
```

### Vue.js Example
```vue
<template>
  <div class="events-container">
    <div v-for="event in events" :key="event.id" class="event-card">
      <!-- Primary Image -->
      <img 
        v-if="event.primary_image" 
        :src="event.primary_image" 
        :alt="event.title"
        class="primary-image"
      />
      
      <div class="event-details">
        <h2>{{ event.title }}</h2>
        <p>{{ event.description }}</p>
        <p>📍 {{ event.full_address }}</p>
        <p>📅 {{ event.start_date }} at {{ event.start_time }}</p>
        
        <!-- Image Gallery -->
        <div v-if="event.all_images && event.all_images.length > 0" class="gallery">
          <h3>Event Gallery ({{ event.image_count }} images)</h3>
          <div class="images">
            <div 
              v-for="image in event.all_images" 
              :key="image.id"
              class="image-item"
            >
              <img 
                :src="image.url" 
                :alt="image.caption || event.title"
                :class="{ 'primary': image.is_primary }"
              />
              <p v-if="image.caption" class="caption">{{ image.caption }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      events: []
    }
  },
  async mounted() {
    try {
      const response = await fetch('/api/events/');
      const data = await response.json();
      
      if (data.success) {
        this.events = data.results;
      }
    } catch (error) {
      console.error('Error fetching events:', error);
    }
  }
}
</script>
```

## Image Upload Integration

### Upload Images to Existing Event
```javascript
const uploadEventImages = async (eventId, imageFiles) => {
  const formData = new FormData();
  
  // Add multiple images
  Array.from(imageFiles).forEach(file => {
    formData.append('images', file);
  });
  
  try {
    const response = await fetch(`/api/events/${eventId}/upload_images/`, {
      method: 'POST',
      body: formData
    });
    
    const data = await response.json();
    
    if (data.success) {
      console.log(`Successfully uploaded ${data.images.length} images`);
      return data.images;
    } else {
      console.error('Upload failed:', data.message);
    }
  } catch (error) {
    console.error('Upload error:', error);
  }
};
```

## Performance Considerations

### Image Optimization
- Images are served with absolute URLs for easy caching
- Consider implementing image resizing/compression on upload
- Use CDN for image delivery in production

### Database Optimization
- Images are prefetched with events to minimize database queries
- Use pagination for large event lists
- Consider implementing image lazy loading for better performance

## Error Handling

### Common Image-Related Errors
```json
{
  "success": false,
  "message": "Image validation failed",
  "errors": {
    "images": {
      "0": ["Image size cannot exceed 10MB."],
      "1": ["Only JPEG, PNG, GIF, and WebP images are allowed."]
    }
  }
}
```

## Testing

Run the comprehensive test suite:
```bash
python test_fetch_events.py
```

This will test:
- Basic event retrieval with images
- Image data structure validation
- Filtering with image data
- Special endpoints with images
- Error handling

## Migration Notes

If you're upgrading from the previous version:
1. The `images` field now includes absolute URLs
2. New fields: `primary_image`, `image_count`, `all_images`
3. Enhanced `organizer_email` field
4. All existing functionality remains backward compatible


