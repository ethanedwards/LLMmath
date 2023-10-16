#Main function to run the experiment
#A lot of the code is based around avoiding the api limits
#At present, GPT-3 is limited to 90k tokens per minute, but 3,500 requests per minute, so the token is the relevant limiter
#GPT-4 is limited to 200 requests per limit

from experiment import cot_lang_experiment_records, analyze_completion, write_to_csv
from completion_analysis import clean_completion
from data_record import Record
from api_call import begin_async, end_async, api_call, TokenLimiter
import asyncio
import time


#Simple function for chunking the record list into smaller components to avoid api limits
def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

#Function to get each responses from gpt-4 and then use the processing functions to get the data
async def handle_record(record: Record, semaphore:asyncio.Semaphore, token_semaphore: TokenLimiter, failed_records: list=[]):
    #
    try:
        completion = await api_call(prompt=record.output_prompt(), semaphore=semaphore)
        answer, first, second = record.output_completion_vars()
        languages, numsystems, operands, check_answer, answer_string, answer_number, misc_qualities = await analyze_completion(completion=completion, answer=answer, operandA=first, operandB=second, tokensemaphore=token_semaphore)
        record.update_results(completion=clean_completion(completion), completionLanguages=languages, completionNumeralSystems=numsystems, completionOperands=operands, completionAnswer=answer_string, completionAnswerArabic=answer_number, completionCorrect=check_answer, completionDescriptors=misc_qualities)
    except Exception as e:
        print(f"Failure handling record {record.to_csv()}: {e}")
        failed_records.append(record)


async def run_experiment():
    GPT4_RATE_LIMIT = 300
    GPT3_TOKEN_COUNT = 70000
    CHUNK_SIZE = 199
    records = cot_lang_experiment_records()
    total_records = len(records)
    failed_records = []

    semaphore = asyncio.Semaphore(GPT4_RATE_LIMIT)
    token_semphore = TokenLimiter(GPT3_TOKEN_COUNT)

    begin_async()

    start_time_total = time.time()  

    for chunk_index, batch in enumerate(chunks(records, CHUNK_SIZE)):
        start_time = time.time()  # Timer to maintain the 1-minute interval

        await asyncio.gather(*[handle_record(record, semaphore=semaphore, token_semaphore=token_semphore, failed_records=failed_records) for record in batch])
        write_to_csv(
        [record.to_dict() for record in batch],
        'output.csv'
        )

        write_to_csv(
        [record.to_dict() for record in failed_records],
        'failed.csv'
        )

        processed_records = chunk_index * CHUNK_SIZE + len(batch)
        remaining_records = total_records - processed_records

        process_time = time.time() - start_time
        total_time = time.time() - start_time_total 

        print(f"Processed records: {processed_records}, Remaining records: {remaining_records}, Elapsed time: {total_time} seconds")

        process_time = time.time() - start_time
        if process_time < 60.0:
            await asyncio.sleep(60.0 - process_time)  # Sleep to fill up the remaining time to 1 minute


    await end_async()

if __name__ == '__main__':
    asyncio.run(run_experiment())