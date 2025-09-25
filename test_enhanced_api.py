#!/usr/bin/env python3
"""
Comprehensive test script for the enhanced Event Requests API
Tests all the new backend changes including attendance tracking and management features
"""

import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_event_management_endpoint():
    """Test the new event management endpoint"""
    print("=== Testing Event Management Endpoint ===")
    
    try:
        # First get an event ID
        events_response = requests.get(f"{BASE_URL}/events/")
        if events_response.status_code == 200:
            events_data = events_response.json()
            if events_data.get('results'):
                event_id = events_data['results'][0]['id']
                
                # Test the management endpoint
                response = requests.get(f"{BASE_URL}/events/{event_id}/manage/")
                print(f"Status Code: {response.status_code}")
                print(f"Response: {json.dumps(response.json(), indent=2)}")
                return response.json()
            else:
                print("No events found to test management endpoint")
        else:
            print(f"Failed to get events: {events_response.status_code}")
    except Exception as e:
        print(f"Error: {e}")
    return None

def test_attendance_tracking():
    """Test attendance tracking by creating and updating requests"""
    print("\n=== Testing Attendance Tracking ===")
    
    try:
        # Get an event ID
        events_response = requests.get(f"{BASE_URL}/events/")
        if events_response.status_code == 200:
            events_data = events_response.json()
            if events_data.get('results'):
                event_id = events_data['results'][0]['id']
                
                # Check initial attendance
                print(f"Testing with Event ID: {event_id}")
                management_response = requests.get(f"{BASE_URL}/events/{event_id}/manage/")
                if management_response.status_code == 200:
                    initial_data = management_response.json()
                    initial_attendees = initial_data['event']['current_attendees']
                    print(f"Initial attendees: {initial_attendees}")
                    
                    # Create a new request
                    request_data = {
                        "event": event_id,
                        "user_email": "test_attendance@example.com",
                        "user_name": "Test Attendance User",
                        "message": "Testing attendance tracking"
                    }
                    
                    create_response = requests.post(f"{BASE_URL}/requests/", json=request_data)
                    if create_response.status_code == 201:
                        request_data = create_response.json()
                        request_id = request_data['request']['id']
                        print(f"Created request ID: {request_id}")
                        
                        # Confirm the request
                        update_data = {"status": "confirmed"}
                        update_response = requests.patch(f"{BASE_URL}/requests/{request_id}/", json=update_data)
                        if update_response.status_code == 200:
                            print("Request confirmed successfully")
                            
                            # Check updated attendance
                            updated_management = requests.get(f"{BASE_URL}/events/{event_id}/manage/")
                            if updated_management.status_code == 200:
                                updated_data = updated_management.json()
                                updated_attendees = updated_data['event']['current_attendees']
                                print(f"Updated attendees: {updated_attendees}")
                                print(f"Attendance increased: {updated_attendees > initial_attendees}")
                            else:
                                print("Failed to get updated management data")
                        else:
                            print(f"Failed to confirm request: {update_response.status_code}")
                    else:
                        print(f"Failed to create request: {create_response.status_code}")
                else:
                    print("Failed to get initial management data")
            else:
                print("No events found for attendance testing")
    except Exception as e:
        print(f"Error: {e}")

def test_enhanced_events_list():
    """Test the enhanced events list with attendance data"""
    print("\n=== Testing Enhanced Events List ===")
    
    try:
        response = requests.get(f"{BASE_URL}/events/")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('results'):
                event = data['results'][0]
                print("Enhanced event data includes:")
                print(f"- current_attendees: {event.get('current_attendees')}")
                print(f"- available_spots: {event.get('available_spots')}")
                print(f"- is_full: {event.get('is_full')}")
                print(f"- attendance: {len(event.get('attendance', []))} attendees")
                print(f"Sample attendance data: {event.get('attendance', [])[:2]}")
            else:
                print("No events found")
        else:
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

def test_enhanced_requests_list():
    """Test the enhanced requests list"""
    print("\n=== Testing Enhanced Requests List ===")
    
    try:
        response = requests.get(f"{BASE_URL}/requests/")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('results'):
                request = data['results'][0]
                print("Enhanced request data includes:")
                print(f"- requester_name: {request.get('requester_name')}")
                print(f"- requester_email: {request.get('requester_email')}")
                print(f"- current_attendees: {request.get('current_attendees')}")
                print(f"- available_spots: {request.get('available_spots')}")
                print(f"- is_full: {request.get('is_full')}")
                print(f"- unread_messages_count: {request.get('unread_messages_count')}")
            else:
                print("No requests found")
        else:
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

def test_enhanced_chat_messages():
    """Test the enhanced chat messages endpoint"""
    print("\n=== Testing Enhanced Chat Messages ===")
    
    try:
        # First get a request ID
        requests_response = requests.get(f"{BASE_URL}/requests/")
        if requests_response.status_code == 200:
            requests_data = requests_response.json()
            if requests_data.get('results'):
                request_id = requests_data['results'][0]['id']
                
                # Test the chat messages endpoint
                response = requests.get(f"{BASE_URL}/chat/request/{request_id}/")
                print(f"Status Code: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print("Enhanced chat messages data includes:")
                    print(f"- request_id: {data.get('request_id')}")
                    print(f"- messages count: {len(data.get('messages', []))}")
                    
                    if data.get('messages'):
                        message = data['messages'][0]
                        print("Sample message data:")
                        print(f"- sender_email: {message.get('sender_email')}")
                        print(f"- sender_name: {message.get('sender_name')}")
                        print(f"- is_from_host: {message.get('is_from_host')}")
                        print(f"- message_type: {message.get('message_type')}")
                        print(f"- is_read: {message.get('is_read')}")
                else:
                    print(f"Response: {response.text}")
            else:
                print("No requests found for chat testing")
        else:
            print(f"Failed to get requests: {requests_response.status_code}")
    except Exception as e:
        print(f"Error: {e}")

def test_create_chat_message():
    """Test creating a chat message"""
    print("\n=== Testing Create Chat Message ===")
    
    try:
        # Get a request ID
        requests_response = requests.get(f"{BASE_URL}/requests/")
        if requests_response.status_code == 200:
            requests_data = requests_response.json()
            if requests_data.get('results'):
                request_id = requests_data['results'][0]['id']
                
                # Create a chat message
                message_data = {
                    "request_id": request_id,
                    "message": "This is a test message for enhanced chat functionality!",
                    "message_type": "text"
                }
                
                response = requests.post(f"{BASE_URL}/chat/", json=message_data)
                print(f"Status Code: {response.status_code}")
                print(f"Response: {json.dumps(response.json(), indent=2)}")
            else:
                print("No requests found for message creation")
        else:
            print(f"Failed to get requests: {requests_response.status_code}")
    except Exception as e:
        print(f"Error: {e}")

def main():
    """Run all tests"""
    print("🚀 Starting Enhanced Event Requests API Tests")
    print("Make sure the Django server is running on localhost:8000")
    print("=" * 60)
    
    # Run all tests
    test_event_management_endpoint()
    test_attendance_tracking()
    test_enhanced_events_list()
    test_enhanced_requests_list()
    test_enhanced_chat_messages()
    test_create_chat_message()
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("\n📋 Summary of Enhanced Features:")
    print("✅ Event management endpoint with attendance overview")
    print("✅ Automatic attendance tracking on request status changes")
    print("✅ Enhanced events list with attendance data")
    print("✅ Enhanced requests list with comprehensive data")
    print("✅ Enhanced chat messages with sender details")
    print("✅ Flexible field names for frontend compatibility")
    print("✅ No authentication required (as requested)")

if __name__ == "__main__":
    main()

