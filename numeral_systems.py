class Converter:
    def __init__(self, numerals_map):
        self.numerals_map = numerals_map
        self.reverse_numerals_map = {v: k for k, v in numerals_map.items()}

    def to_arabic(self, num):
        arabic = ''
        for digit in str(num):
            arabic += self.reverse_numerals_map.get(digit, '')
        return int(arabic)

    def to_alt(self, num):
        alt = ''
        for digit in str(num):
            alt += self.numerals_map.get(digit, '')
        return alt

    def is_alt(self, str_num):
        return any(c in self.numerals_map.values() for c in str_num)

    @staticmethod
    def is_arabic(str_num):
        return any('0' <= c <= '9' for c in str_num)
    

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