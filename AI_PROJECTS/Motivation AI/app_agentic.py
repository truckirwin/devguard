from flask import Flask, request, jsonify, send_file, render_template_string
from flask_cors import CORS
import os
import asyncio
import json
from datetime import datetime
from pathlib import Path

# Import our agentic AI service
from agentic_ai_service import AgenticAIService, MessagePreferences

app = Flask(__name__)
CORS(app)

# Initialize the agentic AI service
agentic_ai = AgenticAIService()

@app.route('/')
def index():
    """Serve the web interface for agentic AI generation"""
    with open('web_interface.html', 'r') as f:
        return f.read()

@app.route('/generate_agentic_package', methods=['POST'])
def generate_agentic_package():
    """Generate a complete motivational package using agentic AI"""
    try:
        # Get JSON data from request
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided', 'success': False}), 400
        
        # Validate required fields
        if 'user_input' not in data or not data['user_input'].strip():
            return jsonify({'error': 'User input is required', 'success': False}), 400
        
        # Create MessagePreferences object
        preferences = MessagePreferences(
            intensity=data.get('intensity', 50),
            language_clean=data.get('language_clean', 50),
            humor_style=data.get('humor_style', 50),
            action_orientation=data.get('action_orientation', 50),
            message_length=data.get('message_length', 50),
            music_style=data.get('music_style', 50),
            visual_style=data.get('visual_style', 50),
            user_input=data['user_input'].strip()
        )
        
        # Check if API keys are configured
        missing_keys = []
        if not agentic_ai.anthropic_api_key:
            missing_keys.append('ANTHROPIC_API_KEY')
        if not agentic_ai.elevenlabs_api_key:
            missing_keys.append('ELEVENLABS_API_KEY')
        if not agentic_ai.leonardo_api_key:
            missing_keys.append('LEONARDO_API_KEY')
        
        if missing_keys:
            return jsonify({
                'error': f'Missing API keys: {", ".join(missing_keys)}',
                'message': 'Please set the required environment variables',
                'success': False,
                'demo_available': True
            }), 400
        
        # Generate the complete package using agentic AI
        print(f"🚀 Starting agentic AI generation...")
        
        # Run the async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                agentic_ai.generate_complete_motivation_package(preferences)
            )
        finally:
            loop.close()
        
        # Format the response with download URLs
        response = {
            'message_text': result.message_text,
            'audio_url': f'/download/audio/{Path(result.audio_file_path).name}',
            'image_url': f'/download/image/{Path(result.image_file_path).name}',
            'captions_json': result.captions_json,
            'package_url': f'/download/package/{Path(result.package_zip_path).name}',
            'metadata': result.generation_metadata,
            'success': True,
            'agentic_mode': True
        }
        
        print(f"✅ Agentic AI package generated successfully!")
        return jsonify(response)
        
    except Exception as e:
        print(f"❌ Error generating agentic package: {e}")
        return jsonify({
            'error': 'Failed to generate agentic package',
            'message': str(e),
            'success': False
        }), 500

