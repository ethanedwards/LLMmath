from experiment import cot_lang_experiment_records, analyze_completion, write_to_csv
from completion_analysis import clean_completion
from data_record import Record
from api_call import begin_async, end_async, api_call, TokenLimiter
import asyncio
from concurrent.futures import ThreadPoolExecutor
import time


def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

async def handle_record(record, semaphore, token_semaphore: TokenLimiter=None):
    try:
        completion = await api_call(prompt=record.output_prompt(), semaphore=semaphore)
        answer, first, second = record.output_completion_vars()
        languages, numsystems, operands, check_answer, answer_string, answer_number, misc_qualities = await analyze_completion(completion=completion, answer=answer, operandA=first, operandB=second, tokensemaphore=token_semaphore)
        record.update_results(completion=clean_completion(completion), completionLanguages=languages, completionNumeralSystems=numsystems, completionOperands=operands, completionAnswer=answer_string, completionAnswerArabic=answer_number, completionCorrect=check_answer, completionDescriptors=misc_qualities)
    except Exception as e:
        print(f"Failure handling record {record}: {e}")

async def run_experiment():
    records = cot_lang_experiment_records()[:420]

#    asyncio.set_event_loop(asyncio.new_event_loop())

    RATE_LIMIT = 900
    semaphore = asyncio.Semaphore(RATE_LIMIT)
    token_semphore = TokenLimiter(90000)

    begin_async()

    for batch in chunks(records, 199):
        start_time = time.time()  # Timer to maintain the 1-minute interval

        await asyncio.gather(*[handle_record(record, semaphore=semaphore, token_semaphore=token_semphore) for record in batch])

        write_to_csv(
        [record.to_dict() for record in batch],
        'output.csv'
        )

        process_time = time.time() - start_time
        if process_time < 60.0:
            await asyncio.sleep(60.0 - process_time)  # Sleep to fill up the remaining time to 1 minute


    await end_async()

if __name__ == '__main__':
    asyncio.run(run_experiment())