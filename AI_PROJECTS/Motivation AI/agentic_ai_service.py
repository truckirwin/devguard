import os
import json
import requests
import asyncio
import aiohttp
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import base64
import zipfile
import tempfile
from pathlib import Path

@dataclass
class MessagePreferences:
    """User preferences for motivational message generation"""
    intensity: int  # 0=Chill, 100=Drill Sergeant
    language_clean: int  # 0=Dirty, 100=Clean
    humor_style: int  # 0=Clean, 100=Raunchy
    action_orientation: int  # 0=Yoga/Mindful, 100=Action-oriented
    message_length: int  # 0=Single Quote, 100=60 seconds
    music_style: int  # 0=Chill, 100=Rock and Roll
    visual_style: int  # 0=Still Image, 100=Active Video
    user_input: str  # User's text description

@dataclass
class GeneratedContent:
    """Container for all generated content"""
    message_text: str
    audio_file_path: str
    audio_url: str
    captions_json: dict
    image_file_path: str
    image_url: str
    package_zip_path: str
    generation_metadata: dict

class AgenticAIService:
    """Fully agentic AI service that orchestrates Claude, ElevenLabs, and Leonardo AI"""
    
    def __init__(self):
        # API Configuration
        self.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
        self.elevenlabs_api_key = os.getenv('ELEVENLABS_API_KEY')
        self.leonardo_api_key = os.getenv('LEONARDO_API_KEY')
        
        # API URLs
        self.anthropic_base_url = "https://api.anthropic.com/v1"
        self.elevenlabs_base_url = "https://api.elevenlabs.io/v1"
        self.leonardo_base_url = "https://cloud.leonardo.ai/api/rest/v1"
        
        # Voice IDs for ElevenLabs (you can customize these)
        self.voice_profiles = {
            'motivational_male': 'pNInz6obpgDQGcFmaJgB',  # Adam voice
            'motivational_female': 'EXAVITQu4vr4xnSDxMaL',  # Bella voice
            'drill_sergeant': 'VR6AewLTigWG4xSOukaG',  # Josh voice (more intense)
            'calm_yoga': 'ThT5KcBeYPX3keUQqHPh'  # Dorothy voice (calming)
        }
        
        # Output directories
        self.output_dir = Path("generated_content")
        self.output_dir.mkdir(exist_ok=True)
        
    async def generate_complete_motivation_package(self, preferences: MessagePreferences) -> GeneratedContent:
        """
        Generate a complete motivational package using agentic AI:
        1. Claude Sonnet generates the message
        2. ElevenLabs generates audio + captions
        3. Leonardo AI generates matching image
        4. Package everything into downloadable content
        """
        print(f"🚀 Starting agentic AI generation for: {preferences.user_input}")
        
        try:
            # Step 1: Generate motivational message with Claude Sonnet
            print("🧠 Generating message with Claude Sonnet...")
            message_text = await self._generate_message_with_claude(preferences)
            
            # Step 2: Generate audio and captions with ElevenLabs
            print("🎵 Generating audio with ElevenLabs...")
            audio_result = await self._generate_audio_with_elevenlabs(message_text, preferences)
            
            # Step 3: Generate matching image with Leonardo AI
            print("🎨 Generating image with Leonardo AI...")
            image_result = await self._generate_image_with_leonardo(message_text, preferences)
            
            # Step 4: Package everything together
            print("📦 Packaging complete motivational content...")
            package_result = await self._package_content(
                message_text, audio_result, image_result, preferences
            )
            
            print("✅ Agentic AI generation complete!")
            return package_result
            
        except Exception as e:
            print(f"❌ Error in agentic AI generation: {e}")
            raise
    
    async def _generate_message_with_claude(self, preferences: MessagePreferences) -> str:
        """Generate motivational message using Claude Sonnet"""
        
        # Determine message style and tone based on preferences
        style_descriptor = self._determine_style_descriptor(preferences)
        length_descriptor = self._determine_length_descriptor(preferences)
        
        prompt = f"""You are a world-class motivational speaker and coach. Create a powerful, personalized motivational message.

TOPIC: {preferences.user_input}

STYLE REQUIREMENTS:
- Tone: {style_descriptor}
- Length: {length_descriptor}
- Language: {'Clean and professional' if preferences.language_clean > 50 else 'Raw and authentic (some strong language OK)'}
- Approach: {'Action-oriented and energetic' if preferences.action_orientation > 50 else 'Mindful and reflective'}
- Humor: {'Include appropriate humor' if preferences.humor_style > 30 else 'Keep serious and focused'}

INSTRUCTIONS:
1. Make it deeply personal and relatable
2. Include specific, actionable advice
3. Use vivid imagery and metaphors
4. Create emotional resonance
5. End with a powerful call to action
6. Write as if speaking directly to someone who needs this message RIGHT NOW

The message should feel like it was crafted specifically for someone struggling with: {preferences.user_input}

Generate the motivational message now:"""

        headers = {
            'Content-Type': 'application/json',
            'x-api-key': self.anthropic_api_key,
            'anthropic-version': '2023-06-01'
        }
        
        data = {
            'model': 'claude-3-sonnet-20240229',
            'max_tokens': 1500,
            'messages': [
                {
                    'role': 'user',
                    'content': prompt
                }
            ]
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.anthropic_base_url}/messages",
                headers=headers,
                json=data
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result['content'][0]['text'].strip()
                else:
                    error_text = await response.text()
                    raise Exception(f"Claude API error: {response.status} - {error_text}")
    
    async def _generate_audio_with_elevenlabs(self, message_text: str, preferences: MessagePreferences) -> dict:
        """Generate audio and captions using ElevenLabs"""
        
        # Select voice based on preferences
        voice_id = self._select_voice(preferences)
        
        # Generate audio
        headers = {
            'Accept': 'audio/mpeg',
            'Content-Type': 'application/json',
            'xi-api-key': self.elevenlabs_api_key
        }
        
        data = {
            'text': message_text,
            'model_id': 'eleven_monolingual_v1',
            'voice_settings': {
                'stability': 0.5,
                'similarity_boost': 0.5,
                'style': 0.8 if preferences.intensity > 70 else 0.4,
                'use_speaker_boost': True
            }
        }
        
        # Generate audio file
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.elevenlabs_base_url}/text-to-speech/{voice_id}",
                headers=headers,
                json=data
            ) as response:
                if response.status == 200:
                    audio_content = await response.read()
                    
                    # Save audio file
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    audio_filename = f"motivation_audio_{timestamp}.mp3"
                    audio_path = self.output_dir / audio_filename
                    
                    with open(audio_path, 'wb') as f:
                        f.write(audio_content)
                    
                    # Generate captions JSON
                    captions = self._generate_captions(message_text)
                    captions_filename = f"motivation_captions_{timestamp}.json"
                    captions_path = self.output_dir / captions_filename
                    
                    with open(captions_path, 'w') as f:
                        json.dump(captions, f, indent=2)
                    
                    return {
                        'audio_path': str(audio_path),
                        'captions_path': str(captions_path),
                        'captions_data': captions,
                        'duration': len(message_text.split()) * 0.5  # Rough estimate
                    }
                else:
                    error_text = await response.text()
                    raise Exception(f"ElevenLabs API error: {response.status} - {error_text}")
    
    async def _generate_image_with_leonardo(self, message_text: str, preferences: MessagePreferences) -> dict:
        """Generate matching motivational image using Leonardo AI"""
        
        # Analyze message to determine image style
        image_prompt = self._create_image_prompt(message_text, preferences)
        
        headers = {
            'accept': 'application/json',
            'content-type': 'application/json',
            'authorization': f'Bearer {self.leonardo_api_key}'
        }
        
        # Determine model and settings based on preferences
        model_id = "6bef9f1b-29cb-40c7-b9df-32b51c1f67d3"  # Leonardo Creative model
        
        data = {
            'height': 1024,
            'width': 1024,
            'modelId': model_id,
            'prompt': image_prompt,
            'negative_prompt': 'low quality, blurry, distorted, text overlay, watermark',
            'num_images': 1,
            'guidance_scale': 7,
            'num_inference_steps': 30,
            'presetStyle': 'CINEMATIC'
        }
        
        # Generate image
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.leonardo_base_url}/generations",
                headers=headers,
                json=data
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    generation_id = result['sdGenerationJob']['generationId']
                    
                    # Poll for completion
                    image_url = await self._poll_leonardo_generation(generation_id)
                    
                    # Download and save image
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    image_filename = f"motivation_image_{timestamp}.jpg"
                    image_path = self.output_dir / image_filename
                    
                    await self._download_image(image_url, image_path)
                    
                    return {
                        'image_path': str(image_path),
                        'image_url': image_url,
                        'prompt_used': image_prompt
                    }
                else:
                    error_text = await response.text()
                    raise Exception(f"Leonardo AI API error: {response.status} - {error_text}")
    
    async def _poll_leonardo_generation(self, generation_id: str) -> str:
        """Poll Leonardo AI until image generation is complete"""
        headers = {
            'accept': 'application/json',
            'authorization': f'Bearer {self.leonardo_api_key}'
        }
        
        max_attempts = 30
        attempt = 0
        
        async with aiohttp.ClientSession() as session:
            while attempt < max_attempts:
                await asyncio.sleep(2)  # Wait 2 seconds between polls
                
                async with session.get(
                    f"{self.leonardo_base_url}/generations/{generation_id}",
                    headers=headers
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        if result['generations_by_pk']['status'] == 'COMPLETE':
                            images = result['generations_by_pk']['generated_images']
                            if images:
                                return images[0]['url']
                        elif result['generations_by_pk']['status'] == 'FAILED':
                            raise Exception("Leonardo AI generation failed")
                
                attempt += 1
        
        raise Exception("Leonardo AI generation timed out")
    
    async def _download_image(self, image_url: str, save_path: Path):
        """Download image from URL and save locally"""
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as response:
                if response.status == 200:
                    image_content = await response.read()
                    with open(save_path, 'wb') as f:
                        f.write(image_content)
                else:
                    raise Exception(f"Failed to download image: {response.status}")
    
    async def _package_content(self, message_text: str, audio_result: dict, 
                             image_result: dict, preferences: MessagePreferences) -> GeneratedContent:
        """Package all generated content into a downloadable zip file"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        package_name = f"motivation_package_{timestamp}"
        zip_path = self.output_dir / f"{package_name}.zip"
        
        # Create metadata
        metadata = {
            'generated_at': datetime.now().isoformat(),
            'user_input': preferences.user_input,
            'preferences': {
                'intensity': preferences.intensity,
                'language_clean': preferences.language_clean,
                'humor_style': preferences.humor_style,
                'action_orientation': preferences.action_orientation,
                'message_length': preferences.message_length,
                'music_style': preferences.music_style,
                'visual_style': preferences.visual_style
            },
            'content': {
                'message_text': message_text,
                'audio_duration': audio_result.get('duration', 0),
                'image_prompt': image_result.get('prompt_used', '')
            }
        }
        
        # Create zip package
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add message text
            zipf.writestr(f"{package_name}_message.txt", message_text)
            
            # Add audio file
            zipf.write(audio_result['audio_path'], f"{package_name}_audio.mp3")
            
            # Add captions
            zipf.write(audio_result['captions_path'], f"{package_name}_captions.json")
            
            # Add image
            zipf.write(image_result['image_path'], f"{package_name}_image.jpg")
            
            # Add metadata
            zipf.writestr(f"{package_name}_metadata.json", json.dumps(metadata, indent=2))
        
        return GeneratedContent(
            message_text=message_text,
            audio_file_path=audio_result['audio_path'],
            audio_url="",  # Will be set by Flask route
            captions_json=audio_result['captions_data'],
            image_file_path=image_result['image_path'],
            image_url=image_result['image_url'],
            package_zip_path=str(zip_path),
            generation_metadata=metadata
        )
    
    def _determine_style_descriptor(self, preferences: MessagePreferences) -> str:
        """Determine message style based on preferences"""
        if preferences.intensity > 80:
            return "Ultra-intense drill sergeant style - commanding, demanding, no-nonsense"
        elif preferences.intensity > 60:
            return "Strong motivational energy - powerful but encouraging"
        elif preferences.intensity > 40:
            return "Balanced motivation - firm but supportive"
        elif preferences.intensity > 20:
            return "Gentle encouragement - warm and understanding"
        else:
            return "Peaceful and calming - mindful and nurturing"
    
    def _determine_length_descriptor(self, preferences: MessagePreferences) -> str:
        """Determine message length based on preferences"""
        if preferences.message_length > 80:
            return "Long-form speech (45-60 seconds when spoken)"
        elif preferences.message_length > 60:
            return "Medium speech (30-45 seconds when spoken)"
        elif preferences.message_length > 40:
            return "Short speech (15-30 seconds when spoken)"
        elif preferences.message_length > 20:
            return "Brief message (10-15 seconds when spoken)"
        else:
            return "Quick quote or mantra (5-10 seconds when spoken)"
    
    def _select_voice(self, preferences: MessagePreferences) -> str:
        """Select ElevenLabs voice based on preferences"""
        if preferences.intensity > 70:
            return self.voice_profiles['drill_sergeant']
        elif preferences.action_orientation < 30:
            return self.voice_profiles['calm_yoga']
        elif preferences.user_input.lower().find('female') != -1:
            return self.voice_profiles['motivational_female']
        else:
            return self.voice_profiles['motivational_male']
    
    def _generate_captions(self, message_text: str) -> dict:
        """Generate closed captions JSON for the message"""
        words = message_text.split()
        duration_per_word = 0.5  # Rough estimate
        
        captions = {
            "version": "1.0",
            "language": "en",
            "segments": []
        }
        
        current_time = 0.0
        for i, word in enumerate(words):
            segment = {
                "id": i,
                "start": round(current_time, 2),
                "end": round(current_time + duration_per_word, 2),
                "text": word
            }
            captions["segments"].append(segment)
            current_time += duration_per_word
        
        return captions
    
    def _create_image_prompt(self, message_text: str, preferences: MessagePreferences) -> str:
        """Create image generation prompt based on message content and preferences"""
        
        # Analyze message content for visual themes
        message_lower = message_text.lower()
        
        # Base style
        if preferences.visual_style > 70:
            base_style = "dynamic action scene, movement, energy"
        else:
            base_style = "serene, contemplative, peaceful scene"
        
        # Determine scene based on message content
        if any(word in message_lower for word in ['morning', 'dawn', 'sunrise', 'wake']):
            scene = "beautiful sunrise, golden hour, new beginnings"
        elif any(word in message_lower for word in ['mountain', 'climb', 'peak', 'summit']):
            scene = "majestic mountain landscape, climbing, achievement"
        elif any(word in message_lower for word in ['ocean', 'wave', 'sea', 'water']):
            scene = "powerful ocean waves, vast seascape, strength of nature"
        elif any(word in message_lower for word in ['forest', 'tree', 'nature', 'green']):
            scene = "lush forest path, natural growth, life force"
        elif any(word in message_lower for word in ['city', 'urban', 'street', 'building']):
            scene = "inspiring urban landscape, modern achievement, progress"
        elif any(word in message_lower for word in ['run', 'fitness', 'exercise', 'workout']):
            scene = "athletic achievement, fitness journey, human potential"
        else:
            scene = "inspirational landscape symbolizing growth and potential"
        
        # Intensity and mood
        if preferences.intensity > 70:
            mood = "dramatic lighting, intense atmosphere, powerful energy"
        elif preferences.intensity > 40:
            mood = "warm inspiring light, hopeful atmosphere, encouraging energy"
        else:
            mood = "soft gentle lighting, peaceful atmosphere, calming energy"
        
        # Combine into final prompt
        prompt = f"{scene}, {base_style}, {mood}, cinematic composition, high quality, motivational and inspiring, 4K resolution, professional photography style"
        
        return prompt 