@app.route('/generate_demo', methods=['POST'])
def generate_demo():
    """Generate a demo package without API calls (fallback)"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided', 'success': False}), 400
        
        if 'user_input' not in data or not data['user_input'].strip():
            return jsonify({'error': 'User input is required', 'success': False}), 400
        
        # Create a demo response based on preferences
        preferences = MessagePreferences(
            intensity=data.get('intensity', 50),
            language_clean=data.get('language_clean', 50),
            humor_style=data.get('humor_style', 50),
            action_orientation=data.get('action_orientation', 50),
            message_length=data.get('message_length', 50),
            music_style=data.get('music_style', 50),
            visual_style=data.get('visual_style', 50),
            user_input=data['user_input'].strip()
        )
        
        # Generate a demo message based on preferences
        demo_message = generate_demo_message(preferences)
        
        response = {
            'message_text': demo_message,
            'audio_url': '',
            'image_url': '',
            'captions_json': {'segments': []},
            'package_url': '',
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'mode': 'demo',
                'user_input': preferences.user_input
            },
            'success': True,
            'demo_mode': True,
            'message': 'Demo mode - configure API keys for full agentic generation'
        }
        
        return jsonify(response)
        
    except Exception as e:
        print(f"Error generating demo: {e}")
        return jsonify({
            'error': 'Failed to generate demo',
            'message': str(e),
            'success': False
        }), 500

@app.route('/download/<file_type>/<filename>')
def download_file(file_type, filename):
    """Download generated files"""
    try:
        file_path = agentic_ai.output_dir / filename
        
        if not file_path.exists():
            return jsonify({'error': 'File not found'}), 404
        
        # Determine mime type based on file type
        mime_types = {
            'audio': 'audio/mpeg',
            'image': 'image/jpeg',
            'package': 'application/zip',
            'captions': 'application/json'
        }
        
        mime_type = mime_types.get(file_type, 'application/octet-stream')
        
        return send_file(
            file_path,
            mimetype=mime_type,
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        print(f"Error downloading file: {e}")
        return jsonify({'error': 'Download failed'}), 500

@app.route('/api/status', methods=['GET'])
def api_status():
    """Check API configuration status"""
    status = {
        'anthropic_configured': bool(agentic_ai.anthropic_api_key),
        'elevenlabs_configured': bool(agentic_ai.elevenlabs_api_key),
        'leonardo_configured': bool(agentic_ai.leonardo_api_key),
        'output_directory': str(agentic_ai.output_dir),
        'voice_profiles_available': len(agentic_ai.voice_profiles)
    }
    
    status['fully_configured'] = all([
        status['anthropic_configured'],
        status['elevenlabs_configured'],
        status['leonardo_configured']
    ])
    
    return jsonify(status)

@app.route('/api/voices', methods=['GET'])
def get_voices():
    """Get available voice profiles"""
    return jsonify({
        'voices': list(agentic_ai.voice_profiles.keys()),
        'voice_mapping': agentic_ai.voice_profiles
    })

@app.route('/api/test', methods=['GET'])
def test_api():
    """Test API status"""
    return jsonify({
        'status': 'online',
        'service': 'Agentic Motivation AI',
        'timestamp': datetime.now().isoformat(),
        'agentic_features': [
            'Claude Sonnet message generation',
            'ElevenLabs audio synthesis',
            'Leonardo AI image generation',
            'Automated packaging',
            'Downloadable content'
        ]
    })

def generate_demo_message(preferences: MessagePreferences) -> str:
    """Generate a demo motivational message based on preferences"""
    
    topic = preferences.user_input
    
    # Style templates based on intensity
    if preferences.intensity > 80:
        template = f"""Listen up! {topic} isn't going to happen by itself. You've been making excuses long enough. Every second you waste is another second you're not becoming who you're meant to be. Stop talking, stop planning, stop hesitating. The time is NOW. Get up, get moving, and make {topic} your reality. No more tomorrow, no more next week. TODAY!"""
    
    elif preferences.intensity > 60:
        template = f"""It's time to take control of {topic}. You have everything you need inside you right now. The only thing standing between you and success is action. Stop letting fear make your decisions. Stop letting doubt write your story. You are capable of incredible things. Start with one step, then another. Your journey toward {topic} begins the moment you decide you're worth it. And you ARE worth it."""
    
    elif preferences.intensity > 40:
        template = f"""I believe in your ability to achieve {topic}. Every challenge you've faced has prepared you for this moment. When you feel like giving up, remember why you started. When progress feels slow, trust the process. Small consistent actions create extraordinary results. Your commitment to {topic} is an investment in your future self. Stay patient, stay focused, and keep moving forward."""
    
    elif preferences.intensity > 20:
        template = f"""Take a deep breath and trust yourself with {topic}. You don't have to be perfect, you just have to begin. Every step forward is progress, no matter how small. Be gentle with yourself as you work toward {topic}. Celebrate the small wins. Learn from the setbacks. Remember that growth happens in your own time, at your own pace. You've got this."""
    
    else:
        template = f"""Find peace in your journey toward {topic}. Like a river flowing gently toward the ocean, your path unfolds naturally when you align with your inner wisdom. Breathe deeply and trust the process. Each moment brings new opportunities for growth and understanding. Approach {topic} with compassion for yourself and openness to what emerges. You are exactly where you need to be."""
    
    # Add humor if requested
    if preferences.humor_style > 50:
        humor_additions = [
            " (And yes, that includes getting off the couch.)",
            " Your excuses called - they want a vacation too.",
            " Time to show life who's boss... spoiler alert: it's you!",
            " Your future self is already sending thank you notes."
        ]
        import random
        template += random.choice(humor_additions)
    
    return template

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print("🤖 Starting Agentic Motivation AI Server...")
    print(f"📱 Web interface available at: http://localhost:{port}")
    print(f"🚀 Agentic API endpoint: http://localhost:{port}/generate_agentic_package")
    print(f"🎭 Demo endpoint: http://localhost:{port}/generate_demo")
    print(f"📊 Status endpoint: http://localhost:{port}/api/status")
    
    # Check API configuration
    status = {
        'anthropic': bool(os.getenv('ANTHROPIC_API_KEY')),
        'elevenlabs': bool(os.getenv('ELEVENLABS_API_KEY')),
        'leonardo': bool(os.getenv('LEONARDO_API_KEY'))
    }
    
    if all(status.values()):
        print("✅ All API keys configured - full agentic mode available!")
    else:
        print("⚠️  Missing API keys - demo mode only:")
        for service, configured in status.items():
            print(f"   {service}: {'✅' if configured else '❌'}")
    
    app.run(host='0.0.0.0', port=port) 