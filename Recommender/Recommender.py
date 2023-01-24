import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from hazm import word_tokenize, Normalizer
import multiprocessing
from gensim.test.utils import datapath
from gensim.models.doc2vec import TaggedDocument
from gensim.models import Doc2Vec


class SingletonRecommender:

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(SingletonRecommender, cls).__new__(cls)
        return cls.instance

    def delete_book(self, id):
        self.book_data.pop(id)

    def init_model(self, book_data):
        self.book_data = book_data
        self.embedding_model = SentEmbedding(model_path='C:/Users/delta/PycharmProjects/net/Recommender/sent2vec-naab.model')
        tmp_dic = {}
        for item in book_data:
            tmp_dic[item] = self.embedding_model[book_data[item]]
        self.book_data = tmp_dic

    def insert_book(self, id: int, summary: str):
        book_vec = self.embedding_model[summary]
        self.book_data[id] = book_vec

    def ask_book(self, id: int):

        selected_vec = self.book_data[id]

        similarity_element = cosine_similarity([selected_vec], list(self.book_data.values()))
        similar_indices = similarity_element.argsort()
        similar_indices = np.flip(similar_indices)

        books = np.array(list(self.book_data))

        return list(books[similar_indices][0][1:])


class SentEmbedding:
    """این کلاس شامل توابعی برای تبدیل جمله به برداری از اعداد است.
    Args:
        model_path (str, optional): مسیر فایل امبدینگ.
    """

    def __init__(self, model_path=None):
        if model_path:
            self.load_model(model_path)

    def load_model(self, model_path):
        """فایل امبدینگ را بارگذاری می‌کند.
        Examples:
            >>> sentEmbedding = SentEmbedding()
            >>> sentEmbedding.load_model('sent2vec_model_path')
        Args:
            model_path (str): مسیر فایل امبدینگ.
        """

        self.model = Doc2Vec.load(model_path)

    def train(
        self,
        dataset_path,
        min_count=5,
        workers=multiprocessing.cpu_count() - 1,
        windows=5,
        vector_size=300,
        epochs=10,
        dest_path=None,
    ):
        """یک فایل امبدینگ doc2vec ترین می‌کند.
        Examples:
            >>> sentEmbedding = SentEmbedding()
            >>> sentEmbedding.train(dataset_path = 'dataset.txt', min_count = 10, worker = 6, windows = 3, vector_size = 250, epochs = 35, dest_path = 'doc2vec_model')
        Args:
            dataset_path (str): مسیر فایل متنی.
            min_count (int, optional): مینیموم دفعات تکرار یک کلمه برای حضور آن در لیست کلمات امبدینگ.
            worker (int, optional): تعداد هسته درگیر برای ترین مدل.
            wondows (int, optional): طول پنجره برای لحاظ کلمات اطراف یک کلمه در ترین آن.
            vector_size (int, optional): طول وکتور خروجی به ازای هر جمله.
            epochs (int, optional): تعداد تکرار ترین بر روی کل دیتا.
            dest_path (str, optional): مسیر مورد نظر برای ذخیره فایل امبدینگ.
        """
        workers = 1 if workers == 0 else workers

        doc = SentenceEmbeddingCorpus(dataset_path)

        model = Doc2Vec(
            min_count=min_count,
            window=windows,
            vector_size=vector_size,
            workers=workers,
        )
        model.build_vocab(doc)
        model.train(doc, total_examples=model.corpus_count, epochs=epochs)

        self.model = model

        print("Model trained.")

        if dest_path is not None:
            model.save(dest_path)
            print("Model saved.")

    def __getitem__(self, sent):
        if not self.model:
            raise AttributeError("Model must not be None! Please load model first.")
        return self.get_sentence_vector(sent)


    def get_sentence_vector(self, sent):
        """جمله‌ای را دریافت می‌کند و بردار امبدینگ متناظر با آن را برمی‌گرداند.
        Examples:
            >>> sentEmbedding = SentEmbedding(sent_embedding_file)
            >>> sentEmbedding.get_sentence_vector('این متن به برداری متناظر با خودش تبدیل خواهد شد')
            array([-0.28460968,  0.04566888, -0.00979532, ..., -0.4701098 , -0.3010612 , -0.18577948], dtype=float32)
        Args:
            sent (str): جمله‌ای که می‌خواهید بردار امبیدنگ آن را دریافت کنید.
        Returns:
            (numpy.ndarray(float32)): لیست بردار مرتبط با جملهٔ ورودی.
        """

        if not self.model:
            raise AttributeError("Model must not be None! Please load model first.")
        else:
            tokenized_sent = word_tokenize(sent)
            return self.model.infer_vector(tokenized_sent)

    def similarity(self, sent1, sent2):
        """میزان شباهت دو جمله را برمی‌گرداند.
        Examples:
            >>> sentEmbedding = SentEmbedding(sent_embedding_file)
            >>> sentEmbedding.similarity('شیر حیوانی وحشی است', 'پلنگ از دیگر جانوران درنده است')
            0.8748713
            >>> sentEmbedding.similarity('هضم یک محصول پردازش متن فارسی است', 'شیر حیوانی وحشی است')
            0.2379288
        Args:
            sent1 (str): جملهٔ اول.
            sent2 (str): جملهٔ دوم.
        Returns:
            (float): میزان شباهت دو جمله که عددی بین `0` و`1` است.
        """

        if not self.model:
            raise AttributeError("Model must not be None! Please load model first.")
        else:
            return float(
                str(
                    self.model.similarity_unseen_docs(
                        word_tokenize(sent1), word_tokenize(sent2)
                    )
                )
            )


class SentenceEmbeddingCorpus:
    def __init__(self, data_path):
        self.data_path = data_path

    def __iter__(self):
        corpus_path = datapath(self.data_path)
        normalizer = Normalizer()
        for i, list_of_words in enumerate(open(corpus_path)):
            yield TaggedDocument(
                word_tokenize(normalizer.normalize(list_of_words)), [i]
            )


if __name__ == '__main__':

    recommender = SingletonRecommender()
    recommender.init_model({})
    recommender.insert_book(2, 'دانشجویان این دانشگاه در حال بررسی پروژه خود هستند.')
    recommender.insert_book(5, 'دانش‌آموزان این مدرسه در تلاش برای انجام تمارین هستند.')
    recommender.insert_book(6, 'در جنگل ایران ببرهای بسیاری وجود دارد که در معرض خطر هستند.')
    recommender.insert_book(7, 'تاریخ بیهقی شامل فراز و نشیب بسیار است.')
    print(recommender.ask_book(2))

