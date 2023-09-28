from dotenv import load_dotenv
import os

load_dotenv() # take environment variables from .env.
api_key = os.getenv('OPENAI_KEY')

#API keys and private information
openai_api_key = os.getenv('OPENAI_API_KEY')
openai_org_key = os.getenv('OPENAI_ORG_KEY')