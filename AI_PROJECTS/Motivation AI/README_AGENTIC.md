# 🤖 Agentic Motivation AI

**A fully autonomous AI system that generates complete motivational packages using Claude Sonnet, ElevenLabs, and Leonardo AI.**

## 🌟 What This Does

This agentic AI system creates **complete motivational experiences** by orchestrating multiple AI services:

1. **🧠 Claude Sonnet** generates personalized motivational messages
2. **🎵 ElevenLabs** converts text to high-quality speech with captions  
3. **🎨 Leonardo AI** creates matching motivational images
4. **📦 Automated Packaging** bundles everything into downloadable content

## ✨ Features

### 🎯 **Agentic AI Workflow**
- **Autonomous operation** - AI manages the entire generation pipeline
- **Multi-modal output** - Text, audio, images, and captions in one package
- **Intelligent voice selection** based on content intensity and style
- **Smart image prompting** that matches message themes
- **Automatic packaging** with metadata and organized file structure

### 🎛️ **Customization Controls**
- **Intensity**: Chill 😌 ↔ Drill Sergeant 💪
- **Language**: Raw 🤬 ↔ Clean 😇  
- **Humor**: Serious 😐 ↔ Funny 😂
- **Approach**: Mindful 🧘 ↔ Action ⚡
- **Length**: Quote 💬 ↔ Speech 📜
- **Music Style**: Chill 🎵 ↔ Rock 🎸
- **Visual Style**: Still 🖼️ ↔ Dynamic 🎬

### 📦 **Generated Package Contains**
- **Message text** (.txt) - The motivational content
- **Audio file** (.mp3) - Professional voice synthesis
- **Captions** (.json) - Precise word-level timing
- **Image** (.jpg) - AI-generated motivational artwork
- **Metadata** (.json) - Generation parameters and timestamps
- **Complete ZIP** - Everything bundled for easy download

## 🚀 Quick Start

### Option 1: Automated Setup
```bash
python3 setup_agentic_ai.py
./start_agentic_ai.sh
```

### Option 2: Manual Setup
```bash
# Install dependencies
pip install -r requirements_agentic.txt

# Configure API keys (create .env file)
ANTHROPIC_API_KEY=your_claude_key_here
ELEVENLABS_API_KEY=your_elevenlabs_key_here  
LEONARDO_API_KEY=your_leonardo_key_here
PORT=8080

# Create output directory
mkdir generated_content

# Start the server
python3 app_agentic.py
```

### 🌐 Access the Interface
Open **http://localhost:8080** in your browser

## 🔑 API Keys Required

### 🧠 **Claude Sonnet (Anthropic)**
- **Purpose**: Generates personalized motivational messages
- **Get key**: https://console.anthropic.com/
- **Features**: Context-aware messaging, style adaptation, emotional intelligence

### 🎵 **ElevenLabs** 
- **Purpose**: Converts text to professional-quality speech
- **Get key**: https://elevenlabs.io/
- **Features**: Multiple voice profiles, emotion control, captions generation

### 🎨 **Leonardo AI**
- **Purpose**: Creates motivational images that match message content
- **Get key**: https://leonardo.ai/
- **Features**: Content-aware prompting, cinematic quality, style control

## 🎭 Demo Mode

**No API keys?** The system includes a demo mode that:
- Generates template-based motivational messages
- Shows the full interface and workflow
- Demonstrates all customization options
- Perfect for testing and development

## 🏗️ Architecture

### 🔄 **Agentic Workflow**
```
User Input + Preferences
         ↓
🧠 Claude Sonnet Analysis
    → Generate message based on style, intensity, length
         ↓
🎵 ElevenLabs Synthesis  
    → Select voice profile based on preferences
    → Generate audio + word-level captions
         ↓
🎨 Leonardo AI Generation
    → Analyze message content for visual themes
    → Generate matching motivational image
         ↓
📦 Automated Packaging
    → Bundle all assets with metadata
    → Create downloadable ZIP package
```

### 🏗️ **Core Components**

- **`agentic_ai_service.py`** - Main orchestration engine
- **`app_agentic.py`** - Flask web server and API
- **`web_interface_agentic.html`** - Interactive web UI
- **`setup_agentic_ai.py`** - Automated setup and configuration

## 🎯 Use Cases

### 💼 **Professional**
- **Corporate training** - Generate motivational content for teams
- **Life coaching** - Create personalized client materials  
- **Content creation** - Produce social media motivation posts
- **Education** - Develop encouraging study materials

### 🏠 **Personal**
- **Daily motivation** - Custom morning affirmations
- **Fitness goals** - Workout encouragement packages
- **Habit building** - Personalized behavior change support
- **Overcoming challenges** - Specific situation guidance

## 🎨 Voice Profiles

