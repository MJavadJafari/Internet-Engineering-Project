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
        self.book_data = book_data
        self.embedding_model = SentEmbedding(model_path= '')

    def insert_book(self, id: int, summary: str):
        book_vec = self.embedding_model[summary]
        self.book_data[id] = book_vec 

    def ask_book(self, id: int, num_book: int):
        if(num_book > self.book_data + 1):
            print('the total number of books is lower than the requested number...')
            return None

        selected_vec = self.book_data[id]

        similarity_element = cosine_similarity(selected_vec, list(self.book_data))
        similar_indices = similarity_element.argsort()
        similar_indices = np.flip(similar_indices)

        books = np.array(list(self.book_data))

        books[similar_indices]

        return books[similar_indices][0]


if __name__ == '__main__':

    recommender = SingletonRecommender()
    




