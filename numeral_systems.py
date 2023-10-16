#Handles the numeral conversions necessary for this experiment
#Currently assumes numeral systems that use standard base 10 place numerals
#Could be modified to accomodate other systems such as Chinese or Roman
class Converter:
    def __init__(self, numerals_map: dict):
        self.numerals_map = numerals_map
        self.reverse_numerals_map = {v: k for k, v in numerals_map.items()}

    #Converts back to arabic and then to an int
    def to_arabic(self, num: int):
        arabic = ''
        for digit in str(num):
            arabic += self.reverse_numerals_map.get(digit, '')
        return int(arabic)

    #Converts to the num_arabic system
    def to_alt(self, num: int):
        alt = ''
        for digit in str(num):
            alt += self.numerals_map.get(digit, '')
        return alt

    #A simple detector for the alt system in question
    def is_alt(self, str_num: str):
        return any(c in self.numerals_map.values() for c in str_num)

    #Just checking for arabic numerals
    @staticmethod
    def is_arabic(str_num: str):
        return any('0' <= c <= '9' for c in str_num)
    


#Converters for each numeral system
class PersianConverter(Converter):
    def __init__(self):
        super().__init__({
            "0" : "۰",
            "1" : "۱",
            "2" : "۲",
            "3" : "۳",
            "4" : "۴",
            "5" : "۵",
            "6" : "۶",
            "7" : "۷",
            "8" : "۸",
            "9" : "۹",
        })


class DevanagariConverter(Converter):
    def __init__(self):
        super().__init__({
            "0" : "०",
            "1" : "१",
            "2" : "२",
            "3" : "३",
            "4" : "४",
            "5" : "५",
            "6" : "६",
            "7" : "७",
            "8" : "८",
            "9" : "९",
        })


class BurmeseConverter(Converter):
    def __init__(self):
        super().__init__({
            "0" : "၀",
            "1" : "၁",
            "2" : "၂",
            "3" : "၃",
            "4" : "၄",
            "5" : "၅",
            "6" : "၆",
            "7" : "၇",
            "8" : "၈",
            "9" : "၉",
        })

 
class ThaiConverter(Converter):
    def __init__(self):
        super().__init__({
            "0" : "๐",
            "1" : "๑",
            "2" : "๒",
            "3" : "๓",
            "4" : "๔",
            "5" : "๕",
            "6" : "๖",
            "7" : "๗",
            "8" : "๘",
            "9" : "๙",
        })


class BengaliConverter(Converter):
    def __init__(self):
        super().__init__({
            "0" : "০",
            "1" : "১",
            "2" : "২",
            "3" : "৩",
            "4" : "৪",
            "5" : "৫",
            "6" : "৬",
            "7" : "৭",
            "8" : "৮",
            "9" : "৯",
        })

#Helpful for keeping all numeral systems equivalent even if arabic has special status

class ArabicConverter(Converter):
    def __init__(self):
        super().__init__({
            "0" : "0",
            "1" : "1",
            "2" : "2",
            "3" : "3",
            "4" : "4",
            "5" : "5",
            "6" : "6",
            "7" : "7",
            "8" : "8",
            "9" : "9",
        })