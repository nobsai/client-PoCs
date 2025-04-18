# Persona Genie: AI-Powered Customer Profiling for AlFahim HQ

A Streamlit-based solution for generating intelligent, narrative-style customer profiles based on purchase history, built specifically for AlFahim HQ's luxury retail environment.

## Overview

Persona Genie uses CrewAI agents to analyze customer order data and generate detailed, narrative-style customer personas. The solution works entirely locally, using only CSV/Excel files without requiring databases or external APIs.

## Features

- Generate realistic sample customer order datasets customized for luxury retail
- AI-powered customer persona generation using CrewAI agents
- Elegant Streamlit frontend with luxury-inspired aesthetics
- Local operation using only CSV/Excel files
- Stylish, narrative-driven customer profiles with unique archetypes
- Export profiles to CSV for further analysis

## Getting Started

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/persona-genie.git
   cd persona-genie
   ```

2. Navigate to the persona_genie directory:
   ```
   cd persona_genie
   ```

3. Install required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Configure your environment by updating the `.env` file with your OpenAI API key.

### Running the Application

**Windows:**
Simply double-click the `run.bat` file.

**Command Line:**
```
python run.py
```

Or run the Streamlit app directly:
```
streamlit run app.py
```

## How It Works

1. **Data Handling**: The application accepts customer order data via file upload or can generate synthetic data.

2. **AI Agent Analysis**: CrewAI agents analyze each customer's purchases to identify:
   - Style preferences
   - Color affinity
   - Price sensitivity
   - Brand loyalty
   - Inferred lifestyle traits
   - Emotional values

3. **Persona Generation**: The system creates detailed, narrative-style profiles including:
   - Style analysis
   - Lifestyle traits
   - A unique archetype (e.g., "The Urban Nomad", "The Prestige Minimalist")
   - A story-style profile blurb with a stylish tone

4. **Visualization**: Customer profiles are presented as elegant cards with expandable sections.

## Project Structure

- `app.py`: Main Streamlit application
- `run.py`: Helper script to run the application
- `agents/`: Customer profiling AI agents using CrewAI
- `components/`: Streamlit UI components
- `data/`: Directory for sample and uploaded datasets
- `utils/`: Utility functions for data processing

## Contact

For questions or feedback, please contact [your.email@example.com](mailto:your.email@example.com). 