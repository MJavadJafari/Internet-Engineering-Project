from unittest.mock import patch
from hazm import POSTagger
from flask import Flask, request, make_response, jsonify
from main import *
from hazm.embedding import SentEmbedding


#prepared data
embedding_path = r'/Users/e_ghafour/models/hazm/sent2vec/sent2vec-naab.model'
tagger_path = r'/Users/e_ghafour/models/hazm/pos_tagger.model'
big_sample_text = 'سفارت ایران در مادرید درباره فیلم منتشرشده از «حسن قشقاوی» در مراسم سال نو در کاخ سلطنتی اسپانیا و حاشیه‌سازی‌ها در فضای مجازی اعلام کرد: به تشریفات دربار کتباً اعلام شد سفیر بدون همراه در مراسم حضور خواهد داشت و همچون قبل به دلایل تشریفاتی نمی‌تواند با ملکه دست بدهد. همان‌گونه که کارشناس رسمی تشریفات در توضیحات خود به یک نشریه اسپانیایی گفت این موضوع توضیح مذهبی داشته و هرگز به معنی بی‌احترامی به مقام و شخصیت زن آن هم در سطح ملکه محترمه یک کشور نیست.'
small_sample_text = 'در جنگل ایران گونه‌های جانوری زیادی وجود دارد.'
small_sample_text1 = 'آمازون شامل ببرهای وحشی زیادی است.'
recommender = SingletonRecommender()
sample_dict = {5:small_sample_text, 6:big_sample_text, 7:small_sample_text1}
recommender.init_model(book_data=sample_dict, posTagger_path=tagger_path, sent2vec_path=embedding_path)


def test_insert_book_when_input_big_sample_text_should_return_10_keywords():
    output = recommender.insert_book(1, big_sample_text)
    assert len(output) == 10, f'the number of the keywords should be 10 but it is {len(output)}.'
    recommender.delete_book(id=1)

def test_insert_book_when_input_small_sample_text_should_return_4_keywords():
    output = recommender.insert_book(2, small_sample_text)
    assert len(output) == 4, f'the number of the keywords should be 10 but it is {len(output)}.'
    recommender.delete_book(id=2)

def test_ask_book_when_input_id_is_correct_should_return_2_id():
    output = recommender.ask_book(id=6)
    assert len(output) == 2, f'the number of the ids should be 2 but it is {len(output)}.'
    assert type(output[0]) ==int, f'type of each element should be int and not a {type(output[0])}'

def test_delete_book_when_input_id_is_correct_should_not_exist_in_all_book():
    recommender.delete_book(id=6)
    output = recommender.all_book_id()
    assert 6 not in output, f'the 6th id should be deleted but it is available now'
    recommender.insert_book(id=6, summary=big_sample_text)




# if __name__ == '__main__':
#     test_ask_book_when_input_id_is_correct_should_return_2_id()

#     app = Flask(__name__)
#     print('azinja')
#     with app.test_request_context():
#         routes = [str(rule) for rule in app.url_map.iter_rules()]
#         print(routes)
#     app.run(port=5000)


    

