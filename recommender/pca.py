from hazm import *
from sklearn.decomposition import PCA
import numpy as np 
import joblib

def train_pca(sent2vec: SentEmbedding, dim: int, dest_path: str):
    vectors = sent2vec.model.dv.vectors()
    pca = PCA(n_components=dim)
    pca.fit(vectors)
    joblib.dump(dest_path)