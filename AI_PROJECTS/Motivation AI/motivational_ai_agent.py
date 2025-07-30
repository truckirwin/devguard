import openai
import json
import random
from typing import Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum

@dataclass
class MessagePreferences:
    """User preferences collected from sliders (0-100 scale)"""
    intensity: int  # 0=Chill, 100=Drill Sergeant
    language_clean: int  # 0=Dirty, 100=Clean
    humor_style: int  # 0=Clean, 100=Raunchy
    action_orientation: int  # 0=Yoga/Mindful, 100=Action-oriented
    message_length: int  # 0=Single Quote, 100=60 seconds
    music_style: int  # 0=Chill, 100=Rock and Roll
    visual_style: int  # 0=Still Image, 100=Active Video
    user_input: str  # User's text description of what they want motivation for

class MessageStyle(Enum):
    YOGA_MINDFUL = "yoga_mindful"
    COMEDY_CLEAN = "comedy_clean"
    COMEDY_RAUNCHY = "comedy_raunchy"
    RISE_GRIND = "rise_grind"
    DRILL_SERGEANT = "drill_sergeant"
    STAY_HARD = "stay_hard"

class MotivationalAIAgent:
    """Agentic AI system for generating custom motivational messages"""
    
    def __init__(self, openai_api_key: str = None):
        if openai_api_key:
            openai.api_key = openai_api_key
        
        # Load sample messages from files for inspiration
        self.sample_messages = self._load_sample_messages()
        
    def _load_sample_messages(self) -> Dict[str, List[str]]:
        """Load sample messages from the Messages directory"""
        samples = {}
        
        message_files = {
            'yoga': 'Messages/NewYogaMessages.MD',
            'comedy': 'Messages/JobhuntComedyMessages.md',
            'rise_grind': 'Messages/RiseandGrindMessages.MD',
            'stay_hard': 'Messages/StayHardMessages.md',
            'coach': 'Messages/JobCoachMessages.md'
        }
        
        for style, filepath in message_files.items():
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Extract individual message segments
                    samples[style] = self._extract_messages(content)
            except FileNotFoundError:
                print(f"Warning: Could not find {filepath}")
                samples[style] = []
                
        return samples
    
    def _extract_messages(self, content: str) -> List[str]:
        """Extract individual messages from markdown content"""
        # Split by script headers and clean up
        messages = []
        sections = content.split('### ')
        
        for section in sections[1:]:  # Skip the header
            if section.strip():
                # Take the actual message content, skip the title
                lines = section.split('\n')
                message_lines = []
                in_message = False
                
                for line in lines:
                    if line.startswith('**') and line.endswith('**'):
                        in_message = True
                        message_lines.append(line)
                    elif in_message and line.strip() and not line.startswith('*[Word count:'):
                        message_lines.append(line)
                    elif line.startswith('---') or line.startswith('*[Word count:'):
                        break
                
                if message_lines:
                    messages.append('\n'.join(message_lines))
        
        return messages
    
    def determine_message_style(self, prefs: MessagePreferences) -> MessageStyle:
        """Determine the appropriate message style based on preferences"""
        
        # High intensity = drill sergeant or stay hard
        if prefs.intensity > 80:
            if prefs.language_clean < 30:  # Dirty language
                return MessageStyle.STAY_HARD
            else:
                return MessageStyle.DRILL_SERGEANT
        
        # Low intensity = yoga mindful
        elif prefs.intensity < 30:
            return MessageStyle.YOGA_MINDFUL
        
        # Comedy styles
        elif prefs.humor_style > 60:
            if prefs.language_clean > 70:
                return MessageStyle.COMEDY_CLEAN
            else:
                return MessageStyle.COMEDY_RAUNCHY
        
        # Default to rise and grind
        else:
            return MessageStyle.RISE_GRIND
    
    def generate_system_prompt(self, style: MessageStyle, prefs: MessagePreferences) -> str:
        """Generate the system prompt based on style and preferences"""
        
        base_prompts = {
            MessageStyle.YOGA_MINDFUL: """You are a mindful, zen-like motivational coach who speaks with compassion and wisdom. 
            Use gentle language, breathing metaphors, and focus on inner strength and self-compassion. 
            Emphasize mindfulness, presence, and trusting the process.""",
            
            MessageStyle.COMEDY_CLEAN: """You are a stand-up comedian motivational speaker who uses clean, clever humor 
            to inspire people. Make people laugh while motivating them. Use witty observations, 
            self-deprecating humor, and funny analogies. Keep language family-friendly.""",
            
            MessageStyle.COMEDY_RAUNCHY: """You are a edgy comedian motivational speaker who uses adult humor 
            and occasional profanity to inspire. Be funny but motivating, using raw humor and real talk. 
            You can swear and be a bit crude, but always with purpose.""",
            
            MessageStyle.RISE_GRIND: """You are an energetic, enthusiastic motivational speaker who believes 
            in hard work and persistence. Use powerful language, exclamation points, and focus on 
            taking action and building success through effort.""",
            
            MessageStyle.DRILL_SERGEANT: """You are a tough, no-nonsense drill sergeant motivational coach. 
            Be direct, commanding, and intense without excessive profanity. Use military-style motivation 
            focused on discipline, commitment, and mental toughness.""",
            
            MessageStyle.STAY_HARD: """You are David Goggins-style ultra-intense motivational coach. 
            Use tough love, harsh reality checks, and challenging language including strategic profanity. 
            Focus on mental toughness, embracing struggle, and becoming unstoppable."""
        }
        
        style_prompt = base_prompts[style]
        
        # Add preference modifications
        intensity_mod = ""
        if prefs.intensity > 70:
            intensity_mod = " Be VERY intense and demanding."
        elif prefs.intensity < 30:
            intensity_mod = " Keep the tone gentle and encouraging."
        
        length_mod = ""
        if prefs.message_length < 30:
            length_mod = " Keep it to a short, punchy quote or single paragraph."
        elif prefs.message_length > 70:
            length_mod = " Create a longer, detailed motivational speech (multiple paragraphs)."
        
        action_mod = ""
        if prefs.action_orientation > 70:
            action_mod = " Focus on specific, actionable steps and concrete behaviors."
        else:
            action_mod = " Focus on mindset, feelings, and general inspiration."
        
        clean_mod = ""
        if prefs.language_clean > 80:
            clean_mod = " Use completely clean language suitable for all audiences."
        elif prefs.language_clean < 20:
            clean_mod = " You can use strong profanity when it serves the motivational purpose."
        
        return f"{style_prompt}{intensity_mod}{length_mod}{action_mod}{clean_mod}"
    
    def generate_message(self, prefs: MessagePreferences) -> Dict:
        """Generate a custom motivational message based on preferences"""
        
        # Determine the style
        style = self.determine_message_style(prefs)
        
        # Get sample messages for inspiration
        style_samples = self._get_style_samples(style)
        sample_text = "\n\n".join(style_samples[:2]) if style_samples else ""
        
        # Create the prompt
        system_prompt = self.generate_system_prompt(style, prefs)
        
        user_prompt = f"""Create a motivational message about: {prefs.user_input}

Here are some examples of the style you should emulate:
{sample_text}

Remember to match the tone, intensity, and approach shown in the examples while addressing the user's specific topic: {prefs.user_input}"""

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=1000,
                temperature=0.8
            )
            
            message_text = response.choices[0].message.content.strip()
            
        except Exception as e:
            # Fallback to template-based generation
            print(f"OpenAI API error: {e}")
            message_text = self._generate_fallback_message(prefs, style)
        
        # Generate additional elements
        result = {
            'message_text': message_text,
            'style': style.value,
            'music_style': self._determine_music_style(prefs),
            'visual_style': self._determine_visual_style(prefs),
            'background_image': self._select_background_image(prefs),
            'audio_file': self._select_audio_file(prefs),
            'preferences_used': prefs
        }
        
        return result
    
    def _get_style_samples(self, style: MessageStyle) -> List[str]:
        """Get sample messages for the given style"""
        style_map = {
            MessageStyle.YOGA_MINDFUL: 'yoga',
            MessageStyle.COMEDY_CLEAN: 'comedy',
            MessageStyle.COMEDY_RAUNCHY: 'comedy',
            MessageStyle.RISE_GRIND: 'rise_grind',
            MessageStyle.DRILL_SERGEANT: 'stay_hard',
            MessageStyle.STAY_HARD: 'stay_hard'
        }
        
        sample_key = style_map.get(style, 'rise_grind')
        return self.sample_messages.get(sample_key, [])
    
    def _generate_fallback_message(self, prefs: MessagePreferences, style: MessageStyle) -> str:
        """Generate a fallback message when AI is unavailable"""
        templates = {
            MessageStyle.YOGA_MINDFUL: f"Take a deep breath and center yourself. Your journey with {prefs.user_input} is unfolding perfectly. Trust the process and honor your growth.",
            
            MessageStyle.COMEDY_CLEAN: f"So you want to tackle {prefs.user_input}? That's like trying to fold a fitted sheet - looks impossible, but somehow people manage it every day!",
            
            MessageStyle.RISE_GRIND: f"TIME TO DOMINATE {prefs.user_input.upper()}! No excuses, no delays, just pure ACTION! Your future self is counting on what you do RIGHT NOW!",
            
            MessageStyle.STAY_HARD: f"You think {prefs.user_input} is hard? GOOD! Hard is where you build character! Stop making excuses and start making progress!"
        }
        
        return templates.get(style, f"You've got this! {prefs.user_input} is just another challenge to conquer!")
    
    def _determine_music_style(self, prefs: MessagePreferences) -> str:
        """Determine music style based on preferences"""
        if prefs.music_style > 80:
            return "rock_energetic"
        elif prefs.music_style > 60:
            return "upbeat_pop"
        elif prefs.music_style > 40:
            return "motivational_orchestral"
        elif prefs.music_style > 20:
            return "ambient_inspiring"
        else:
            return "calm_meditation"
    
    def _determine_visual_style(self, prefs: MessagePreferences) -> str:
        """Determine visual presentation style"""
        if prefs.visual_style > 80:
            return "dynamic_video"
        elif prefs.visual_style > 60:
            return "animated_graphics"
        elif prefs.visual_style > 40:
            return "slideshow"
        elif prefs.visual_style > 20:
            return "static_enhanced"
        else:
            return "static_simple"
    
    def _select_background_image(self, prefs: MessagePreferences) -> str:
        """Select appropriate background image"""
        if prefs.intensity > 70:
            options = ["rocky_montin_national_park_valley_at_dawn.jpeg", 
                      "a_tough_femail_athlete_road_running.jpeg"]
        elif prefs.action_orientation > 70:
            options = ["a_runner_from_a_distance_on_a.jpeg", 
                      "manhattan_nightime_street_scene.jpeg"]
        else:
            options = ["winding_country_road.jpeg", 
                      "a_sw_usa_desert_with_a_brewing.jpeg"]
        
        return f"IMAGES/{random.choice(options)}"
    
    def _select_audio_file(self, prefs: MessagePreferences) -> str:
        """Select appropriate audio file"""
        audio_files = [
            "AUDIO/GetTheFckPutofBed.mp3",
            "AUDIO/YouHeardMeRight.mp3", 
            "AUDIO/FrpomTheAshes.mp3"
        ]
        
        # Simple selection for now - could be enhanced with more sophisticated matching
        return random.choice(audio_files)

# Example usage
if __name__ == "__main__":
    # Example preferences
    prefs = MessagePreferences(
        intensity=75,  # High intensity
        language_clean=60,  # Moderately clean
        humor_style=30,  # Not very humorous
        action_orientation=80,  # Very action-oriented
        message_length=60,  # Medium-long message
        music_style=85,  # Rock style
        visual_style=70,  # Animated style
        user_input="getting motivated to wake up early and exercise"
    )
    
    # Initialize agent (you'll need to provide OpenAI API key)
    agent = MotivationalAIAgent()
    
    # Generate message
    result = agent.generate_message(prefs)
    
    print("Generated Message:")
    print(result['message_text'])
    print(f"\nStyle: {result['style']}")
    print(f"Music: {result['music_style']}")
    print(f"Visual: {result['visual_style']}") 