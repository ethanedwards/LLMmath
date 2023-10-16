#Main function to run the experiment
#A lot of the code is based around avoiding the api limits
#At present, GPT-3 is limited to 90k tokens per minute, but 3,500 requests per minute, so the token is the relevant limiter
#GPT-4 is limited to 200 requests per limit

from experiment import cot_lang_experiment_records, analyze_completion, write_to_csv
from completion_analysis import clean_completion
from data_record import Record
from api_call import begin_async, end_async, api_call, TokenLimiter, OPENAI_INTERVAL
import asyncio
import time
from tqdm import tqdm


#Simple function for chunking the record list into smaller components to avoid api limits
def chunks(lst: list, n: int):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

#Function to get each responses from gpt-4 and then use the processing functions to get the data
async def handle_record(record: Record, semaphore:asyncio.Semaphore, token_semaphore: TokenLimiter, pbar:tqdm, failed_records: list=[]):
    try:
        #Get completion from GPT-4
        completion = await api_call(prompt=record.output_prompt(), semaphore=semaphore)
        #Get relevant variables for the procesing stage
        answer, first, second = record.output_completion_vars()
        #Get processed completion variables, including from GPT-3
        languages, numsystems, operands, check_answer, answer_string, answer_number, misc_qualities = await analyze_completion(completion=completion, answer=answer, operandA=first, operandB=second, tokensemaphore=token_semaphore)
        #Update, completing the function
        record.update_results(completion=clean_completion(completion), completionLanguages=languages, completionNumeralSystems=numsystems, completionOperands=operands, completionAnswer=answer_string, completionAnswerArabic=answer_number, completionCorrect=check_answer, completionDescriptors=misc_qualities)
    except Exception as e:
        #If all else fails, including server timeouts. Should keep a running list so that any failures can be processed later and added in to any running files
        print(f"Failure handling record {record.to_csv()}: {e}")
        failed_records.append(record)
    finally:
        pbar.update(1)


#Main function which handles the asyn processing
async def run_experiment():
    #Variables based around the api limits
    #300 chosen to limit concurrency, but likely not hit because the batch system works fine
    GPT4_RATE_LIMIT = 300
    #70k seems to be the best number to not hit token limits, perhaps because of a discrepancy between tiktoken and openai's internal tokenizer
    GPT3_TOKEN_COUNT = 70000
    #199 chosen to avoid hitting the 200 request limit
    CHUNK_SIZE = 199

    #Get all the prompts for the experiment, handled in experiment.py
    records = cot_lang_experiment_records()[:230]
    total_records = len(records)
    failed_records = []

    #Set up the two semaphores for the two separate API limits. The first should rarely be used because of the batch process, but acts as extra security.
    semaphore = asyncio.Semaphore(GPT4_RATE_LIMIT)
    token_semphore = TokenLimiter(GPT3_TOKEN_COUNT)

    #Start the async process with a session
    begin_async()

    #Helper timer for logging purposes
    start_time_total = time.time()  
    pbar = tqdm(total=len(records))

    #Main loop of async processing
    for chunk_index, batch in enumerate(chunks(records, CHUNK_SIZE)):
        start_time = time.time()  # Timer to maintain interval that OpenAI uses for api limits
        #Main processing of asyncio. The limiting factor is currently the token limit for GPT-3, 
        # but in order to do continuous updating and logging waiting for each batch was chosen
        await asyncio.gather(*[handle_record(record, semaphore=semaphore, token_semaphore=token_semphore, pbar=pbar, failed_records=failed_records) for record in batch])
        
        #Writes output of the current batch
        write_to_csv(
        [record.to_dict() for record in batch],
        'output.csv'
        )

        #Writes any failures for later processing
        if failed_records:
            write_to_csv(
            [record.to_dict() for record in failed_records],
            'failed.csv'
        )

        #Logging information
        processed_records = chunk_index * CHUNK_SIZE + len(batch)
        remaining_records = total_records - processed_records

        process_time = time.time() - start_time
        total_time = time.time() - start_time_total 

        print(f"Processed records: {processed_records}, Remaining records: {remaining_records}, Elapsed time: {total_time} seconds")

        #Checks the timer for the 60 second window on the GPT-4 batching
        process_time = time.time() - start_time
        if process_time < OPENAI_INTERVAL:
            await asyncio.sleep(OPENAI_INTERVAL - process_time)  # Sleep to fill up the remaining time to 1 minute

    #Ends the async loop
    await end_async()

#Runs the experiment
if __name__ == '__main__':
    asyncio.run(run_experiment())