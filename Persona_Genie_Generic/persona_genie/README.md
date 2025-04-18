# Persona Genie: AI-Powered Customer Profiling for AlFahim HQ

A Streamlit-based solution for generating intelligent, narrative-style customer profiles based on purchase history.

## Features

- Generate realistic sample customer order datasets
- AI-powered customer persona generation using CrewAI agents
- Beautiful Streamlit frontend with luxury aesthetics
- Local operation using only CSV/Excel files (no databases or APIs)
- Stylish, narrative-driven customer profiles

## Setup

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Configure your environment:
   - Add your OpenAI API key to the `.env` file
   
3. Run the application:
   ```
   streamlit run app.py
   ```

## Usage

1. Generate a sample dataset or upload your own CSV/Excel file
2. View generated customer profiles with detailed style analysis
3. Export profiles to CSV for further analysis

## File Structure

- `app.py`: Main Streamlit application
- `data/`: Directory for sample and uploaded datasets
- `agents/`: Customer profiling AI agents
- `utils/`: Utility functions for data processing
- `components/`: Streamlit UI components 