#This contains the specifics of the experiment including generating the data, analyzing the completions, and writing the results to a csv file.
from data_record import Record, converters
from completion_analysis import find_number, get_numsystems, find_answer_candidates, get_languages, get_completion_pattern
import csv
from api_call import TokenLimiter
import os


#Current experiment, including all prompts, operands, and signs
#Future experiments can use the same basic template
def cot_lang_experiment_records():
    englishpreprompt = "Answer in the following format 'The product of {num2} and {num3} is {num6}'. Find the product {num{first}}{sign}{num{second}}"
    simpchinesepreprompt = "请按照以下格式回答 '{num2}{sign}{num3}的结果是{num6}'. 计算 {num{first}}{sign}{num{second}}"
    tradchineseprompt = "請按照以下格式回答 '{num2}{sign}{num3}的結果是{num6}'. 計算 {num{first}}{sign}{num{second}}"
    croatianprompt = "Odgovorite u sljedećem formatu 'Wynik mnożenia {num2}{sign}{num3} wynosi {num6}'. Podaj wynik mnożenia {num{first}}{sign}{num{second}}"
    japaneseprompt = "次の形式で答えてください '{num2}と{num3}を掛けると、{num6}になります。'. かけ算をしましょう {num{first}}{sign}{num{second}}"
    nepaliprompt =  "निम्न ढाँचामा जवाफ दिनुहोस् '{num2} गुणा {num3} को उत्तर {num6}।'. गणना गर्नुहोस् {num{first}}{sign}{num{second}}"
    bengaliprompt = "নিম্ন কাঠামোতে উত্তর দিন '{num2} গুণি {num3} এর উত্তর {num6}।' গণনা করুন। {num{first}}{sign}{num{second}}"
    farsiprompt = "پاسخ را به قالب زیر بدهید 'محصول {num2} و {num3} برابر با {num6} است'. محصول را پیدا کنید {num{first}}{sign}{num{second}}"
    thaiprompt = "ตอบในรูปแบบต่อไปนี้ 'ผลคูณของ {num2} และ {num3} เท่ากับ {num6}'. หาผลคูณ {num{first}}{sign}{num{second}}"
    burmeseprompt = "အောက်ပါပုံစံဖြင့်အဖြေရပါ '{num2} နှင့် {num3} ကိုမျှောက်ပြီးရလဒ်သည် {num6} ဖြစ်သည်။' ကို တွက်ချက်ပါ။ {num{first}}{sign}{num{second}}"
    prompttemplates = [("English CoT", englishpreprompt, ['prompt_language: English']), ("Simplified Chinese CoT", simpchinesepreprompt, ['prompt_language: simplified_chinese']), ("Traditional Chinese CoT", tradchineseprompt, ['prompt_language: traditional_chinese']), ("Croatian CoT", croatianprompt, ['prompt_language: croatian']), ("Japanese CoT", japaneseprompt, ['prompt_language: japanese']), ("Nepali CoT", nepaliprompt, ['prompt_language: nepali']), ("Bengali CoT", bengaliprompt, ['prompt_language: bengali']), ("Farsi CoT", farsiprompt, ['prompt_language: farsi']), ("Thai CoT", thaiprompt, ['prompt_language: thai']), ("Burmese CoT", burmeseprompt, ['prompt_language: burmese'])]
    operandsA = [373]
    operandsB = [323, 878, 555, 494, 676, 464, 212, 939, 414, 979, 575, 181, 373, 291, 767]
    signs = ['*', 'x', '⋅']
    num_systems = converters.keys()
    records = gen_records(operandsA, operandsB, signs, prompttemplates, num_systems)
    return records

#A general function to generate records based on the inputs
def gen_records(operandsA, operandsB, signs, prompttemplates, num_systems):
    records = []
    for first in operandsA:
        for second in operandsB:
            for sign in signs:
                for promptname, promptformat, promptdescriptors in prompttemplates:
                    for numeral_system in num_systems:
                        records.append(Record(first, second, sign, numeral_system, promptname, promptformat, promptdescriptors))

    return records


#Extract all the information for the completion and return it to fill out the datarecord
#Will be experiment specific, but can may apply to multiple
async def analyze_completion(completion: str, answer: int, operandA: int, operandB: int, tokensemaphore: TokenLimiter=None):
    # Initialize variables with default values to avoid errors in case of empty input
    languages = []
    numsystems = []
    operands = []
    check_answer = False
    answer_candidates = []
    answer_string = ''
    answer_number = 0
    answer_comma = False
    answer_numeral_system = ''
    multiple_answers = False
    other_answers = []
    operand_numsystems = []
    operand_answer_same_numsystem = False
    completion_pattern = ''
    
    # Get values from helper functions only if there is any completion
    if completion:
        #Languages
        languages = await get_languages(completion, tokensemaphore=tokensemaphore)
        #Numsystmes
        numsystems = get_numsystems(completion)
        #Operands
        operands = [find_number(completion, operandA)[0][1] if find_number(completion, operandA) else '',
                    find_number(completion, operandB)[0][1] if find_number(completion, operandB) else '']
        #Check the answer
        if find_number(completion, answer):
            check_answer = True
        #Get any answer candidates and info about them
        answer_candidates = find_answer_candidates(completion)
        if answer_candidates:
            answer_string = answer_candidates[0][0]
            answer_number = answer_candidates[0][1]
            answer_comma = answer_candidates[0][3]
            answer_numeral_system = answer_candidates[0][2]
            multiple_answers = len(answer_candidates) > 1
            other_answers = answer_candidates[1:]
        #Get additional details about operands
        operands_full = [find_number(completion, operandA) if find_number(completion, operandA) else [],
                          find_number(completion, operandB) if find_number(completion, operandB) else []]
        operand_numsystems = [operand[0][2] for operand in operands_full if operand]
        operand_answer_same_numsystem = answer_numeral_system in operand_numsystems

        #Get a classification for the completion pattern
        completion_pattern = await get_completion_pattern(completion, tokensemaphore=tokensemaphore)

    #Misc qualities of interest get logged into a dictionary
    misc_qualities = {
        'answer_comma': answer_comma,
        'answer_numeral_system': answer_numeral_system,
        'multiple_answers': multiple_answers,
        'other_answers': other_answers,
        'operands_full': operands_full,
        'operand_numsystems': operand_numsystems,
        'operand_answer_same_numsystem': operand_answer_same_numsystem,
        'completion_pattern': completion_pattern
    }

    return languages, numsystems, operands, check_answer, answer_string, answer_number, misc_qualities


#Write results of the experiment to a csv
def write_to_csv(dict_records, filename):
    # Check if file does not exist to create it and write headers
    file_exists = os.path.isfile(filename)
    with open(filename, 'a+', newline='') as file:
        fieldnames = dict_records[0].keys()
        writer = csv.DictWriter(file, fieldnames,delimiter="|")
        if not file_exists:
            writer.writeheader()  
        for record in dict_records:
            writer.writerow(record)