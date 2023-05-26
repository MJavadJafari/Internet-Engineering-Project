from unittest.mock import patch
import json
import ast
import pytest
from hazm import POSTagger
from flask import Flask, request, make_response, jsonify
from main import *
from hazm import SentEmbedding


#prepared data
embedding_path = r'~/models/hazm/light_sent2vec.model'
tagger_path = r'/Users/e_ghafour/models/hazm/pos_tagger.model'
big_sample_text = 'سفارت ایران در مادرید درباره فیلم منتشرشده از «حسن قشقاوی» در مراسم سال نو در کاخ سلطنتی اسپانیا و حاشیه‌سازی‌ها در فضای مجازی اعلام کرد: به تشریفات دربار کتباً اعلام شد سفیر بدون همراه در مراسم حضور خواهد داشت و همچون قبل به دلایل تشریفاتی نمی‌تواند با ملکه دست بدهد. همان‌گونه که کارشناس رسمی تشریفات در توضیحات خود به یک نشریه اسپانیایی گفت این موضوع توضیح مذهبی داشته و هرگز به معنی بی‌احترامی به مقام و شخصیت زن آن هم در سطح ملکه محترمه یک کشور نیست.'
small_sample_text = 'در جنگل ایران گونه‌های جانوری زیادی وجود دارد.'
small_sample_text1 = 'آمازون شامل ببرهای وحشی زیادی است.'
test_recommender = SingletonRecommender()
sample_dict = {5:small_sample_text, 6:big_sample_text, 7:small_sample_text1}
test_recommender.init_model(book_data=sample_dict, posTagger_path=tagger_path, sent2vec_path=embedding_path)
recommender = test_recommender

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_insert_book_when_input_big_sample_text_should_return_10_keywords():
    output = test_recommender.insert_book(1, big_sample_text)
    assert len(output) == 10, f'the number of the keywords should be 10 but it is {len(output)}.'
    test_recommender.delete_book(id=1)

def test_insert_book_when_input_small_sample_text_should_return_4_keywords():
    output = test_recommender.insert_book(2, small_sample_text)
    assert len(output) == 4, f'the number of the keywords should be 4 but it is {len(output)}.'
    test_recommender.delete_book(id=2)

def test_ask_book_when_input_id_is_correct_should_return_2_id():
    output = test_recommender.ask_book(id=6)
    assert len(output) == 2, f'the number of the ids should be 2 but it is {len(output)}.'
    assert type(output[0]) ==int, f'type of each element should be int and not a {type(output[0])}'

def test_delete_book_when_input_id_is_correct_should_not_exist_in_all_book():
    test_recommender.delete_book(id=6)
    output = test_recommender.all_book_id()
    assert 6 not in output, f'the 6th id should be deleted but it is available now'
    test_recommender.insert_book(id=6, summary=big_sample_text)

def test_text2vec_when_model_is_none_should_return_2_outputs():
    candidate_vector, text_vector = embedRank.text2vec(['دریا', 'ایران'], sent2vec_model_path=embedding_path)
    assert len(candidate_vector[0]) == 2, f'the len of input is 2, so the output should return a list with 2 elements'
    assert len(text_vector) == 200, f'the output of the embedding is in 300 dimention but it has {len(text_vector)} dimentions'

def test_posTagger_of_embedRank_when_model_is_none_should_return_list_of_tuplels():
    tagged_sent = embedRank.posTagger(text=small_sample_text, pos_model_path=tagger_path)
    assert tagged_sent[0][0][0] == 'در', f'the output of the function is tagged in a wrong way'
    assert tagged_sent[0][0][1] == 'ADP', f'the tag of the input is wrong'

def test_vectorSimilarity_of_embedRank_False_norm_should_return_2_arrays_of_len_2():
    candidate_vector, text_vector = embedRank.text2vec(['دریا', 'ایران'], sent2vecModel=test_recommender.embedding_model)
    candidate_sim_text, candidate_sim_candidate = embedRank.vectorSimilarity(candidate_vector, text_vector, norm=False)
    assert len(candidate_sim_text) == 2, f'the output len should be 2 but it is {len(candidate_sim_text)}'
    assert candidate_sim_candidate.shape == (2,2), f'the output matrix shape should be (2, 2) but the shape is {candidate_sim_candidate.shape}'

def test_Flask_insert_book_when_input_small_sample_text_should_return_4_keywords(client):
    book_data = {'id': 2, 'summary': small_sample_text}
    response = client.post('/insert_book', data=book_data)
    output = ast.literal_eval(response.data.decode('utf-8'))
    assert len(output) == 4, f'the number of the keywords should be 4 but it is {len(output)}.'
    test_recommender.delete_book(id=2)
    assert response.status_code == 200

def test_Flask_delete_book_when_input_id_is_correct_should_not_exist_in_all_book(client):
    book_id = {'id': 6}
    response = client.post('/delete_book', data=book_id)
    output = test_recommender.all_book_id()
    assert response.status_code == 200
    assert response.data.decode('utf-8') == 'success'
    assert 6 not in output, f'the 6th id should be deleted but it is available now'
    test_recommender.insert_book(id=6, summary=big_sample_text)

def test_Flask_all_book_id_should_return_3_books_id(client):
    response = client.get('/all_book_id')
    book_ids = json.loads(response.data)
    assert response.status_code == 200
    assert len(book_ids) == 3, f'there is only 3 books available in that object but it returns {len(book_ids)} book ids'

def test_Flask_ask_book_when_input_id_is_correct_should_return_2_id(client):
    book_id = {'id': 6}
    response = client.post('/ask_book', data=book_id)
    output = json.loads(response.data)
    assert response.status_code == 200
    assert len(output) == 2, f'the number of the ids should be 2 but it is {len(output)}.'
    assert type(output[0]) ==int, f'type of each element should be int and not a {type(output[0])}'




# if __name__ == '__main__':
#     test_ask_book_when_input_id_is_correct_should_return_2_id()

#     app = Flask(__name__)
#     print('azinja')
#     with app.test_request_context():
#         routes = [str(rule) for rule in app.url_map.iter_rules()]
#         print(routes)
#     app.run(port=5000)