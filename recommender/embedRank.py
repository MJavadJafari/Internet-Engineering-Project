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

def extractKeyword(candidates, keyword_num=5, sent2vecModel=None):
    None

def embedRank(text, keyword_num, sent2vecModel=None, posTaggerModel=None):
    token_tag = posTagger(text, posTaggerModel=posTaggerModel)
    candidates = extractCandidates(token_tag)
    return extractKeyword(candidates, keyword_num, sent2vecModel=sent2vecModel)


if __name__ == "__main__":
    text = next('ضمن عرض سلام و خسته نباشید خدمت شما تی‌ای محترمه، این یک جمله برای تست کارایی برنامه است.')
    keyword_num = 5
    keywords = embedRank(text, keyword_num)
    print(keywords)