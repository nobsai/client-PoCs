# voice_assistant/main.py

import logging
import time
from colorama import Fore, init
from voice_assistant.audio import record_audio, play_audio
from voice_assistant.transcription import transcribe_audio
from voice_assistant.response_generation import generate_response
from voice_assistant.text_to_speech import text_to_speech
from voice_assistant.utils import delete_file
from voice_assistant.config import Config
from voice_assistant.api_key_manager import get_transcription_api_key, get_response_api_key, get_tts_api_key

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize colorama
init(autoreset=True)

import threading

SYSTEM_PROMPT = """## Objective
You are Rafa, a helpful and polite voice assistant for Dubai Constructions Company. You assist users by answering their questions about inventory, equipment, safety gear, and spare parts.

## Knowledge Base
Inventory Overview:
- Raw Materials:
  - Cement (OPC 53 Grade): 12,000 bags in stock; reorder level at 3,000 bags.
  - Steel Rebars (TMT Fe500): 820 tons in stock; reorder level at 200 tons.
  - River Sand: 2,500 m³ in stock.
  - Aggregates (20mm): 3,200 m³ in stock.
  - Ready Mix Concrete (M25): 400 m³ in stock.

- Construction Equipment:
  - Tower Crane (TC-90): 4 units (3 active, 1 under maintenance).
  - Concrete Mixer (500L): 8 units (6 active, 2 idle).
  - Excavator (CAT 320D): 5 units (all active).
  - Vibrator (Needle): 20 units (18 active, 2 damaged).

- Tools & Consumables:
  - Binding Wire: 1,500 kg from Emirates Metals (next restock due: 25-Apr-2025).
  - Nails (4 inch): 75,000 pieces from Al Noor Hardware.
  - Cutting Blades: 250 pieces from Sharjah Tools Co.
  - Sealant (Polyurethane): 400 liters.

- Safety Gear:
  - Safety Helmets: 500 units (380 currently in use); expiry: Dec-2026.
  - Reflective Vests: 600 units (400 in use).
  - Safety Boots: 450 pairs (370 in use).
  - Gloves (Nitrile): 5,000 units.

- Spare Parts:
  - Hydraulic Pump: 3 units available for Excavators.
  - Mixer Belt: Available for Concrete Mixers.

## Purchase or Special Requests
For purchase inquiries or special inventory requests, please redirect the user to contact:

**Inventory Manager:** Fahad Al Marzouqi  
**Email:** fahad.m@dubaiconstructions.ae  
**Phone:** +971-4-234-5678  
**Location:** Warehouse 3, Industrial Area 15, Dubai

## Response Style
- Always answer factually and politely.
- If a user asks something outside the known information, respond with: "I currently don't have that information."
- Be warm and professional in tone, reflecting the Dubai Constructions Company brand.
"""


def main():
    """
    Main function to run the voice assistant.
    """
    chat_history = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

    while True:
        try:
            # Record audio from the microphone and save it as 'test.wav'
            record_audio(Config.INPUT_AUDIO)

            # Get the API key for transcription
            transcription_api_key = get_transcription_api_key()
            
            # Transcribe the audio file
            user_input = transcribe_audio(Config.TRANSCRIPTION_MODEL, transcription_api_key, Config.INPUT_AUDIO, Config.LOCAL_MODEL_PATH)

            # Check if the transcription is empty and restart the recording if it is. This check will avoid empty requests if vad_filter is used in the fastwhisperapi.
            if not user_input:
                logging.info("No transcription was returned. Starting recording again.")
                continue
            logging.info(Fore.GREEN + "You said: " + user_input + Fore.RESET)

            # Check if the user wants to exit the program
            if "goodbye" in user_input.lower() or "arrivederci" in user_input.lower():
                break

            # Append the user's input to the chat history
            chat_history.append({"role": "user", "content": user_input})

            # Get the API key for response generation
            response_api_key = get_response_api_key()

            # Generate a response
            response_text = generate_response(Config.RESPONSE_MODEL, response_api_key, chat_history, Config.LOCAL_MODEL_PATH)
            logging.info(Fore.CYAN + "Response: " + response_text + Fore.RESET)

            # Append the assistant's response to the chat history
            chat_history.append({"role": "assistant", "content": response_text})

            # Determine the output file format based on the TTS model
            if Config.TTS_MODEL == 'openai' or Config.TTS_MODEL == 'elevenlabs' or Config.TTS_MODEL == 'melotts' or Config.TTS_MODEL == 'cartesia':
                output_file = 'output.mp3'
            else:
                output_file = 'output.wav'

            # Get the API key for TTS
            tts_api_key = get_tts_api_key()

            # Convert the response text to speech and save it to the appropriate file
            text_to_speech(Config.TTS_MODEL, tts_api_key, response_text, output_file, Config.LOCAL_MODEL_PATH)

            # Play the generated speech audio
            play_audio(output_file)
            
            # Clean up audio files
            # delete_file(Config.INPUT_AUDIO)
            # delete_file(output_file)

        except Exception as e:
            logging.error(Fore.RED + f"An error occurred: {e}" + Fore.RESET)
            delete_file(Config.INPUT_AUDIO)
            if 'output_file' in locals():
                delete_file(output_file)
            time.sleep(1)

if __name__ == "__main__":
    main()
