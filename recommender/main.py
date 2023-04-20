import numpy as np
from embedding import SentEmbedding
from hazm import POSTagger
from sklearn.metrics.pairwise import cosine_similarity
import embedRank
from flask import Flask, request, make_response, jsonify
from SequenceTagger import POSTagger

app = Flask(__name__)
sent2vec_path = r'C:\Users\delta\PycharmProjects\net\recommender\sent2vec-naab.model'
posTagger_path = r'C:\Users\delta\PycharmProjects\net\recommender\posTagger.model'


class SingletonRecommender:

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(SingletonRecommender, cls).__new__(cls)
        return cls.instance

    def init_model(self, book_data, sent2vec_path=sent2vec_path, posTagger_path=posTagger_path):
        self.embedding_model = SentEmbedding(model_path= sent2vec_path)
        self.posTagger = POSTagger(model = posTagger_path)
        tmp_dic = {}
        for item in book_data:
            summary = book_data[item]
            keywords = np.unique(embedRank.embedRank(summary, max(4, len(summary.split()) / 8), self.embedding_model, self.posTagger))
            tmp_dic[item] = [self.embedding_model[keyword] for keyword in keywords]
        self.book_data = tmp_dic

    def insert_book(self, id: int, summary: str):
        keywords = np.unique(embedRank.embedRank(summary, max(4, len(summary.split()) / 8), self.embedding_model, self.posTagger))
        self.book_data[id] = [self.embedding_model[keyword] for keyword in keywords]
        # return keywords in list
        return keywords.tolist()

    def delete_book(self, id):
        self.book_data.pop(id)

    def print_books(self):
        print(self.book_data)

    def ask_book(self, id: int):
        selected_vec = self.book_data[id]
        sim_dic = {}
        for i in self.book_data:
            sim_dic[i] = np.max(cosine_similarity(selected_vec, self.book_data[i]))
        similar_indices = sorted(sim_dic, key=sim_dic.get, reverse=True)

        return similar_indices[1:]


@app.route('/init_model', methods=['POST'])
def init_model():
    book_data = request.form.get('book_data')
    recommender.init_model(book_data, sent2vec_path, posTagger_path)
    return 'success'


@app.route('/insert_book', methods=['POST'])
def insert_book():
    id = int(request.form.get('id'))
    summary = request.form.get('summary')
    result = recommender.insert_book(id, summary)
    print(result)
    return jsonify(result)


@app.route('/delete_book', methods=['POST'])
def delete_book():
    id = int(request.form.get('id'))
    recommender.delete_book(id)
    return 'success'


@app.route('/print_books')
def print_books():
    recommender.print_books()
    return 'success'


@app.route('/ask_book', methods=['POST'])
def ask_book():
    id = int(request.form.get('id'))
    return recommender.ask_book(id)


if __name__ == '__main__':
    recommender = SingletonRecommender()
    recommender.init_model({})
    app.run(port=5000)
