import numpy as np 
import pandas as pd 
from embedding import SentEmbedding
from sklearn.metrics.pairwise import cosine_similarity


class SingletonRecommender:

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(SingletonRecommender, cls).__new__(cls)
        return cls.instance

    def init_model(self, book_data):
        self.embedding_model = SentEmbedding(model_path= '/home/ebrahim/Desktop/sent2vec/sent2vec-naab.model')
        tmp_dic = {}
        for item in book_data:
            tmp_dic[item] = self.embedding_model[book_data[item]]
        self.book_data = tmp_dic

    def insert_book(self, id: int, summary: str):
        book_vec = self.embedding_model[summary]
        self.book_data[id] = book_vec 

    def delete_book(self, id):
        self.book_data.pop(id)

    def print_books(self):
        print(self.book_data)

    def ask_book(self, id: int):

        selected_vec = self.book_data[id]

        similarity_element = cosine_similarity([selected_vec], list(self.book_data.values()))
        similar_indices = similarity_element.argsort()
        similar_indices = np.flip(similar_indices)

        books = np.array(list(self.book_data))

        return list(books[similar_indices][0][1:])


if __name__ == '__main__':

    recommender = SingletonRecommender()