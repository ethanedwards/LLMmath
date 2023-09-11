import asyncio
import openai


# The rate limit for OpenAI API
RATE_LIMIT = 60
# Create a semaphore to avoid rate limits
semaphore = asyncio.Semaphore(RATE_LIMIT)

# Create a session to be used by aiohttp for greatest efficiency
def begin_async():
    openai.aiosession.set(ClientSession())

# Close the session when you are done, should be called at end of experiment
async def end_async():
    await openai.aiosession.get().close()


async def api_call(prompt: str, model: str='gpt-4', temperature: float=0.0, max_tokens: int=100, messages: list=[]):
    # Obtain a semaphore
    async with semaphore:
        result = await create_chat_completion(prompt, model, temperature, max_tokens, messages)

    return result


async def create_chat_completion(prompt: str, model: str='gpt-4', temperature: float=0.0, max_tokens: int=100, messages: list=[]):
    if not messages:  # if messages list is empty
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    chat_completion_resp = await openai.ChatCompletion.acreate(
        model=model, 
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens
        )
    return chat_completion_resp['choices'][0]['message']['content']
