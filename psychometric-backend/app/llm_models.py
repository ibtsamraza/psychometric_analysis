from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain_together import ChatTogether
from config import GROQ_API_KEY, TOGETHER_API_KEY
#from langchain_huggingface import HuggingFaceEndpoint
# Importing the required chat model classes (assumed to be imported earlier)
# from langchain.chat_models import ChatGroq, ChatTogether

# Initialize the Groq model "gemma2-9b-it" with low creativity (temperature = 0.1)
gemma = ChatGroq(
    temperature=0.1,
    model="gemma2-9b-it",
    groq_api_key=GROQ_API_KEY
)

# Initialize the Groq model "llama-3.3-70b-versatile" with moderate creativity
groq_llama = ChatGroq(
    temperature=0.2,
    model="llama-3.3-70b-versatile",
    groq_api_key=GROQ_API_KEY
)

# Initialize the Groq model "deepseek-r1-distill-qwen-32b" for efficient reasoning tasks
groq_r1_qwen = ChatGroq(
    temperature=0.2,
    model="deepseek-r1-distill-qwen-32b",
    groq_api_key=GROQ_API_KEY
)

# Initialize the Groq model "deepseek-r1-distill-llama-70b" with balanced creativity
groq_r1_llama = ChatGroq(
    temperature=0.2,
    model="deepseek-r1-distill-llama-70b",
    groq_api_key=GROQ_API_KEY
)

# Initialize another Groq-hosted model "qwen-2.5-32b" with moderate temperature
groq_qwen = ChatGroq(
    temperature=0.2,
    model="qwen-2.5-32b",
    groq_api_key=GROQ_API_KEY
)

# Initialize a Together-hosted LLaMA 4 Maverick model, 17B version, with retry logic
llama_maverick_70b_together = ChatTogether(
    together_api_key=TOGETHER_API_KEY,
    model="meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
    temperature=0.2,
    max_tokens=None,     # Let the model decide max tokens
    timeout=None,        # No timeout restriction
    max_retries=2        # Retry twice in case of failure
)

# Initialize a free Together-hosted LLaMA 3.3 70B model for low-cost usage
llama_70b_together_free = ChatTogether(
    together_api_key=TOGETHER_API_KEY,
    model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
    temperature=0.2,
    max_tokens=None,
    timeout=None,
    max_retries=2
)
