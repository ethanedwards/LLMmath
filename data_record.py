from numeral_systems import PersianConverter, DevanagariConverter, BurmeseConverter, BengaliConverter, ThaiConverter, ArabicConverter
import re

converters = {
    'Persian': PersianConverter(),
    'Devanagari': DevanagariConverter(),
    'Burmese': BurmeseConverter(),
    'Bengali': BengaliConverter(),
    'Thai': ThaiConverter(),
    'Arabic': ArabicConverter()
}

class Record:
    def __init__(self, first: int, second: int, sign: str, numeral_system: str, promptname: str, promptformat: str, promptdescriptors: list):
        self.first = first
        self.second = second
        self.sign = sign
        self.answer = first * second
        self.numeral_system = numeral_system
        self.promptname = promptname
        self.promptdescriptors = promptdescriptors
        self.completion = None
        self.completionLanguages = None
        self.completionNumeralSystems = None
        self.completionOperands = None
        self.completionAnswer = None
        self.completionAnswerArabic = None
        self.completionCorrect = None
        self.completionDescriptors = None

        # Convert first and second to the given numeral system.
        self.converter = converters.get(numeral_system, lambda x: str(x))  # Default to identity function for Arabic numeral system
        self.numfirst = self.converter.to_alt(first)
        self.numsecond = self.converter.to_alt(second)
        #Replace prompt with formatted strings
        #This assumes that prompt format will be of the following format
        #"Odgovorite u sljedećem formatu 'Wynik mnożenia {num2}{sign}{num3} wynosi {num6}'. Podaj wynik mnożenia {numfirst}{sign}{numsecond}"
        new_promptformat = promptformat
        new_promptformat = new_promptformat.replace('{first}', str(first))
        new_promptformat = new_promptformat.replace('{second}', str(second))
        new_promptformat = new_promptformat.replace('{sign}', str(sign))
        for match in re.findall(r'\{num(\d+)\}', new_promptformat):
            number = int(match)
            new_promptformat = new_promptformat.replace('{num' + match + '}', converters[numeral_system].to_alt(number))

        # Replace prompt with formatted strings
        self.prompt = new_promptformat.format(first=self.first, second=self.second, numfirst=self.numfirst, numsecond=self.numsecond, sign=sign)

    def update_results(self, completion: str, completionLanguages: list, completionNumeralSystems: list, completionOperands: str, completionAnswer: str, completionAnswerArabic: int, completionCorrect: bool, completionDescriptors: list):
        self.completion = completion
        self.completionLanguages = completionLanguages
        self.completionNumeralSystems = completionNumeralSystems
        self.completionOperands = completionOperands
        self.completionAnswer = completionAnswer
        self.completionAnswerArabic = completionAnswerArabic
        self.completionCorrect = completionCorrect
        self.completionDescriptors = completionDescriptors

    def output_prompt(self):
        return self.prompt
    
    def output_completion_vars(self):
        return self.answer, self.first, self.second

    def to_dict(self):
        return {
            'first': self.first,
            'second': self.second,
            'sign': self.sign,
            'numeral_system': self.numeral_system,
            'promptname': self.promptname,
            'promptdescriptors': self.promptdescriptors,
            'prompt': self.prompt,
            'completion': self.completion,
            'completionLanguages': self.completionLanguages,
            'completionNumeralSystems': self.completionNumeralSystems,
            'completionOperands': self.completionOperands,
            'completionAnswer': self.completionAnswer,
            'completionDescriptors': self.completionDescriptors
        }
    
    def to_csv(self, divider: str = '|'):
        return divider.join([str(self.first), str(self.second), str(self.sign), str(self.numeral_system), str(self.promptname), str(self.promptdescriptors), str(self.prompt), str(self.completion), str(self.completionLanguages), str(self.completionNumeralSystems), str(self.completionOperands), str(self.completionAnswer), str(self.completionDescriptors)])
