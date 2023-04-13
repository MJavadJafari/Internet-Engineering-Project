from hazm import (
    Normalizer,
    sent_tokenize,
    word_tokenize,
    POSTagger,
)
from .embedding import SentEmbedding
import nltk
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

grammers = [
    """
NP:
        {<Ne>?<N.*>}    # Noun(s) + Noun(optional) 
        
""",
    """
NP:
        {<N.*><AJ.*>?}    # Noun(s) + Adjective(optional) 
        
""",
]

normalizer = Normalizer()

def text2vec(candidates, sent2vec_model_path="sent2vec.model", sent2vecModel=None):
    if sent2vecModel is None:
        sent2vec_model = SentEmbedding(sent2vec_model_path)
    else:
        sent2vec_model = sent2vecModel
    candidate_vector = [[sent2vec_model[candidate] for candidate in candidates]]
    text_vector = sent2vec_model[" ".join(candidates)]
    return candidate_vector, text_vector

def posTagger(text, pos_model_path="POStagger.model", posTaggerModel=None):
    tokens = [word_tokenize(sent) for sent in sent_tokenize(normalizer.normalize(text))]
    if posTaggerModel is None:
        tagger = POSTagger(pos_model_path)
    else:
        tagger = posTaggerModel
    return tagger.tag_sents(tokens)

def extractGrammer(tagged_text, grammer):
    keyphrase_candidate = set()
    np_parser = nltk.RegexpParser(grammer)
    trees = np_parser.parse_sents(tagged_text)
    for tree in trees:
        for subtree in tree.subtrees(
            filter=lambda t: t.label() == "NP"
        ):
            keyphrase_candidate.add(" ".join(word for word, _ in subtree.leaves()))
    keyphrase_candidate = {kp for kp in keyphrase_candidate if len(kp.split()) <= 5}
    keyphrase_candidate = list(keyphrase_candidate)
    return keyphrase_candidate

def extractCandidates(tagged_text, grammers = grammers):
    all_candidates = set()
    for grammer in grammers:
        all_candidates.update(extractGrammer(tagged_text, grammer))
    return np.array(list(all_candidates))



def vectorSimilarity(candidates_vector, text_vector, norm=True):
    candidate_sim_text = cosine_similarity(
        candidates_vector[0], text_vector.reshape(1, -1)
    )
    candidate_sim_candidate = cosine_similarity(candidates_vector[0])
    if norm:
        candidates_sim_text_norm = candidate_sim_text / np.max(candidate_sim_text)
        candidates_sim_text_norm = 0.5 + (
            candidates_sim_text_norm - np.average(candidates_sim_text_norm)
        ) / np.std(candidates_sim_text_norm)
        np.fill_diagonal(candidate_sim_candidate, np.NaN)
        candidate_sim_candidate_norm = candidate_sim_candidate / np.nanmax(
            candidate_sim_candidate, axis=0
        )
        candidate_sim_candidate_norm = 0.5 + (
            candidate_sim_candidate_norm
            - np.nanmean(candidate_sim_candidate_norm, axis=0)
        ) / np.nanstd(candidate_sim_candidate_norm, axis=0)
        return candidates_sim_text_norm, candidate_sim_candidate_norm
    return candidate_sim_text, candidate_sim_candidate


def extractKeyword(candidates, keyword_num=5, sent2vecModel=None):
    candidates_vector, text_vector = text2vec(candidates, sent2vecModel=sent2vecModel)
    candidate_sim_text_norm, candidate_sim_candidate_norm = vectorSimilarity(
        candidates_vector, text_vector
    )
######### 

    

def embedRank(text, keyword_num, sent2vecModel=None, posTaggerModel=None):
    token_tag = posTagger(text, posTaggerModel=posTaggerModel)
    candidates = extractCandidates(token_tag)
    return extractKeyword(candidates, keyword_num, sent2vecModel=sent2vecModel)


if __name__ == "__main__":
    text = next('ضمن عرض سلام و خسته نباشید خدمت شما تی‌ای محترمه، این یک جمله برای تست کارایی برنامه است.')
    keyword_num = 5
    keywords = embedRank(text, keyword_num)
    print(keywords)