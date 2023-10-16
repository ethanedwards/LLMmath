#This class needs to fill the following functions to analyze completions
#Get all languages in the completion
#Get all numeral systems in the completion
#Get any and all operands in the text of the completion
#Check if the answer is in the completion
#Get the answer from the completion if possible
#Get qualities of the answer (numeral system, inclusion of comma)
#Get any qualities or patterns of the completion (CoT, refusal to answer, etc)
#Have async functions for the GPT aspects so that they can be run in parallel
#Update the record with all these values

import re
from api_call import api_call, TokenLimiter
from numeral_systems import PersianConverter, DevanagariConverter, BurmeseConverter, BengaliConverter, ThaiConverter, ArabicConverter
import tiktoken
import asyncio


numsystems = {
    'Persian': PersianConverter(),
    'Devanagari': DevanagariConverter(),
    'Burmese': BurmeseConverter(),
    'Bengali': BengaliConverter(),
    'Thai': ThaiConverter(),
    'Arabic': ArabicConverter()
}

def count_tokens(prompt: str):
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    return len(encoding.encode(prompt))

#General function for calling GPT to assess a condition in the completion
async def get_gpt_check(completion: str, pattern: str, prompt_template: str, tokensemaphore: TokenLimiter=None):
    matched_resp = []
    checkprompt = prompt_template.format(completion=completion)
    token_count = count_tokens(checkprompt)
    print(f"begun waiting with token count {token_count}")
    await tokensemaphore.use_tokens(token_count)
    asyncio.create_task(tokensemaphore.release_tokens(token_count, 60))
    print(f"finished waiting with token count {token_count}")
    checkresponse = await api_call(checkprompt, model='gpt-3.5-turbo', temperature=0.7, max_retries=3, semaphore=tokensemaphore.sem)

    

    keys_in_response = re.findall(pattern, checkresponse)

    # Capitalize each key for standardization
    matched_resp = [key.capitalize() for key in keys_in_response]

    return matched_resp if matched_resp else ["error"]

#Get languages in the completion
async def get_languages(completion: str, tokensemaphore: TokenLimiter=None):
    checkprompt = f"""The following is a completion from a prompt asking a GPT-model to perform a math problem in several different languages and numeral system. You need to classify the language that the sentence is written in completely ignore numerals. Your response options are '&english&', '&croatian&', '&traditionalchinese&', '&simplifiedchinese&', '&burmese&', '&thai&', '&nepali&', '&bengali&', '&farsi&', and '&japanese&' If there are only numbers and no language just put '&nolanguage&'. If there is a mix of multiple languages, list each of them. If it does not fall into these categories answer '&other&'. Ignore all numerals in your answer. So for example "The product of ๖๗๖ and ๔๑๔ is ๒๗๙๔๔๔." would return '&english&' because the words are in English even if the numerals are in Thai.

/completion
{completion}
/endcompletion"""
    
    return await get_gpt_check(completion, r"&(.+?)&", checkprompt, tokensemaphore=tokensemaphore)

#Use GPT to check which sentence pattern the completion follows
async def get_completion_pattern(completion: str, tokensemaphore: TokenLimiter=None):
    checkprompt = f"""The following is a completion prompt asking a GPT-model to perform a math problem in several different languages and numeral system. You need to translate the completion into english and then classify which category the response belongs to. If it outputs just the answer like '३१३६४४' or '321,521' then your response should be '&nocot&'. If it does not contain a number in any numeral system, write '&nonumber&'. If it takes the form of something like '676 গুণিত 464 এর উত্তর হলো 313,664' or 'The product of 676 and 464 is 313664.' which states the problem and then answers write '&cot&'. If it does not follow any of these patterns write '&other&' 

/completion
{completion}
/endcompletion"""
    return await get_gpt_check(completion, r"&(.+?)&", checkprompt, tokensemaphore=tokensemaphore)


#Get numeral systems in the completion
#Keeping this seaparate from find_all_numbers in case of unforseen edge cases
def get_numsystems(completion: str):
    numsystems_list = []
    for numsystem in numsystems:
        if numsystems[numsystem].is_alt(completion):
            numsystems_list.append(numsystem)
    return numsystems_list

#Get a list of all numbers of a particular number system
def find_numbers(completion: str, numsystem: str):
    converter = numsystems[numsystem]
    # The regex pattern below captures numbers including ',' in between for example '12,345'
    pattern = re.compile(r"(?:[\d]+,)*[\d]+")
    # Initialize an empty list to hold the numbers
    numbers = []
    # Iterate over all matched patterns
    for match in pattern.finditer(completion):
        # If the number is in alternative number system
        if converter.is_alt(match.group()):
            # Convert the number to alternative number system and add to the list
            numbers.append(match.group())
    return numbers

def find_all_numbers(completion: str):
    numbers = {}
    for numsystem in numsystems:
        numbers[numsystem] = find_numbers(completion, numsystem)
    return numbers

#Check if a number is in the completion, if so return true, the number system, and whether it uses a comma
def find_number(completion: str, answer: int):
    numberlist = find_all_numbers(completion)
    result = []
    for numsystem in numsystems:
        numbers = numberlist[numsystem]
        for number in numbers:
            clean_number = number
            if ',' in clean_number:
                clean_number.replace(',', '')
            clean_number = numsystems[numsystem].to_arabic(clean_number)
            if clean_number and int(clean_number) == answer:
                result.append((number, clean_number, numsystem, ',' in number))
    return result

#Find all candidates for the answer (should only be one most of the time, the only 5 or 6 digit number) and return a list containing the candidate, its numeral system, and whether it uses a comma
def find_answer_candidates(completion: str):
    numberlist = find_all_numbers(completion)
    candidates = []
    for numsystem in numsystems:
        for number in numberlist[numsystem]:
            digits = number.replace(',', '')
            if len(digits) in [5, 6]:
                arabic_form = numsystems[numsystem].to_arabic(digits)
                contains_comma = ',' in number
                candidates.append((number, arabic_form, numsystem, contains_comma))
    return candidates

def clean_completion(completion: str):
    completion = completion.replace('\n', '{newline}')
    return completion