The system intelligently selects voices based on your preferences:

- **🎯 Drill Sergeant** - High intensity, commanding tone
- **💪 Motivational Male** - Balanced, encouraging energy  
- **🌟 Motivational Female** - Warm, inspiring delivery
- **🧘 Calm Yoga** - Peaceful, mindful approach

## 🖼️ Image Generation

**Smart image prompting** analyzes your message content:

- **🌅 Morning themes** → Sunrise and new beginnings
- **🏔️ Challenge themes** → Mountains and achievement  
- **🌊 Flow themes** → Ocean and natural power
- **🏃 Action themes** → Athletic and fitness imagery
- **🏙️ Urban themes** → City and progress landscapes

## 📊 API Endpoints

### **Agentic Generation**
- `POST /generate_agentic_package` - Full AI pipeline
- `GET /api/status` - Check API configuration
- `GET /api/voices` - Available voice profiles

### **Demo & Testing**  
- `POST /generate_demo` - Demo mode generation
- `GET /api/test` - System health check

### **File Downloads**
- `GET /download/audio/<filename>` - Audio files
- `GET /download/image/<filename>` - Generated images  
- `GET /download/package/<filename>` - Complete packages

## 🔧 Configuration

### **Environment Variables**
```bash
# Required for full agentic mode
ANTHROPIC_API_KEY=sk-ant-xxxxx
ELEVENLABS_API_KEY=xxxxx  
LEONARDO_API_KEY=xxxxx

# Server configuration
PORT=8080
```

### **Voice Customization**
Modify `voice_profiles` in `agentic_ai_service.py`:
```python
self.voice_profiles = {
    'motivational_male': 'pNInz6obpgDQGcFmaJgB',
    'motivational_female': 'EXAVITQu4vr4xnSDxMaL', 
    'drill_sergeant': 'VR6AewLTigWG4xSOukaG',
    'calm_yoga': 'ThT5KcBeYPX3keUQqHPh'
}
```

## 🚀 Integration with Rise and Grind

This agentic AI system is designed to complement the Rise and Grind app:

- **Rise and Grind** - Pre-built motivational content with polished UI
- **Motivation AI** - Dynamic content generation with full customization

Both can run simultaneously on different simulator instances for comparison and different use cases.

## 🛠️ Development

### **Adding New AI Services**
1. Create service class in `agentic_ai_service.py`
2. Add API configuration to setup script
3. Integrate into the main workflow
4. Update web interface for new options

### **Customizing Generation**
- **Message styles** - Modify prompt templates in `_generate_message_with_claude()`
- **Voice selection** - Update logic in `_select_voice()`
- **Image prompts** - Enhance `_create_image_prompt()` function

### **Testing**
```bash
# Test individual components
python3 -c "from agentic_ai_service import AgenticAIService; print('Import successful')"

# Test full workflow (requires API keys)
curl -X POST http://localhost:8080/generate_demo -H "Content-Type: application/json" -d '{"user_input":"test motivation", "intensity":50}'
```

## 📦 Package Structure

```
Motivation AI/
├── agentic_ai_service.py      # Core agentic AI engine
├── app_agentic.py             # Flask web server
├── web_interface_agentic.html # Interactive UI
├── setup_agentic_ai.py        # Automated setup
├── requirements_agentic.txt   # Dependencies
├── generated_content/         # Output directory
│   ├── motivation_audio_*.mp3
│   ├── motivation_image_*.jpg
│   ├── motivation_captions_*.json
│   └── motivation_package_*.zip
└── .env                       # API configuration
```

## 🤝 Contributing

This agentic AI system is designed for:
- **Easy extension** - Add new AI services
- **Flexible customization** - Modify generation parameters  
- **Robust error handling** - Graceful fallbacks
- **Clear documentation** - Well-commented code

## 📄 License

Built for educational and personal use. Ensure compliance with:
- Anthropic's terms of service
- ElevenLabs' usage policies  
- Leonardo AI's licensing terms

## 🆘 Troubleshooting

### **"Missing API keys" error**
- Run `python3 setup_agentic_ai.py` to configure
- Check `.env` file exists and has correct format
- Verify API keys are valid and have sufficient credits

### **Generation fails**
- Check internet connection
- Verify API service status
- Review generated_content/ directory permissions
- Try demo mode to test basic functionality

### **Slow generation**
- Leonardo AI image generation takes 10-30 seconds
- ElevenLabs audio generation varies by length
- Claude Sonnet is typically fastest (2-5 seconds)

---

## 🎉 Ready to Create Amazing Motivational Content!

Run the setup, configure your API keys, and start generating personalized motivation packages that combine the power of multiple AI systems into cohesive, downloadable experiences!

**Your motivation journey, powered by agentic AI. 🚀** 