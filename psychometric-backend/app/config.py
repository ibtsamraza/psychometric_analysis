# config.py
import os
from dotenv import load_dotenv

load_dotenv()  # Load from .env file
# Together_api_key
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
# Groq_api_key
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
