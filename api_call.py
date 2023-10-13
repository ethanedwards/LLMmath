import asyncio
import aiohttp
from aiohttp import ClientSession
import openai
import config
import time
from random import uniform

# The rate limit for OpenAI API
# Set to GPT-4 limit by default
RATE_LIMIT = 10
# Set RETRY_AFTER_STATUS_CODES to API rate limit status code
RETRY_AFTER_STATUS_CODES = (429, 500, 502, 503, 504)
# Create a semaphore to avoid rate limits
semaphore = asyncio.Semaphore(RATE_LIMIT)

# Retry parameters
min_wait_time = 1
max_wait_time = 60  # Maximum wait time before retrying when rate limited
jitter = 0.1  # Add some randomness to avoid close polling loops between different clients

#set up openai api key
openai.api_key = config.openai_api_key
openai.organization = config.openai_org_key


# Create a session to be used by aiohttp for greatest efficiency
def begin_async():
    openai.aiosession.set(ClientSession())

# Close the session when you are done, should be called at end of experiment
async def end_async():
    await openai.aiosession.get().close()


async def api_call(prompt: str, model: str='gpt-4', temperature: float=0.0, max_tokens: int=100, messages: list=[], max_retries: int=3):
    # Obtain a semaphore
    async with semaphore:
        result = await create_chat_completion(prompt, model, temperature, max_tokens, messages, max_retries)

    return result


async def create_chat_completion(prompt: str, model: str='gpt-4', temperature: float=0.0, max_tokens: int=100, messages: list=[], max_retries: int=3):
    if not messages:  # if messages list is empty
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]

    for i in range(max_retries):
        try:
            chat_completion_resp = await openai.ChatCompletion.acreate(
                model=model, 
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
                )
            
            return chat_completion_resp['choices'][0]['message']['content']
            
        except aiohttp.ClientError as e:

            print(f"Attempt {i+1}/{max_retries} failed with error: {e}")
            if e.status in RETRY_AFTER_STATUS_CODES or 'request limit' in str(e):

                if i < max_retries - 1:
                    wait_time = min(max_wait_time, min_wait_time * (2 ** i))  # Exponential backoff
                    wait_time += uniform(-jitter, jitter) * wait_time  # Random jitter
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    print("All attempts failed. Raising last captured exception.")
                    raise  # Re-raise the last exception

        except openai.error.APIError as e:
        #Handle API error here, e.g. retry or log
            print(f"OpenAI API returned an API Error: {e}")
            print(f'Last attempt was {prompt}')
            pass
        except openai.error.APIConnectionError as e:
            #Handle connection error here
            print(f"Failed to connect to OpenAI API: {e}")
            print(f'Last attempt was {prompt}')
            pass
        except openai.error.RateLimitError as e:
        #Handle rate limit error (we recommend using exponential backoff)
            print(f"OpenAI API request exceeded rate limit: {e}")
            print(f'Last attempt was {prompt}')
            pass

#Not asynchronous, use for testing
def create_chat_completion_sync(prompt: str, model: str='gpt-4', temperature: float=0.0, max_tokens: int=100, messages: list=[], max_retries: int=3):
    if not messages:  # if messages list is empty
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]

    for i in range(max_retries):
        try:
            chat_completion_resp = openai.ChatCompletion.create(
                model=model, 
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
                )
            
            return chat_completion_resp['choices'][0]['message']['content']
            
        except openai.error.Timeout:
            if i < max_retries - 1:  # i.e. if it's not the final attempt
                time.sleep(5)
            else:
                print(f'Last attempt was {prompt}')
                raise  # re-throw the last exception if all attempts fail
        except openai.error.APIError as e:
        #Handle API error here, e.g. retry or log
            print(f"OpenAI API returned an API Error: {e}")
            print(f'Last attempt was {prompt}')
            pass
        except openai.error.APIConnectionError as e:
            #Handle connection error here
            print(f"Failed to connect to OpenAI API: {e}")
            print(f'Last attempt was {prompt}')
            pass
        except openai.error.RateLimitError as e:
        #Handle rate limit error (we recommend using exponential backoff)
            print(f"OpenAI API request exceeded rate limit: {e}")
            print(f'Last attempt was {prompt}')
            pass



# Define a synchronous function to call API
def sync_create_chat_completion(data):
    try:
        return openai.ChatCompletion.create(**data)
    except Exception as e:
        print(f"Failed to create chat completion: {e}")

async def create_chat_completion2(prompt, model='gpt-4', temperature=0.0, max_tokens=100, messages=[], max_retries=3):
    loop = asyncio.get_event_loop()
    data = {
        "model": model,
        "messages": messages if messages else [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    
    for i in range(max_retries):
        try:
            chat_completion_resp = await loop.run_in_executor(None, sync_create_chat_completion, data)
            
            return chat_completion_resp['choices'][0]['message']['content']
            
        except aiohttp.ClientError as e:

            print(f"Attempt {i+1}/{max_retries} failed with error: {e}")
            if e.status in RETRY_AFTER_STATUS_CODES or 'request limit' in str(e):

                if i < max_retries - 1:
                    wait_time = min(max_wait_time, min_wait_time * (2 ** i))  # Exponential backoff
                    wait_time += uniform(-jitter, jitter) * wait_time  # Random jitter
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    print("All attempts failed. Raising last captured exception.")
                    raise  # Re-raise the last exception

        except openai.error.APIError as e:
        #Handle API error here, e.g. retry or log
            print(f"OpenAI API returned an API Error: {e}")
            print(f'Last attempt was {prompt}')
            pass
        except openai.error.APIConnectionError as e:
            #Handle connection error here
            print(f"Failed to connect to OpenAI API: {e}")
            print(f'Last attempt was {prompt}')
            pass
        except openai.error.RateLimitError as e:
        #Handle rate limit error (we recommend using exponential backoff)
            print(f"OpenAI API request exceeded rate limit: {e}")
            print(f'Last attempt was {prompt}')
            pass