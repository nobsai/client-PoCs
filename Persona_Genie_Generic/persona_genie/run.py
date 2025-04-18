import os
import subprocess
import sys

def main():
    """
    Run the Streamlit application with proper environment setup
    """
    print("Starting Persona Genie - AlFahim HQ Customer Profiling Solution")
    
    # Check if requirements are installed
    try:
        import streamlit
        import pandas
        import crewai
    except ImportError:
        print("Installing requirements...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    # Run the Streamlit app
    print("Starting Streamlit server...")
    os.system(f"{sys.executable} -m streamlit run app.py")

if __name__ == "__main__":
    main() 