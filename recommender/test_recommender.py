from unittest.mock import patch
from SequenceTagger import POSTagger
from main import *
from embedding import *


#prepared data
embedding_path = '/home/ebrahim/training/sent2vecModel/sent2vec-test.model'
tagger_path = '/home/ebrahim/repos/Kahroba/Internet-Engineering-Project/python-crf_uni_iter400_train95_rs10_c1-0.4_c2-0.04.model'
big_sample_text = 'سفارت ایران در مادرید درباره فیلم منتشرشده از «حسن قشقاوی» در مراسم سال نو در کاخ سلطنتی اسپانیا و حاشیه‌سازی‌ها در فضای مجازی اعلام کرد: به تشریفات دربار کتباً اعلام شد سفیر بدون همراه در مراسم حضور خواهد داشت و همچون قبل به دلایل تشریفاتی نمی‌تواند با ملکه دست بدهد. همان‌گونه که کارشناس رسمی تشریفات در توضیحات خود به یک نشریه اسپانیایی گفت این موضوع توضیح مذهبی داشته و هرگز به معنی بی‌احترامی به مقام و شخصیت زن آن هم در سطح ملکه محترمه یک کشور نیست.'
small_sample_text = 'در جنگل ایران گونه‌های جانوری زیادی وجود دارد.'
recommender = SingletonRecommender()
recommender.init_model({}, posTagger_path=tagger_path, embedding_path = embedding_path)



def test_insert_book_when_input_big_sample_text_should_return_10_keywords():
    output = recommender.insert_book(1, big_sample_text)
    assert len(output) == 10, f'the number of the keywords should be 10 but it is {len(output)}.'
    recommender.delete_book(id=1)


def test_insert_book_when_input_small_sample_text_should_return_4_keywords():
    output = recommender.insert_book(2, small_sample_text)
    assert len(output) == 4, f'the number of the keywords should be 10 but it is {len(output)}.'
    recommender.delete_book(id=2)

def test_ask_book_when_input_id_is_corrct_should_return_2_id():
    output = recommender.ask_book(id=6)
    assert len(output) == 2, f'the number of the ids should be 2 but it is {len(output)}.'
    assert type(output[0]) ==int, f'type of each element should be int and not a {type(output[0])}'

def test_print_books_should_return_dict_with_2_element_of_books():
    output = recommender.print_books()
    assert len(output) == 3, f'there are only 3 books inserted, but now it has {len(output)}'
    assert type(output) == dict



# if __name__ == '__main__':
    

