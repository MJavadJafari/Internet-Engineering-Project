import numpy as np 
import pandas as pd 
from embedding import SentEmbedding
from sklearn.metrics.pairwise import cosine_similarity

 

class Recommender:
    
    def __init__(self, book_data):
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
        similarity_indices = similarity_element.argsort()
        # return list(similarity_element[])


        


        






if __name__ == '__main__':
    recommender = Recommender()
    




