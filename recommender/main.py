import numpy as np
from hazm import SentEmbedding
from sklearn.metrics.pairwise import cosine_similarity
import embedRank
import pca
import joblib
import heapq
from flask import Flask, request, make_response, jsonify
from hazm import POSTagger
from configparser import ConfigParser



config_file_path = '/Users/e_ghafour/repos/kahroba/Internet-Engineering-Project/recommender/config.ini'


big_sample_text = 'سفارت ایران در مادرید درباره فیلم منتشرشده از «حسن قشقاوی» در مراسم سال نو در کاخ سلطنتی اسپانیا و حاشیه‌سازی‌ها در فضای مجازی اعلام کرد: به تشریفات دربار کتباً اعلام شد سفیر بدون همراه در مراسم حضور خواهد داشت و همچون قبل به دلایل تشریفاتی نمی‌تواند با ملکه دست بدهد. همان‌گونه که کارشناس رسمی تشریفات در توضیحات خود به یک نشریه اسپانیایی گفت این موضوع توضیح مذهبی داشته و هرگز به معنی بی‌احترامی به مقام و شخصیت زن آن هم در سطح ملکه محترمه یک کشور نیست.'
small_sample_text = 'در جنگل ایران گونه‌های جانوری زیادی وجود دارد.'
small_sample_text1 = 'آمازون شامل ببرهای وحشی زیادی است.'
sample_dict = {5:small_sample_text, 6:big_sample_text, 7:small_sample_text1}


app = Flask(__name__)
# sent2vec_path = r'C:\Users\delta\PycharmProjects\net\recommender\sent2vec-naab.model'
# posTagger_path = r'C:\Users\delta\PycharmProjects\net\recommender\posTagger.model'



config = ConfigParser()
config.read(config_file_path)

sent2vec_path = config.get('MAIN_MODEL', 'sent2vec')
posTagger_path = config.get('MAIN_MODEL', 'pos_tagger')
pca_path = config.get('MAIN_MODEL', 'pca')
train_pca = config.getboolean('MAIN_MODEL', 'train_pca')
pca_dim = config.getint('MAIN_MODEL', 'pca_dim')
new_pca = config.get('MAIN_MODEL', 'new_pca')


class SingletonRecommender:

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(SingletonRecommender, cls).__new__(cls)
        return cls.instance

    def init_model(self, book_data, sent2vec_path=sent2vec_path, posTagger_path=posTagger_path, pca_path=pca_path):
        self.embedding_model = SentEmbedding(model_path= sent2vec_path)
        self.posTagger = POSTagger(model = posTagger_path)
        self.pca = joblib.load(pca_path)
        tmp_dic = {}
        for item in book_data:
            summary = book_data[item]
            item = int(item)
            keywords = np.unique(embedRank.embedRank(summary, max(4, len(summary.split()) / 8), self.embedding_model, self.posTagger))
            # tmp_dic[item] = [self.embedding_model[keyword] for keyword in keywords]
            tmp_dic[item] = self.pca.transform([self.embedding_model[keyword] for keyword in keywords]).tolist()
        self.book_data = tmp_dic

    def insert_book(self, id: int, summary: str):
        keywords = np.unique(embedRank.embedRank(summary, max(4, len(summary.split()) / 8), self.embedding_model, self.posTagger))
        # self.book_data[id] = [self.embedding_model[keyword] for keyword in keywords]
        self.book_data[id] = self.pca.transform([self.embedding_model[keyword] for keyword in keywords]).tolist()
        # return keywords in list
        return keywords.tolist()

    def delete_book(self, id):
        if(id in self.book_data.keys()):
            self.book_data.pop(id)

    def ask_book(self, id: int, topn=5):
        selected_vec = self.book_data[id]
        sim_dic = {}
        # for i in self.book_data:
        #     sim_dic[i] = np.max(cosine_similarity(selected_vec, self.book_data[i]))
        sim_dic = {i:np.max(cosine_similarity(selected_vec, self.book_data[i])) for i in self.book_data}
        topn += 1 
        topn = min(len(self.book_data), topn)

        similar_indices = heapq.nlargest(topn, sim_dic, key=sim_dic.get)
        # similar_indices = sorted(sim_dic, key=sim_dic.get, reverse=True)

        return similar_indices[1:]
    
    def all_book_id(self):
        return list(self.book_data.keys())


@app.route('/init_model', methods=['POST'])
def init_model():
    # book_data = request.form.get('book_data')
    book_data = request.get_json()
    recommender.init_model(book_data, sent2vec_path, posTagger_path)
    return 'success'


@app.route('/insert_book', methods=['POST'])
def insert_book():
    id = int(request.form.get('id'))
    summary = request.form.get('summary')

    result = recommender.insert_book(id, summary)
    return jsonify(result)


@app.route('/delete_book', methods=['POST'])
def delete_book():
    id = int(request.form.get('id'))
    recommender.delete_book(id)
    return 'success'


@app.route('/all_book_id')
def all_book_id():
    return jsonify(recommender.all_book_id())
    

@app.route('/ask_book', methods=['POST'])
def ask_book():
    id = int(request.form.get('id'))
    return recommender.ask_book(id)

recommender = SingletonRecommender()

if __name__ == '__main__':
    #for locust...
    recommender.init_model(sample_dict, sent2vec_path, posTagger_path)
    print(recommender.all_book_id())
    
    # recommender.init_model({})
    app.run(port=5000)
