from api_call import begin_async, end_async, api_call
import asyncio
import random
import time


async def testAsync():
    begin_async()
    #set up timer
    start = time.time()
    #iterate through two one-digit random number lists as operands
    for i in range(10):
        for j in range(10):
            #generate random operator
            operator = random.choice(['+', '-', '*', '/'])
            #generate prompt
            prompt = str(i) + operator + str(j) + '='
            #call api
            #use turbo to save on credits
            result = await api_call(prompt, model='gpt-3.5-turbo')
            print(result)

    #end timer
    end = time.time()
    print(f'Completion time is {end - start}')

    #close session
    await end_async()

#main function
if __name__ == '__main__':
    asyncio.run(testAsync())
