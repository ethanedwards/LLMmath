from api_call import begin_async, end_async, api_call, create_chat_completion_sync
import asyncio
import random
import time

async def test_async():
    begin_async()
    start = time.time()
    tasks = []

    for i in range(5):
        for j in range(5):
            operator = random.choice(['+', '-', '*', '/'])
            prompt = str(i) + operator + str(j) + '='
            tasks.append(api_call(prompt, model='gpt-3.5-turbo'))
    results = await asyncio.gather(*tasks)
    
    for result in results:
        print(result)

    end = time.time()
    print(f'Completion time is {end - start}')
    await end_async()

def test_sync():
    #set up timer
    start = time.time()
    #iterate through two one-digit random number lists as operands
    for i in range(5):
        for j in range(5):
            #generate random operator
            operator = random.choice(['+', '-', '*', '/'])
            #generate prompt
            prompt = str(i) + operator + str(j) + '='
            #call api
            #use turbo to save on credits
            result = create_chat_completion_sync(prompt, model='gpt-3.5-turbo')
            print(result)

    #end timer
    end = time.time()
    print(f'Completion time is {end - start}')

#main function
if __name__ == '__main__':
    asyncio.run(test_async2())
    #test_sync()
