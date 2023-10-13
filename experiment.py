#This contains the specifics of the experiment including generating the data, analyzing the completions, and writing the results to a csv file.
from data_record import Record, converters

def cot_lang_experiment():
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
    operandsA = [373, 291, 767]
    operandsB = [323, 878, 555, 494, 676, 464, 212, 939, 414, 979, 575, 181, 373, 291, 767]
    signs = ['*', 'x', '⋅']
    num_systems = converters.keys()
    records = gen_records(operandsA, operandsB, signs, prompttemplates, num_systems)


def gen_records(operandsA, operandsB, signs, prompttemplates, num_systems):
    records = []
    for first in operandsA:
        for second in operandsB:
            for sign in signs:
                for promptname, promptformat, promptdescriptors in prompttemplates:
                    for numeral_system in num_systems:
                        records.append(Record(first, second, sign, numeral_system, promptname, promptformat, promptdescriptors))

    return records

