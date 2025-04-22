from flask import Flask, request, jsonify, render_template
from langchain_experimental.agents import create_csv_agent
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.agents.agent_types import AgentType
from langchain_community.document_loaders import Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
import os
from utils import get_openai_api_key
import re
import logging
import base64
import openai
import tempfile

app = Flask(__name__)

# Enable logging
logging.basicConfig(level=logging.DEBUG)

# Initialize OpenAI API key
openai_api_key = get_openai_api_key()
os.environ["OPENAI_API_KEY"] = openai_api_key

# Initialize LangChain components
llm = ChatOpenAI(model="gpt-4o", temperature=0)

# Paths to files
FLIGHT_STATUS_CSV = r'Documents/flight_status_data.csv'
BOOKING_DETAILS_CSV = r'Documents/booking_details_data.csv'
FAQ_DOCX = r'Documents/FAQs.docx'

# User details
username = "Ashik Andrews"

# Initialize CSV agent
try:
    csv_agent = create_csv_agent(
        llm=llm,
        path=[FLIGHT_STATUS_CSV, BOOKING_DETAILS_CSV],
        verbose=False,
        agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        allow_dangerous_code=True
    )
except Exception as e:
    logging.error(f"Error initializing CSV agent: {str(e)}")
    csv_agent = None

# Initialize conversational memory
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# Initialize FAQ retrieval system
def initialize_faq_retriever():
    try:
        loader = Docx2txtLoader(FAQ_DOCX)
        documents = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        texts = text_splitter.split_documents(documents)
        embeddings = OpenAIEmbeddings()
        vectorstore = Chroma.from_documents(texts, embeddings)
        retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=False
        )
        return qa_chain
    except Exception as e:
        logging.error(f"Error initializing FAQ retriever: {str(e)}")
        return None

faq_retriever = initialize_faq_retriever()

# Prompt for LLM-based file selection
FILE_SELECTION_PROMPT = PromptTemplate(
    input_variables=["query"],
    template="""
    You are an assistant tasked with classifying a user query to determine which data source to use for generating a response. The available data sources are:
    1. **flight_status_data.csv**: Contains flight status information (e.g., flight number, departure, arrival, status). Use this for queries about flight schedules, delays, or flight numbers (e.g., "What's the status of flight EY123?").
    2. **booking_details_data.csv**: Contains booking information (e.g., destination, class, price, ticket details). Use this for queries about bookings, ticket prices, or travel classes (e.g., "Show my booking details").
    3. **FAQs.docx**: Contains general FAQs about airline policies (e.g., baggage, check-in, cancellations). Use this for general questions not related to specific flights or bookings (e.g., "What's the baggage policy?").

    Based on the user query below, select the most appropriate data source. Return only the name of the data source (e.g., "flight_status_data.csv", "booking_details_data.csv", or "FAQs.docx").

    User query: {query}
    """
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
        with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as temp_file:
            temp_file.write(audio_bytes)
            temp_file_path = temp_file.name

        # Transcribe using OpenAI Whisper
        with open(temp_file_path, "rb") as audio_file:
            transcript = openai.audio.transcribe(
                model="whisper-1",
                file=audio_file
            )

        # Clean up temporary file
        os.remove(temp_file_path)

        return jsonify({"text": transcript['text']})

    except Exception as e:
        logging.error(f"Error processing audio: {str(e)}")
        return jsonify({"error": "Error processing audio"}), 500

# Chatbot response route
@app.route('/get_response', methods=['POST'])
def get_response():
    user_message = request.json.get('message', '').strip()
    if not user_message:
        return jsonify({"response": "I'm sorry, I didn't understand that. Could you rephrase?"})

    try:
        if not csv_agent:
            return jsonify({"response": "CSV agent is not initialized. Please try again later."}), 500

        # Use LLM to classify the query and select the data source
        file_selection_chain = FILE_SELECTION_PROMPT | llm
        selected_file = file_selection_chain.invoke({"query": user_message}).content.strip()
        response_text = ""

        if "flight_status_data.csv" in selected_file:
            # Handle flight status inquiry using CSV agent
            prompt = (
                f"Please assist the user '{username}' with their flight status inquiry. "
                f"Look up the flight status data for: {user_message}. "
                f"Provide a friendly summary of relevant flight details such as departure, arrival, and status. "
                f"Start the response by addressing the user by name. "
                f"If no relevant data is found, reply with: 'Hi {username}, the requested flight details are unavailable.'"
            )
            response_text = csv_agent.run(prompt)
        elif "booking_details_data.csv" in selected_file:
            # Handle booking inquiry using CSV agent
            prompt = (
                f"Please help the user '{username}' with their booking details inquiry. "
                f"Search the booking details data for: {user_message}. "
                f"Provide a clear summary including destination, class, and price. "
                f"Begin the response by addressing the user by name. "
                f"If no information is found, respond with: 'Hi {username}, the requested booking details are unavailable.'"
            )
            response_text = csv_agent.run(prompt)
        elif "FAQs.docx" in selected_file:
            # Handle FAQ inquiry using retriever
            if faq_retriever:
                prompt = (
                    f"Help the user '{username}' with their question based on our FAQ document. "
                    f"The question is: {user_message}. "
                    f"Provide a clear, user-friendly answer and start the response by addressing the user. "
                    f"If the answer is not available, respond with: 'Hi {username}, the requested information is unavailable in our FAQs.'"
                )
                response_text = faq_retriever.run(prompt)
            else:
                response_text = f"Hi {username}, the requested information is unavailable in our FAQs."
        else:
            # Fallback if LLM selects an invalid file
            response_text = f"Hi {username}, I'm sorry, I couldn't determine how to process your query. Please try again."


        # Save conversation to memory
        memory.save_context({"input": user_message}, {"output": response_text})

        # Enhance response formatting
        response_text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', response_text)
        response_text = re.sub(r'##(.*?)\n', r'<h2>\1</h2>', response_text)
        response_text += "<br>Best Regards, Etihad Airways Assistant"

        return jsonify({"response": response_text})

    except Exception as e:
        logging.error(f"Error processing inquiry: {str(e)}")
        return jsonify({"response": "An error occurred while processing your request."})

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
            voice="alloy",
            input=text
        )

        # Convert binary audio to base64
        audio_base64 = base64.b64encode(response.content).decode('utf-8')

        return jsonify({
            "audio": audio_base64,
            "mimeType": "audio/mpeg"
        })

    except Exception as e:
        logging.error(f"Speech synthesis error: {str(e)}")
        return jsonify({"error": "Error generating speech"}), 500

# Get conversation history
@app.route('/get_history', methods=['GET'])
def get_history():
    try:
        history = memory.load_memory_variables({})['chat_history']
        formatted_history = [
            {"role": "user" if msg.type == "human" else "bot", "content": msg.content}
            for msg in history
        ]
        return jsonify({"history": formatted_history})
    except Exception as e:
        logging.error(f"Error fetching history: {str(e)}")
        return jsonify({"history": []}), 500

# Reset conversation history
@app.route('/reset_history', methods=['POST'])
def reset_history():
    try:
        memory.clear()
        return jsonify({"message": "Conversation reset successfully."})
    except Exception as e:
        logging.error(f"Error resetting history: {str(e)}")
        return jsonify({"error": "Failed to reset conversation."}), 500

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)