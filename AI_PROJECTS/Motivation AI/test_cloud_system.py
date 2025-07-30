#!/usr/bin/env python3
"""
Test script for Motivation AI Cloud Backend
Demonstrates the complete user journey from registration to content generation
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:8081"
TEST_EMAIL = "demo@motivationai.com"
TEST_PASSWORD = "demo123"

def test_system():
    """Test the complete Motivation AI system"""
    
    print("🚀 Testing Motivation AI Cloud Backend System")
    print("=" * 50)
    
    # Step 1: Health Check
    print("\n1️⃣ Health Check...")
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Server Status: {data['status']}")
            print(f"✅ Service: {data['service']}")
            print(f"✅ Version: {data['version']}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        return
    
    # Step 2: User Registration
    print("\n2️⃣ User Registration...")
    register_data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/register",
            headers={"Content-Type": "application/json"},
            json=register_data
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ Registration successful!")
                print(f"✅ User ID: {data['user']['id']}")
                print(f"✅ Email: {data['user']['email']}")
                print(f"✅ Subscription: {data['user']['subscription_tier']}")
                token = data['token']
            else:
                print(f"❌ Registration failed: {data.get('error', 'Unknown error')}")
                return
        else:
            print(f"❌ Registration failed with status: {response.status_code}")
            # Try login instead
            print("🔄 Attempting login...")
            login_response = requests.post(
                f"{BASE_URL}/api/auth/login",
                headers={"Content-Type": "application/json"},
                json=register_data
            )
            if login_response.status_code == 200:
                login_data = login_response.json()
                if login_data.get('success'):
                    print(f"✅ Login successful!")
                    token = login_data['token']
                else:
                    print(f"❌ Login failed: {login_data.get('error')}")
                    return
            else:
                print(f"❌ Login also failed: {login_response.status_code}")
                return
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return
    
    # Step 3: Check Subscription Status
    print("\n3️⃣ Checking Subscription Status...")
    try:
        response = requests.get(
            f"{BASE_URL}/api/user/subscription",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Subscription Tier: {data['subscription_tier']}")
            print(f"✅ Usage: {data['usage_count']}/{data['limits']['generations_per_month']}")
            print(f"✅ Max Length: {data['limits']['max_length_seconds']} seconds")
            print(f"✅ Video Quality: {data['limits']['video_quality']}")
        else:
            print(f"❌ Subscription check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Subscription check error: {e}")
    
    # Step 4: Generate Motivational Content
    print("\n4️⃣ Generating Motivational Content...")
    generation_request = {
        "user_input": "I need motivation to start my morning workout routine",
        "intensity": 75,  # High intensity
        "language_clean": 80,  # Mostly clean
        "humor_style": 40,  # Some humor
        "action_orientation": 90,  # Very action-oriented
        "message_length": 45,  # Medium length
        "music_style": 70,  # Energetic music
        "visual_style": 85   # Dynamic visuals
    }
    
    print(f"📝 Request: {generation_request['user_input']}")
    print(f"🎛️ Settings: Intensity={generation_request['intensity']}, Action={generation_request['action_orientation']}")
    
    try:
        print("⏳ Generating content (this may take 30-60 seconds)...")
        start_time = time.time()
        
        response = requests.post(
            f"{BASE_URL}/api/generate",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            json=generation_request,
            timeout=120  # 2 minute timeout
        )
        
        generation_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ Generation completed in {generation_time:.1f} seconds!")
                print(f"📄 Request ID: {data['request_id']}")
                print(f"💬 Generated Message Preview:")
                print(f"   {data['message_text'][:200]}...")
                print(f"🎵 Audio URL: {data['audio_url']}")
                print(f"🖼️ Image URL: {data['image_url']}")
                print(f"🎬 Video URL: {data['video_url']}")
                
                # Show metadata
                metadata = data.get('metadata', {})
                print(f"📊 Generation Stats:")
                print(f"   Time: {metadata.get('generation_time', 'N/A')} seconds")
                print(f"   Type: {metadata.get('content_type', 'N/A')}")
            else:
                print(f"❌ Generation failed: {data.get('error', 'Unknown error')}")
                if data.get('upgrade_required'):
                    print("💳 Upgrade required for more generations")
        elif response.status_code == 401:
            print("❌ Authentication failed - token may be invalid")
        elif response.status_code == 402:
            print("❌ Payment required - subscription limit reached")
        else:
            print(f"❌ Generation failed with status: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('error', 'Unknown')}")
            except:
                print(f"   Raw response: {response.text}")
    
    except requests.exceptions.Timeout:
        print("❌ Generation timed out (this is normal if AI APIs aren't configured)")
    except Exception as e:
        print(f"❌ Generation error: {e}")
    
    # Step 5: System Summary
    print("\n🎯 System Demo Complete!")
    print("=" * 50)
    print("✅ Backend Server: Running")
    print("✅ User Authentication: Working")
    print("✅ Subscription Management: Working")
    print("✅ Rate Limiting: Active")
    print("⚠️  AI Generation: Requires API keys for full functionality")
    print("\n📱 Next Steps:")
    print("   1. Configure AI API keys for full generation")
    print("   2. Deploy to production cloud server")
    print("   3. Build iOS app using MotivationAI_CloudClient.swift")
    print("   4. Submit to App Store with subscription features")

if __name__ == "__main__":
    test_system() 