import streamlit as st
import os
import time
import base64
from io import BytesIO
import tempfile
import re
from datetime import datetime
import wave
import struct
import math

# Try to import TTS libraries
try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

# Simulated IBM Watson services (replace with actual IBM Watson API calls)
class SimulatedWatsonxLLM:
    """Simulates IBM Watsonx Granite LLM for tone-adaptive text rewriting"""
    
    def __init__(self):
        self.tone_prompts = {
            "Neutral": "Rewrite the following text in a clear, balanced, and informative tone. Maintain all factual information while making it easy to understand:",
            "Suspenseful": "Rewrite the following text to create tension, mystery, and intrigue. Use dramatic language and pacing while preserving the original meaning:",
            "Inspiring": "Rewrite the following text in an uplifting, motivational tone that energizes and encourages the reader. Maintain the core message while making it inspiring:"
        }
    
    def rewrite_text(self, original_text, tone):
        """Simulate tone-adaptive text rewriting using prompt chaining"""
        time.sleep(2)  # Simulate API processing time
        
        # Enhanced rewriting based on tone
        if tone == "Neutral":
            return self._neutral_rewrite(original_text)
        elif tone == "Suspenseful":
            return self._suspenseful_rewrite(original_text)
        elif tone == "Inspiring":
            return self._inspiring_rewrite(original_text)
        else:
            return original_text
    
    def _neutral_rewrite(self, text):
        """Convert text to neutral, informative tone"""
        # Simple simulation - in practice, this would use the LLM
        sentences = text.split('.')
        rewritten = []
        for sentence in sentences:
            if sentence.strip():
                # Add clarity markers
                sentence = sentence.strip()
                if not sentence.endswith(('.', '!', '?')):
                    sentence += '.'
                rewritten.append(f"It is important to note that {sentence.lower()}" if len(sentence) > 10 else sentence)
        return ' '.join(rewritten)
    
    def _suspenseful_rewrite(self, text):
        """Convert text to suspenseful tone"""
        sentences = text.split('.')
        rewritten = []
        suspense_words = ["suddenly", "mysteriously", "unexpectedly", "ominously", "silently"]
        
        for i, sentence in enumerate(sentences):
            if sentence.strip():
                sentence = sentence.strip()
                if i % 2 == 0 and len(sentence) > 10:
                    suspense_word = suspense_words[i % len(suspense_words)]
                    sentence = f"{suspense_word.capitalize()}, {sentence.lower()}"
                sentence += "..." if not sentence.endswith(('.', '!', '?')) else ""
                rewritten.append(sentence)
        return ' '.join(rewritten)
    
    def _inspiring_rewrite(self, text):
        """Convert text to inspiring tone"""
        sentences = text.split('.')
        rewritten = []
        inspiring_phrases = ["remarkably", "brilliantly", "powerfully", "magnificently", "extraordinarily"]
        
        for i, sentence in enumerate(sentences):
            if sentence.strip():
                sentence = sentence.strip()
                if len(sentence) > 10:
                    inspiring_word = inspiring_phrases[i % len(inspiring_phrases)]
                    sentence = f"This {inspiring_word} demonstrates that {sentence.lower()}"
                sentence += "!" if not sentence.endswith(('.', '!', '?')) else ""
                rewritten.append(sentence)
        return ' '.join(rewritten)


