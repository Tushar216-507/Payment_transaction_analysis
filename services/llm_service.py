from groq import Groq
from config import Config
import json
import time

client = Groq(api_key=Config.GROQ_API_KEY)

def _build_system_prompt():
    base = """
    YOU ARE AN ANALYSIS AI AGENT, WHICH ANALYZES THE PAYMENT TRANSACTIONS AND GIVE INSIGHTS
"""

