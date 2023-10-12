from api_call import begin_async, end_async, api_call, create_chat_completion_sync
import asyncio
import random
import time

import unittest
from numeral_systems import PersianConverter, DevanagariConverter, BurmeseConverter, ThaiConverter, BengaliConverter
from data_record import Record, converters

class TestRecord(unittest.TestCase):

    def test_constructor(self):
        # Test initialization of Record object
        record = Record(2, 3, '+', 'Persian', 'Test', 'Example format', ['descriptor1', 'descriptor2'])
        self.assertEqual(record.first, 2)
        self.assertEqual(record.second, 3)
        self.assertEqual(record.promptname, 'Test')
        # ... continue asserting other attributes

    def test_update_results(self):
        # Test update_results function
        record = Record(2, 3, '+', 'Persian', 'Test', 'Example format', ['descriptor1', 'descriptor2'])
        record.update_results('completion', ['lang1', 'lang2'], ['Persian', 'Arabic'], 'operand', 'answer', ['desc1', 'desc2'])
        self.assertEqual(record.completion, 'completion')
        self.assertEqual(record.completionLanguages, ['lang1', 'lang2'])
        # ... continue asserting other attributes

    def test_to_dict(self):
        # Test to_dict function
        record = Record(2, 3, '+', 'Persian', 'Test', 'Example format', ['descriptor1', 'descriptor2'])
        dict_record = record.to_dict()
        self.assertEqual(dict_record['first'], 2)
        self.assertEqual(dict_record['second'], 3)
        # ... continue asserting other attributes

    def test_to_csv(self):
        # Test to_csv function
        record = Record(2, 3, '+', 'Persian', 'Test', 'Example format', ['descriptor1', 'descriptor2'])
        csv_record = record.to_csv()
        self.assertIsInstance(csv_record, str)  # check if csv_record is indeed string
        # check if csv string contains all elements
        self.assertTrue(str(2) in csv_record)
        self.assertTrue('+' in csv_record)
        self.assertTrue('Test' in csv_record)
        # ... continue asserting other elements

class TestConverters(unittest.TestCase):
    def test_persian_converter(self):
        converter = PersianConverter()
        self.assertEqual(converter.to_alt(123), '۱۲۳')
        self.assertEqual(converter.to_arabic('۱۲۳'), 123)
        self.assertTrue(converter.is_alt('۱2۳'))
        self.assertTrue(converter.is_arabic('12۳'))
        self.assertFalse(converter.is_alt('123'))
        self.assertFalse(converter.is_arabic('۱۲۳'))

    def test_devanagari_converter(self):
        converter = DevanagariConverter()
        self.assertEqual(converter.to_alt(123), '१२३')
        self.assertEqual(converter.to_arabic('१२३'), 123)
        self.assertTrue(converter.is_alt('१2३'))
        self.assertTrue(converter.is_arabic('12३'))
        self.assertFalse(converter.is_alt('123'))
        self.assertFalse(converter.is_arabic('१२३'))

    def test_burmese_converter(self):
        converter = BurmeseConverter()
        self.assertEqual(converter.to_alt(123), '၁၂၃')
        self.assertEqual(converter.to_arabic('၁၂၃'), 123)
        self.assertTrue(converter.is_alt('၁2၃'))
        self.assertTrue(converter.is_arabic('12၃'))
        self.assertFalse(converter.is_alt('123'))
        self.assertFalse(converter.is_arabic('၁၂၃'))

    def test_thai_converter(self):
        converter = ThaiConverter()
        self.assertEqual(converter.to_alt(123), '๑๒๓')
        self.assertEqual(converter.to_arabic('๑๒๓'), 123)
        self.assertTrue(converter.is_alt('๑2๓'))
        self.assertTrue(converter.is_arabic('12๓'))
        self.assertFalse(converter.is_alt('123'))
        self.assertFalse(converter.is_arabic('๑๒๓'))

    def test_bengali_converter(self):
        converter = BengaliConverter()
        self.assertEqual(converter.to_alt(123), '১২৩')
        self.assertEqual(converter.to_arabic('১২৩'), 123)
        self.assertTrue(converter.is_alt('১2৩'))
        self.assertTrue(converter.is_arabic('12৩'))
        self.assertFalse(converter.is_alt('123'))
        self.assertFalse(converter.is_arabic('১২৩'))


##Async tests

async def test_async():
    begin_async()
    start = time.time()
    tasks = []

    for i in range(5):
        for j in range(5):
            operator = random.choice(['+', '-', '*', '/'])
            prompt = str(i) + operator + str(j) + '='
            tasks.append(api_call(prompt, model='gpt-3.5-turbo'))
    results = await asyncio.gather(*tasks)
    
    for result in results:
        print(result)

    end = time.time()
    print(f'Completion time is {end - start}')
    await end_async()

def test_sync():
    #set up timer
    start = time.time()
    #iterate through two one-digit random number lists as operands
    for i in range(5):
        for j in range(5):
            #generate random operator
            operator = random.choice(['+', '-', '*', '/'])
            #generate prompt
            prompt = str(i) + operator + str(j) + '='
            #call api
            #use turbo to save on credits
            result = create_chat_completion_sync(prompt, model='gpt-3.5-turbo')

    #end timer
    end = time.time()
    print(f'Completion time is {end - start}')


def test_async_vs_sync():
    test_sync()
    asyncio.run(test_async())


###Numeral tests

#main function
if __name__ == '__main__':
    unittest.main()