class RealTTSEngine:
    """Real Text-to-Speech engine using multiple TTS backends"""
    
    def __init__(self):
        self.voices = {
            "Lisa": {"gender": "female", "accent": "American", "rate": 180, "voice_id": 0},
            "Michael": {"gender": "male", "accent": "American", "rate": 170, "voice_id": 1},
            "Allison": {"gender": "female", "accent": "British", "rate": 175, "voice_id": 2}
        }
        self.available_engines = self._check_available_engines()
    
    def _check_available_engines(self):
        """Check which TTS engines are available"""
        engines = []
        if PYTTSX3_AVAILABLE:
            engines.append("pyttsx3")
        if GTTS_AVAILABLE:
            engines.append("gtts")
        return engines
    
    def synthesize(self, text, voice="Lisa", audio_format="wav"):
        """Generate speech using available TTS engines"""
        if not self.available_engines:
            st.error("No TTS engines available! Please install pyttsx3 or gtts.")
            return None
        
        # Use the best available engine
        if "pyttsx3" in self.available_engines:
            return self._synthesize_pyttsx3(text, voice)
        elif "gtts" in self.available_engines:
            return self._synthesize_gtts(text, voice)
        else:
            st.error("No compatible TTS engine found!")
            return None
    
    def _synthesize_pyttsx3(self, text, voice):
        """Generate speech using pyttsx3 (offline TTS)"""
        try:
            engine = pyttsx3.init()
            
            # Configure voice settings
            voice_config = self.voices[voice]
            engine.setProperty('rate', voice_config['rate'])
            
            # Try to set voice based on gender and preferences
            voices = engine.getProperty('voices')
            if voices:
                # Select voice based on gender preference
                if voice_config['gender'] == 'male':
                    male_voices = [v for v in voices if 'male' in v.name.lower() or 'david' in v.name.lower() or 'mark' in v.name.lower()]
                    if male_voices:
                        engine.setProperty('voice', male_voices[0].id)
                else:
                    female_voices = [v for v in voices if 'female' in v.name.lower() or 'zira' in v.name.lower() or 'hazel' in v.name.lower()]
                    if female_voices:
                        engine.setProperty('voice', female_voices[0].id)
            
            # Generate audio to temporary file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_filename = temp_file.name
            
            engine.save_to_file(text, temp_filename)
            engine.runAndWait()
            
            # Read the generated audio file
            with open(temp_filename, 'rb') as audio_file:
                audio_data = audio_file.read()
            
            # Clean up temporary file
            os.unlink(temp_filename)
            
            # Calculate duration
            word_count = len(text.split())
            duration = word_count * 0.6
            
            return {
                "format": "wav",
                "duration": duration,
                "voice": voice,
                "size": len(audio_data),
                "data": audio_data,
                "text_preview": text[:50] + "..." if len(text) > 50 else text,
                "engine": "pyttsx3"
            }
            
        except Exception as e:
            st.error(f"pyttsx3 TTS Error: {str(e)}")
            return None
    
    def _synthesize_gtts(self, text, voice):
        """Generate speech using Google Text-to-Speech (online)"""
        try:
            # Configure language based on voice accent
            voice_config = self.voices[voice]
            lang = 'en-uk' if voice_config['accent'] == 'British' else 'en-us'
            
            # Create gTTS object
            tts = gTTS(text=text, lang=lang, slow=False)
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
                temp_filename = temp_file.name
            
            tts.save(temp_filename)
            
            # Read the generated audio file
            with open(temp_filename, 'rb') as audio_file:
                audio_data = audio_file.read()
            
            # Clean up temporary file
            os.unlink(temp_filename)
            
            # Calculate duration
            word_count = len(text.split())
            duration = word_count * 0.6
            
            return {
                "format": "mp3",
                "duration": duration,
                "voice": voice,
                "size": len(audio_data),
                "data": audio_data,
                "text_preview": text[:50] + "..." if len(text) > 50 else text,
                "engine": "gtts"
            }
            
        except Exception as e:
            st.error(f"gTTS Error: {str(e)} - Make sure you have internet connection!")
            return None


