#Handle API and org keys
from dotenv import load_dotenv
import os

load_dotenv()

#API keys and private information
openai_api_key = os.getenv('OPENAI_API_KEY')
openai_org_key = os.getenv('OPENAI_ORG_KEY')