import numpy as np 
from embedding import SentEmbedding
from hazm import POSTagger
from sklearn.metrics.pairwise import cosine_similarity
import embedRank


class SingletonRecommender:

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(SingletonRecommender, cls).__new__(cls)
        return cls.instance

    def init_model(self, book_data):
        self.embedding_model = SentEmbedding(model_path= '/home/ebrahim/Desktop/sent2vec/sent2vec-naab.model')
        self.posTagger = POSTagger(model = '/home/ebrahim/training/postagger.model')
        tmp_dic = {}
        for item in book_data:
            summary = book_data[item]
            keywords = np.unique(embedRank.embedRank(summary, max(4, len(summary.split()) / 8), self.embedding_model, self.posTagger))
            tmp_dic[item] = [self.embedding_model[keyword] for keyword in keywords]
        self.book_data = tmp_dic

    def insert_book(self, id: int, summary: str):
        keywords = np.unique(embedRank.embedRank(summary, max(4, len(summary.split()) / 8), self.embedding_model, self.posTagger))
        self.book_data[id] = [self.embedding_model[keyword] for keyword in keywords]
        return keywords

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
        # similarity_element = cosine_similarity(selected_vec, list(self.book_data.values()))
        # similar_indices = similarity_element.argsort()
        # similar_indices = np.flip(similar_indices)

        # books = np.array(list(self.book_data))

        # return list(books[similar_indices][0][1:])


if __name__ == '__main__':

    recommender = SingletonRecommender()
    recommender.init_model({})
    recommender.insert_book(2, 'دانشجویان این دانشگاه در حال بررسی پروژه خود هستند.')
    recommender.insert_book(5, 'دانش‌آموزان این مدرسه در تلاش برای انجام تمارین هستند.')
    recommender.insert_book(6, 'در جنگل ایران ببرهای بسیاری وجود دارد که در معرض خطر هستند.')
    recommender.insert_book(7, 'تاریخ بیهقی شامل فراز و نشیب بسیار است.')
    print(recommender.ask_book(2))
    recommender.print_books()