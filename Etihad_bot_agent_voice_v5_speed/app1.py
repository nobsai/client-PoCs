from flask import Flask, request, jsonify, render_template, after_this_request
from crewai import Agent, Task, Crew
from crewai_tools import DOCXSearchTool, CSVSearchTool
import os
from utils import get_openai_api_key
import re
import logging
import base64
import openai

app = Flask(__name__)

# Enable logging
logging.basicConfig(level=logging.DEBUG)

# Initialize OpenAI API key
openai_api_key = get_openai_api_key()
openai.api_key = openai_api_key

# Single Customer Support Agent
customer_support_agent = Agent(
    role="Customer Support Representative",
    goal="Assist customers with flight status, booking details, and general inquiries accurately and efficiently.",
    backstory=("You are a versatile support assistant at Etihad Airways, trained to handle all types of customer inquiries, "
               "including flight status updates, booking information, and general FAQs. Your goal is to provide brief, "
               "precise, and accurate responses tailored to the customer's request."),
    allow_delegation=False,
    verbose=False  # Disabled to reduce overhead
)

# Setup tools
flight_status_search = CSVSearchTool(csv=r'Documents/flight_status_data.csv')
booking_details_search = CSVSearchTool(csv=r'Documents/booking_details_data.csv')
faq_search = DOCXSearchTool(docx=r'Documents/FAQs.docx')

# Single Customer Support Task
customer_support_task = Task(
    description=(
        "{person} inquired:\n"
        "{inquiry}\n\n"
        "Guidelines to respond:\n"
        "1. Classify the inquiry type based on the content:\n"
        "   - If the inquiry mentions 'flight status', 'departure', 'arrival', or a flight number (e.g., 'EY123'), "
        "     treat it as a flight status request.\n"
        "   - If the inquiry mentions 'booking', 'price', 'class', 'ticket', or 'destination', treat it as a booking inquiry.\n"
        "   - If the inquiry is general (e.g., 'baggage policy', 'check-in', or unrelated to flight status/booking), "
        "     treat it as an FAQ request.\n"
        "2. Use the appropriate tool based on the classification:\n"
        "   - For flight status: Use flight_status_search on Documents/flight_status_data.csv.\n"
        "     - Summarize flight details (e.g., departure, arrival, status).\n"
        "     - If no data is found, say: 'The requested flight details are unavailable.'\n"
        "   - For booking details: Use booking_details_search on Documents/booking_details_data.csv.\n"
        "     - Provide relevant info (e.g., destination, class, price).\n"
        "     - If no data is found, say: 'The requested booking details are unavailable.'\n"
        "   - For FAQs: Use faq_search on Documents/FAQs.docx.\n"
        "     - Provide a concise answer from the FAQs.\n"
        "     - If no answer is found, say: 'The requested information is unavailable in our FAQs.'\n"
        "3. Ensure the response is brief, clear, and accurate.\n"
    ),
    expected_output="A precise response addressing the inquiry, tailored to its type (flight status, booking, or FAQ). "
                    "End with 'Best Regards, Etihad Airways Assistant'.",
    tools=[flight_status_search, booking_details_search, faq_search],
    agent=customer_support_agent
)

# Initialize Crew with single agent and task
crew = Crew(
    agents=[customer_support_agent],
    tasks=[customer_support_task],
    verbose=False,  # Disabled to reduce overhead
    memory=False    # Disabled since conversation history isn’t needed per request
)

# Serve HTML template
@app.route('/')
def index():
    return render_template('index.html')

# Voice processing endpoint
@app.route('/process_audio', methods=['POST'])
def process_audio():
    try:
        audio_data = request.json.get('audio')
        if not audio_data:
            return jsonify({"error": "No audio data received"}), 400

        # Decode base64 audio
        audio_bytes = base64.b64decode(audio_data.split(',')[1])

        # Save temporary audio file
        with open("temp.webm", "wb") as f:
            f.write(audio_bytes)

        # Transcribe using OpenAI Whisper
        with open("temp.webm", "rb") as audio_file:
            transcript = openai.Audio.transcribe(
                model="whisper-1",
                file=audio_file
            )

        return jsonify({"text": transcript['text']})

    except Exception as e:
        logging.error(f"Error processing audio: {str(e)}")
        return jsonify({"error": "Error processing audio"}), 500

# Chatbot response route
@app.route('/get_response', methods=['POST'])
def get_response():
    user_message = request.json.get('message', '').strip()
    if user_message:
        inputs = {
            "userid": "1",
            "person": "Ashik Andrews",
            "inquiry": user_message
        }
        try:
            # Generate response from CrewAI
            result = crew.kickoff(inputs=inputs)

            # Extract response and enhance it
            response_text = getattr(result, 'message', str(result))

            response_text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', response_text)
            response_text = re.sub(r'##(.*?)\n', r'<h2>\1</h2>', response_text)

            return jsonify({"response": response_text})

        except Exception as e:
            logging.error(f"Error processing inquiry: {e}")
            return jsonify({"response": "An error occurred while processing your request."})
    else:
        return jsonify({"response": "I'm sorry, I didn't understand that. Could you rephrase?"})

# Text-to-speech synthesis endpoint
@app.route('/synthesize_speech', methods=['POST'])
def synthesize_speech():
    try:
        data = request.json
        text = data.get('text', '').strip()
        if not text:
            return jsonify({"error": "No text provided"}), 400

        # Generate speech using OpenAI TTS
        response = openai.audio.speech.create(
            model="tts-1",
            voice="alloy",  # Choose from alloy, echo, fable, onyx, nova, or shimmer
            input=text
        )

        # Convert binary audio to base64
        audio_base64 = base64.b64encode(response.content).decode('utf-8')

        return jsonify({
            "audio": audio_base64,
            "mimeType": "audio/mpeg"  # OpenAI returns MP3 format
        })

    except Exception as e:
        logging.error(f"Speech synthesis error: {str(e)}")
        return jsonify({"error": "Error generating speech"}), 500

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)