import logging
import json
import pyaudio
import elevenlabs
import soundfile as sf
import requests
import wave

from openai import OpenAI
from deepgram import DeepgramClient, SpeakOptions
from elevenlabs.client import ElevenLabs
from cartesia import Cartesia

from voice_assistant.config import Config
from voice_assistant.local_tts_generation import generate_audio_file_melotts

def text_to_speech(model: str, api_key: str, text: str, output_file_path: str, local_model_path: str = None):
    """
    Convert text to speech using the specified model.
    
    Args:
    model (str): The model to use for TTS ('openai', 'deepgram', 'elevenlabs', 'cartesia', 'melotts', 'piper', 'local').
    api_key (str): The API key for the TTS service.
    text (str): The text to convert to speech.
    output_file_path (str): The path to save the generated speech audio file.
    local_model_path (str): The path to the local model (if applicable).
    """
    
    try:
        if model == 'openai':
            client = OpenAI(api_key=api_key)
            speech_response = client.audio.speech.create(
                model="tts-1",
                voice="nova",
                input=text
            )
            speech_response.stream_to_file(output_file_path)
        
        elif model == 'deepgram':
            client = DeepgramClient(api_key=api_key)
            options = SpeakOptions(
                model="aura-arcas-en",
                encoding="linear16",
                container="wav"
            )
            SPEAK_OPTIONS = {"text": text}
            response = client.speak.v("1").save(output_file_path, SPEAK_OPTIONS, options)
        
        elif model == 'elevenlabs':
            client = ElevenLabs(api_key=api_key)
            audio = client.generate(
                text=text, 
                voice="Paul J.", 
                output_format="mp3_22050_32", 
                model="eleven_turbo_v2"
            )
            elevenlabs.save(audio, output_file_path)
        
        elif model == 'cartesia':
            client = Cartesia(api_key=api_key)
            audio_generator = client.tts.bytes(
                model_id="sonic-2",
                transcript=text,
                voice={"id": "a0e99841-438c-4a64-b679-ae501e7d6091"},
                output_format={
                    "container": "mp3",
                    "bit_rate": 128000,
                    "sample_rate": 44100 # Example bit rate for MP3
                }
            )
            with open(output_file_path, "wb") as f:
                for chunk in audio_generator:
                    f.write(chunk)
        elif model == "melotts":
            generate_audio_file_melotts(text=text, filename=output_file_path)
        
        elif model == "piper":
            try:
                response = requests.post(
                    f"{Config.PIPER_SERVER_URL}/synthesize/",
                    json={"text": text},
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    with open(output_file_path, "wb") as f:
                        f.write(response.content)
                    logging.info(f"Piper TTS output saved to {output_file_path}")
                else:
                    logging.error(f"Piper TTS API error: {response.status_code} - {response.text}")
            
            except Exception as e:
                logging.error(f"Piper TTS request failed: {e}")
        
        elif model == 'local':
            with open(output_file_path, "wb") as f:
                f.write(b"Local TTS audio data")
        
        filtered_text = text.replace('\n', ' ').replace('\r', ' ')
        logging.info(f"Text to speech conversion completed for model '{model}' with text: '{filtered_text}'")
        
    except Exception as e:
        logging.error(f"Failed to convert text to speech: {e}")