class EchoVerseApp:
    """Main EchoVerse application class"""
    
    def __init__(self):
        self.llm = SimulatedWatsonxLLM()
        self.tts = RealTTSEngine()  # Use real TTS engine
        self.setup_session_state()
    
    def setup_session_state(self):
        """Initialize session state variables"""
        if 'original_text' not in st.session_state:
            st.session_state.original_text = ""
        if 'rewritten_text' not in st.session_state:
            st.session_state.rewritten_text = ""
        if 'selected_tone' not in st.session_state:
            st.session_state.selected_tone = "Neutral"
        if 'selected_voice' not in st.session_state:
            st.session_state.selected_voice = "Lisa"
        if 'audio_data' not in st.session_state:
            st.session_state.audio_data = None
        if 'processing' not in st.session_state:
            st.session_state.processing = False
    
    def run(self):
        """Main application interface"""
        st.set_page_config(
            page_title="EchoVerse - AI Audiobook Creator",
            page_icon="🎧",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Main header
        st.title("🎧 EchoVerse")
        st.subheader("AI-Powered Audiobook Creation Tool")
        st.markdown("Transform your text into expressive, downloadable audio content with customizable tone and voice.")
        
        # Sidebar for controls
        with st.sidebar:
            st.header("⚙️ Controls")
            
            # Display available TTS engines
            if hasattr(self.tts, 'available_engines') and self.tts.available_engines:
                st.success(f"✅ TTS Engines: {', '.join(self.tts.available_engines)}")
            else:
                st.warning("⚠️ No TTS engines detected. Install pyttsx3 or gtts for real voices.")
            
            # Tone selection
            st.subheader("Select Tone")
            tone = st.selectbox(
                "Choose the narrative tone:",
                ["Neutral", "Suspenseful", "Inspiring"],
                index=["Neutral", "Suspenseful", "Inspiring"].index(st.session_state.selected_tone)
            )
            st.session_state.selected_tone = tone
            
            # Voice selection
            st.subheader("Select Voice")
            voice = st.selectbox(
                "Choose the narrator voice:",
                ["Lisa", "Michael", "Allison"],
                index=["Lisa", "Michael", "Allison"].index(st.session_state.selected_voice)
            )
            st.session_state.selected_voice = voice
            
            # Voice info
            voice_info = self.tts.voices[voice]
            st.info(f"**{voice}**: {voice_info['gender'].title()} voice with {voice_info['accent']} accent")
            
            st.markdown("---")
            
            # Processing buttons
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Rewrite Text", disabled=st.session_state.processing):
                    if st.session_state.original_text:
                        self.rewrite_text()
                    else:
                        st.error("Please enter text first!")
            
            with col2:
                if st.button("🎵 Generate Audio", disabled=st.session_state.processing):
                    if st.session_state.rewritten_text:
                        self.generate_audio()
                    else:
                        st.error("Please rewrite text first!")
        
        # Main content area
        self.display_text_input()
        self.display_text_comparison()
        self.display_audio_output()
        
        # Footer
        st.markdown("---")
        st.markdown("🤖 Powered by IBM Watsonx & Watson Text-to-Speech")
    
    def display_text_input(self):
        """Display text input section"""
        st.header("📝 Text Input")
        
        # Input method selection
        input_method = st.radio("Choose input method:", ["Paste Text", "Upload File"])
        
        if input_method == "Paste Text":
            text = st.text_area(
                "Enter your text:",
                value=st.session_state.original_text,
                height=200,
                placeholder="Paste your text here to convert into an audiobook..."
            )
            if text != st.session_state.original_text:
                st.session_state.original_text = text
                st.session_state.rewritten_text = ""  # Clear rewritten text when original changes
                st.session_state.audio_data = None
        
        else:
            uploaded_file = st.file_uploader("Upload a text file:", type=['txt'])
            if uploaded_file is not None:
                try:
                    text = uploaded_file.read().decode('utf-8')
                    st.session_state.original_text = text
                    st.session_state.rewritten_text = ""
                    st.session_state.audio_data = None
                    st.success(f"File uploaded successfully! ({len(text)} characters)")
                except Exception as e:
                    st.error(f"Error reading file: {str(e)}")
        
        # Display character count
        if st.session_state.original_text:
            char_count = len(st.session_state.original_text)
            word_count = len(st.session_state.original_text.split())
            st.info(f"📊 Text Statistics: {char_count} characters, {word_count} words")
    
    def display_text_comparison(self):
        """Display side-by-side text comparison"""
        if st.session_state.original_text or st.session_state.rewritten_text:
            st.header("📖 Text Comparison")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Original Text")
                if st.session_state.original_text:
                    st.text_area(
                        "Original:",
                        value=st.session_state.original_text,
                        height=300,
                        disabled=True,
                        key="original_display"
                    )
                else:
                    st.info("No original text available")
            
            with col2:
                st.subheader(f"Rewritten Text ({st.session_state.selected_tone} Tone)")
                if st.session_state.rewritten_text:
                    st.text_area(
                        f"{st.session_state.selected_tone}:",
                        value=st.session_state.rewritten_text,
                        height=300,
                        disabled=True,
                        key="rewritten_display"
                    )
                else:
                    st.info(f"Click 'Rewrite Text' to see the {st.session_state.selected_tone.lower()} version")
    
    def display_audio_output(self):
        """Display audio output section"""
        if st.session_state.audio_data:
            st.header("🎧 Audio Output")
            
            audio_info = st.session_state.audio_data
            
            # Audio information
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Duration", f"{audio_info['duration']:.1f}s")
            with col2:
                st.metric("Voice", audio_info['voice'])
            with col3:
                st.metric("Format", audio_info['format'].upper())
            
            # Audio player with real audio
            st.subheader("🎵 Audio Player")
            
            # Display audio player
            st.audio(audio_info['data'], format='audio/wav')
            
            # Show text preview
            st.text(f"Content: {audio_info['text_preview']}")
            
            # Download button with real audio
            st.subheader("💾 Download")
            download_filename = f"echoverse_audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
            
            st.download_button(
                label="📥 Download Audio (WAV)",
                data=audio_info['data'],
                file_name=download_filename,
                mime="audio/wav",
                help="Download the generated audiobook as a WAV file"
            )
            
            st.success(f"✅ Audio file size: {len(audio_info['data'])} bytes")
    
    def rewrite_text(self):
        """Rewrite text with selected tone"""
        if not st.session_state.original_text:
            st.error("No text to rewrite!")
            return
        
        st.session_state.processing = True
        
        # Progress indicator
        with st.spinner(f"Rewriting text in {st.session_state.selected_tone} tone..."):
            progress_bar = st.progress(0)
            
            # Simulate progress
            for i in range(100):
                time.sleep(0.02)  # Small delay for demonstration
                progress_bar.progress(i + 1)
            
            # Call LLM for rewriting
            try:
                rewritten = self.llm.rewrite_text(
                    st.session_state.original_text, 
                    st.session_state.selected_tone
                )
                st.session_state.rewritten_text = rewritten
                st.session_state.audio_data = None  # Clear audio when text changes
                st.success(f"Text successfully rewritten in {st.session_state.selected_tone} tone!")
                
            except Exception as e:
                st.error(f"Error rewriting text: {str(e)}")
        
        st.session_state.processing = False
        st.rerun()
    
    def generate_audio(self):
        """Generate audio from rewritten text"""
        if not st.session_state.rewritten_text:
            st.error("No rewritten text available!")
            return
        
        st.session_state.processing = True
        
        # Progress indicator
        with st.spinner(f"Generating audio with {st.session_state.selected_voice} voice..."):
            progress_bar = st.progress(0)
            
            # Simulate progress
            for i in range(100):
                time.sleep(0.03)  # Small delay for demonstration
                progress_bar.progress(i + 1)
            
            # Call TTS for audio generation
            try:
                audio_data = self.tts.synthesize(
                    st.session_state.rewritten_text,
                    st.session_state.selected_voice
                )
                st.session_state.audio_data = audio_data
                st.success(f"Audio successfully generated with {st.session_state.selected_voice} voice!")
                
            except Exception as e:
                st.error(f"Error generating audio: {str(e)}")
        
        st.session_state.processing = False
        st.rerun()


def main():
    """Main function to run the EchoVerse application"""
    app = EchoVerseApp()
    app.run()


if __name__ == "__main__":
    main()