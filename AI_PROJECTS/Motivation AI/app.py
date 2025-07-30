from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import os
from motivational_ai_agent import MotivationalAIAgent, MessagePreferences
import json
import requests # Added for admin endpoints

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize the AI agent
ai_agent = MotivationalAIAgent()

# Configuration storage (in production, use a proper database)
app_config = {
    'anthropic_api_key': '',
    'elevenlabs_api_key': '',
    'leonardo_api_key': '',
    'stripe_secret_key': '',
    'aws_access_key_id': '',
    'aws_secret_access_key': '',
    's3_bucket': '',
    'app_name': 'Motivation AI',
    'server_port': 8080,
    'debug_mode': False,
    'rate_limiting': True,
    'max_length': 120,
    'video_quality': '1080p',
    'content_moderation': 'moderate'
}

@app.route('/')
def index():
    """Serve the main web interface"""
    try:
        with open('web_interface.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
        return html_content
    except FileNotFoundError:
        return jsonify({'error': 'Web interface file not found'}), 404

@app.route('/generate_message', methods=['POST'])
def generate_message():
    """Generate a motivational message based on user preferences"""
    try:
        # Get JSON data from request
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        if 'user_input' not in data or not data['user_input'].strip():
            return jsonify({'error': 'User input is required'}), 400
        
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
        
        # Generate the message using AI agent
        result = ai_agent.generate_message(preferences)
        
        # Format the response
        response = {
            'message_text': result['message_text'],
            'style': result['style'],
            'music_style': result['music_style'],
            'visual_style': result['visual_style'],
            'background_image': result['background_image'],
            'audio_file': result.get('audio_file', ''),
            'success': True
        }
        
        return jsonify(response)
        
    except Exception as e:
        print(f"Error generating message: {e}")
        return jsonify({
            'error': 'Failed to generate message',
            'message': str(e),
            'success': False
        }), 500

@app.route('/api/styles', methods=['GET'])
def get_available_styles():
    """Get list of available message styles"""
    styles = [
        {'id': 'yoga_mindful', 'name': 'Yoga & Mindful', 'description': 'Gentle, compassionate, zen-like approach'},
        {'id': 'comedy_clean', 'name': 'Clean Comedy', 'description': 'Humorous but family-friendly motivation'},
        {'id': 'comedy_raunchy', 'name': 'Edgy Comedy', 'description': 'Raw humor with adult themes'},
        {'id': 'rise_grind', 'name': 'Rise & Grind', 'description': 'Energetic, enthusiastic hustle mentality'},
        {'id': 'drill_sergeant', 'name': 'Drill Sergeant', 'description': 'Military-style tough love without excessive profanity'},
        {'id': 'stay_hard', 'name': 'Stay Hard', 'description': 'David Goggins ultra-intense mental toughness'}
    ]
    return jsonify(styles)

@app.route('/api/samples/<style>', methods=['GET'])
def get_sample_messages(style):
    """Get sample messages for a specific style"""
    try:
        style_samples = ai_agent._get_style_samples(ai_agent.MessageStyle(style))
        return jsonify({
            'style': style,
            'samples': style_samples[:3]  # Return first 3 samples
        })
    except Exception as e:
        return jsonify({'error': f'Style not found: {style}'}), 404

@app.route('/api/test', methods=['GET'])
def test_api():
    """Test endpoint to verify API is working"""
    return jsonify({
        'status': 'API is working!',
        'agent_loaded': ai_agent is not None,
        'sample_messages_loaded': len(ai_agent.sample_messages) > 0 if ai_agent else False
    })

@app.route('/demo', methods=['POST'])
def demo_generation():
    """Demo endpoint that doesn't require OpenAI API"""
    try:
        data = request.get_json()
        
        if not data or 'user_input' not in data:
            return jsonify({'error': 'User input is required'}), 400
        
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
        
        # Use fallback generation (doesn't require OpenAI API)
        style = ai_agent.determine_message_style(preferences)
        message_text = ai_agent._generate_fallback_message(preferences, style)
        
        # Build response similar to full generation
        response = {
            'message_text': message_text,
            'style': style.value,
            'music_style': ai_agent._determine_music_style(preferences),
            'visual_style': ai_agent._determine_visual_style(preferences),
            'background_image': ai_agent._select_background_image(preferences),
            'audio_file': ai_agent._select_audio_file(preferences),
            'success': True,
            'demo_mode': True
        }
        
        return jsonify(response)
        
    except Exception as e:
        print(f"Error in demo generation: {e}")
        return jsonify({
            'error': 'Failed to generate demo message',
            'message': str(e),
            'success': False
        }), 500

# ADMIN ROUTES

@app.route('/admin')
def admin_panel():
    """Serve the admin panel"""
    with open('admin_panel.html', 'r') as f:
        return f.read()

@app.route('/admin/get-config', methods=['GET'])
def get_admin_config():
    """Get current configuration (masked sensitive data)"""
    masked_config = app_config.copy()
    
    # Mask sensitive keys
    for key in ['anthropic_api_key', 'elevenlabs_api_key', 'leonardo_api_key', 
                'stripe_secret_key', 'aws_access_key_id', 'aws_secret_access_key']:
        if masked_config[key]:
            masked_config[key] = masked_config[key][:8] + '...' + masked_config[key][-4:] if len(masked_config[key]) > 12 else '***'
    
    return jsonify(masked_config)

@app.route('/admin/save-anthropic', methods=['POST'])
def save_anthropic_config():
    """Save Anthropic API configuration"""
    try:
        data = request.get_json()
        if data and 'api_key' in data:
            app_config['anthropic_api_key'] = data['api_key']
            # In production, save to secure storage
            return jsonify({'success': True, 'message': 'Anthropic configuration saved'})
        return jsonify({'success': False, 'error': 'Invalid data'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/admin/save-elevenlabs', methods=['POST'])
def save_elevenlabs_config():
    """Save ElevenLabs API configuration"""
    try:
        data = request.get_json()
        if data and 'api_key' in data:
            app_config['elevenlabs_api_key'] = data['api_key']
            if 'model' in data:
                app_config['elevenlabs_model'] = data['model']
            return jsonify({'success': True, 'message': 'ElevenLabs configuration saved'})
        return jsonify({'success': False, 'error': 'Invalid data'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/admin/save-leonardo', methods=['POST'])
def save_leonardo_config():
    """Save Leonardo AI API configuration"""
    try:
        data = request.get_json()
        if data and 'api_key' in data:
            app_config['leonardo_api_key'] = data['api_key']
            if 'model' in data:
                app_config['leonardo_model'] = data['model']
            return jsonify({'success': True, 'message': 'Leonardo AI configuration saved'})
        return jsonify({'success': False, 'error': 'Invalid data'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/admin/test-anthropic', methods=['POST'])
def test_anthropic_api():
    """Test Anthropic API connection"""
    try:
        data = request.get_json()
        api_key = data.get('api_key', '')
        
        if not api_key:
            return jsonify({'success': False, 'error': 'API key required'}), 400
        
        # Simple test request to Anthropic
        headers = {
            'Content-Type': 'application/json',
            'x-api-key': api_key,
            'anthropic-version': '2023-06-01'
        }
        
        test_data = {
            'model': 'claude-3-sonnet-20240229',
            'max_tokens': 10,
            'messages': [{'role': 'user', 'content': 'Hello'}]
        }
        
        response = requests.post(
            'https://api.anthropic.com/v1/messages',
            headers=headers,
            json=test_data,
            timeout=10
        )
        
        if response.status_code == 200:
            return jsonify({'success': True, 'message': 'Anthropic API connection successful'})
        else:
            return jsonify({'success': False, 'error': f'API returned status {response.status_code}'}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/admin/test-elevenlabs', methods=['POST'])
def test_elevenlabs_api():
    """Test ElevenLabs API connection"""
    try:
        data = request.get_json()
        api_key = data.get('api_key', '')
        
        if not api_key:
            return jsonify({'success': False, 'error': 'API key required'}), 400
        
        # Test by getting voices list
        headers = {'xi-api-key': api_key}
        response = requests.get(
            'https://api.elevenlabs.io/v1/voices',
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            return jsonify({'success': True, 'message': 'ElevenLabs API connection successful'})
        else:
            return jsonify({'success': False, 'error': f'API returned status {response.status_code}'}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/admin/test-leonardo', methods=['POST'])
def test_leonardo_api():
    """Test Leonardo AI API connection"""
    try:
        data = request.get_json()
        api_key = data.get('api_key', '')
        
        if not api_key:
            return jsonify({'success': False, 'error': 'API key required'}), 400
        
        # Test by getting user info
        headers = {
            'accept': 'application/json',
            'authorization': f'Bearer {api_key}'
        }
        
        response = requests.get(
            'https://cloud.leonardo.ai/api/rest/v1/me',
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            return jsonify({'success': True, 'message': 'Leonardo AI API connection successful'})
        else:
            return jsonify({'success': False, 'error': f'API returned status {response.status_code}'}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/admin/save-app-settings', methods=['POST'])
def save_app_settings():
    """Save general app settings"""
    try:
        data = request.get_json()
        
        # Update app configuration
        for key in ['app_name', 'server_port', 'debug_mode', 'rate_limiting', 
                   'max_length', 'video_quality', 'content_moderation']:
            if key in data:
                app_config[key] = data[key]
        
        return jsonify({'success': True, 'message': 'App settings saved'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/admin/system-status', methods=['GET'])
def get_system_status():
    """Get system status information"""
    import psutil
    import time
    
    try:
        # Get system metrics
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        status = {
            'server_status': 'online',
            'uptime': time.time() - psutil.boot_time(),
            'memory_usage': f"{memory.percent}%",
            'memory_total': f"{memory.total / (1024**3):.1f} GB",
            'disk_usage': f"{disk.percent}%",
            'disk_total': f"{disk.total / (1024**3):.1f} GB",
            'api_status': {
                'anthropic': bool(app_config.get('anthropic_api_key')),
                'elevenlabs': bool(app_config.get('elevenlabs_api_key')),
                'leonardo': bool(app_config.get('leonardo_api_key'))
            }
        }
        
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/restart', methods=['POST'])
def restart_server():
    """Restart the server (placeholder)"""
    try:
        # In production, implement proper restart mechanism
        return jsonify({'success': True, 'message': 'Server restart initiated'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Check if running in production or development
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    port = int(os.environ.get('PORT', 5000))
    
    print("🚀 Starting Motivational AI Server...")
    print(f"📱 Web interface will be available at: http://localhost:{port}")
    print(f"🤖 API endpoint: http://localhost:{port}/generate_message")
    print(f"🧪 Test endpoint: http://localhost:{port}/api/test")
    print(f"🎭 Demo endpoint (no API key needed): http://localhost:{port}/demo")
    
    # Check if sample messages loaded
    if ai_agent and len(ai_agent.sample_messages) > 0:
        print(f"✅ Loaded {len(ai_agent.sample_messages)} style categories with sample messages")
    else:
        print("⚠️  Warning: No sample messages loaded. Check Messages/ directory.")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug_mode
    ) 