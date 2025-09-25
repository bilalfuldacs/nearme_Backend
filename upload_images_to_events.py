#!/usr/bin/env python
import os
import sys
import django
import requests
from PIL import Image
import io

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_api.settings')
django.setup()

from myapp.models import User, Event

def create_sample_image():
    """Create a sample image for testing"""
    # Create a simple colored image
    img = Image.new('RGB', (300, 200), color='lightblue')
    
    # Add some text (this is just for testing)
    from PIL import ImageDraw, ImageFont
    draw = ImageDraw.Draw(img)
    
    # Try to use a default font, fallback to basic if not available
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        font = ImageFont.load_default()
    
    draw.text((50, 50), "Sample Event Image", fill='darkblue', font=font)
    draw.text((50, 80), "This is a test image", fill='darkblue', font=font)
    
    # Convert to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    
    return img_bytes

def upload_images_to_event(event_id, image_count=2):
    """Upload sample images to a specific event"""
    print(f"Uploading {image_count} images to event ID {event_id}...")
    
    base_url = "http://localhost:8000"
    upload_url = f"{base_url}/api/events/{event_id}/upload_images/"
    
    # Create sample images
    images_data = []
    for i in range(image_count):
        img_bytes = create_sample_image()
        images_data.append(('images', (f'sample_image_{i+1}.jpg', img_bytes, 'image/jpeg')))
    
    try:
        response = requests.post(upload_url, files=images_data)
        
        if response.status_code == 201:
            data = response.json()
            print(f"✅ Successfully uploaded {len(data.get('images', []))} images!")
            for img in data.get('images', []):
                print(f"   - Image ID: {img['id']}, URL: {img['image_url']}")
            return True
        else:
            print(f"❌ Upload failed! Status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure Django server is running.")
        return False
    except Exception as e:
        print(f"❌ Error during upload: {e}")
        return False

def upload_images_to_all_events():
    """Upload sample images to all events that don't have images"""
    print("=== Uploading Images to All Events ===")
    
    # Get all events without images
    events_without_images = Event.objects.filter(images__isnull=True).distinct()
    
    print(f"Found {events_without_images.count()} events without images")
    
    if events_without_images.count() == 0:
        print("All events already have images!")
        return
    
    for event in events_without_images:
        print(f"\nProcessing event: {event.title} (ID: {event.id})")
        success = upload_images_to_event(event.id, image_count=2)
        
        if success:
            print(f"✅ Images uploaded to '{event.title}'")
        else:
            print(f"❌ Failed to upload images to '{event.title}'")

def list_events_with_images():
    """List all events and their image status"""
    print("=== Events Image Status ===")
    
    events = Event.objects.all()
    
    for event in events:
        image_count = event.images.count()
        print(f"Event: {event.title} (ID: {event.id})")
        print(f"  Images: {image_count}")
        
        if image_count > 0:
            print(f"  Primary image: {event.images.filter(is_primary=True).first().image.url}")
        else:
            print(f"  No images")
        print()

if __name__ == "__main__":
    print("🚀 Image Upload Helper")
    print("1. List events and their image status")
    print("2. Upload sample images to all events without images")
    print("3. Upload images to a specific event")
    
    choice = input("\nEnter your choice (1/2/3): ").strip()
    
    if choice == "1":
        list_events_with_images()
    elif choice == "2":
        upload_images_to_all_events()
    elif choice == "3":
        event_id = input("Enter event ID: ").strip()
        try:
            event_id = int(event_id)
            upload_images_to_event(event_id)
        except ValueError:
            print("❌ Invalid event ID")
    else:
        print("❌ Invalid choice")
    
    print("\n🎉 Done!")


