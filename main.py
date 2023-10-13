from experiment import cot_lang_experiment_records, analyze_completion, write_to_csv
from completion_analysis import clean_completion
from data_record import Record
from api_call import begin_async, end_async, api_call
import asyncio
from concurrent.futures import ThreadPoolExecutor


async def handle_record(record):
    try:
        completion = await api_call(prompt=record.output_prompt(), model="gpt-3.5-turbo")
        answer, first, second = record.output_completion_vars()
        languages, numsystems, operands, check_answer, answer_string, answer_number, misc_qualities = await analyze_completion(completion=completion, answer=answer, operandA=first, operandB=second)
        record.update_results(completion=clean_completion(completion), completionLanguages=languages, completionNumeralSystems=numsystems, completionOperands=operands, completionAnswer=answer_string, completionAnswerArabic=answer_number, completionCorrect=check_answer, completionDescriptors=misc_qualities)
    except Exception as e:
        print(f"Failure handling record {record}: {e}")

async def run_experiment():
    records = cot_lang_experiment_records()[:12]

#    asyncio.set_event_loop(asyncio.new_event_loop())
    begin_async()

    tasks = [asyncio.ensure_future(handle_record(record)) for record in records]
    await asyncio.gather(*tasks)

    await end_async()
    print(records[0].completion)
    with ThreadPoolExecutor() as executor:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            executor,
            write_to_csv,
            [record.to_dict() for record in records],
            'output.csv'
        )


if __name__ == '__main__':
    asyncio.run(run_experiment())