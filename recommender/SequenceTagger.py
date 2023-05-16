import time

import numpy as np
from pycrfsuite import Tagger, Trainer
from sklearn.metrics import accuracy_score


def features(sent, index):
    return {
        "word": sent[index],
        "is_first": index == 0,
        "is_last": index == len(sent),
        "is_num": sent[index].isdigit(),
        "prev_word": sent[index - 1] if index != 0 else "",
        "next_word": sent[index + 1] if index != len(sent) - 1 else "",
    }


def data_maker(tokens):
    return [[features(sent, index) for index in range(len(sent))] for sent in tokens]


def iob_features(words, pos_tags, index):
    word_features = features(words, index)
    word_features.update(
        {
            "pos": pos_tags[index],
            "prev_pos": "" if index == 0 else pos_tags[index - 1],
            "next_pos": "" if index == len(pos_tags) - 1 else pos_tags[index + 1],
        },
    )
    return word_features


def iob_data_maker(tokens):
    words = [[word for word, _ in token] for token in tokens]
    tags = [[tag for _, tag in token] for token in tokens]
    return [
        [
            iob_features(words=word_tokens, pos_taggs=tag_tokens, index=index)
            for index in range(len(word_tokens))
        ]
        for word_tokens, tag_tokens in zip(words, tags)
    ]


class SequenceTagger:
    """این کلاس شامل توابعی برای برچسب‌گذاری توکن‌ها است. این کلاس در نقش یک
    wrapper برای کتابخانهٔ [python-](https://python-crfsuite.readthedocs.io/en/latest/) است.

    Args:
        model (str, optional): مسیر فایل tagger.
        data_maker (function, optional): تابعی که لیستی دو بعدی از کلمات توکنایز شده را گرفته و لیست دو بعدی از از دیکشنری‌هایی که تعیین‌کننده ویژگی‌ها هر کلمه هستند را برمی‌گرداند.

    """

    def __init__(self, model=None, data_maker=data_maker) -> None:
        if model is not None:
            self.load_model(model)
        else:
            self.model = None
        self.data_maker = data_maker

    def __add_label(self, sentence, tags):
        return [(word, tag) for word, tag in zip(sentence, tags)]

    def __tag(self, tokens):
        return self.__add_label(tokens, self.model.tag(self.data_maker([tokens])[0]))

    def __train(self, X, y, args, verbose, file_name, report_duration):
        trainer = Trainer(verbose=verbose)
        trainer.set_params(args)

        for xseq, yseq in zip(X, y):
            trainer.append(xseq, yseq)

        start_time = time.time()
        trainer.train(file_name)
        end_time = time.time()

        if report_duration:
            print(f"training time: {(end_time - start_time):.2f} sec")

        self.load_model(file_name)

    def __evaluate(self, gold_labels, predicted_labels):
        gold_labels = np.concatenate(gold_labels)
        predicted_labels = np.concatenate(predicted_labels)
        return float(accuracy_score(gold_labels, predicted_labels))

    def load_model(self, model):
        """فایل تگر را بارگزاری می‌کند.

        Examples:
            >>> tagger = SequenceTagger()
            >>> tagger.load_model(model = 'tagger.model')

        Args:
            model (str): مسیر فایل تگر.

        """
        tagger = Tagger()
        tagger.open(model)
        self.model = tagger

    def tag(self, tokens):
        """یک جمله را در قالب لیستی از توکن‌ها دریافت می‌کند و در خروجی لیستی از
        `(توکن، برچسب)`ها برمی‌گرداند.

        Examples:
            >>> tagger = SequenceTagger(model = 'tagger.model')
            >>> tagger.tag(tokens = ['من', 'به', 'مدرسه', 'ایران', 'رفته_بودم', '.'])
            [('من', 'PRON'), ('به', 'ADP'), ('مدرسه', 'NOUN,EZ'), ('ایران', 'NOUN'), ('رفته_بودم', 'VERB'), ('.', 'PUNCT')]

        Args:
            tokens (List[str]): لیستی از توکن‌های یک جمله که باید برچسب‌گذاری شود.

        Returns:
            (List[Tuple[str,str]]): ‌لیستی از `(توکن، برچسب)`ها.

        """
        assert self.model is not None, "you should load model first..."
        return self.__tag(tokens)

    def tag_sents(self, sentences):
        """جملات را در قالب لیستی از توکن‌ها دریافت می‌کند
        و در خروجی، لیستی از لیستی از `(توکن، برچسب)`ها برمی‌گرداند.

        هر لیست از `(توکن، برچسب)`ها مربوط به یک جمله است.

        Examples:
            >>> tagger = SequenceTagger(model = 'tagger.model')
            >>> tagger.tag_sents(sentences = [['من', 'به', 'مدرسه', 'ایران', 'رفته_بودم', '.']])
            [[('من', 'PRON'), ('به', 'ADP'), ('مدرسه', 'NOUN,EZ'), ('ایران', 'NOUN'), ('رفته_بودم', 'VERB'), ('.', 'PUNCT')]]

        Args:
            sentences (List[List[str]]): لیستی از جملات که باید برچسب‌گذاری شود.

        Returns:
            (List[List[Tuple[str,str]]]): لیستی از لیستی از `(توکن، برچسب)`ها.
                    هر لیست از `(توکن،برچسب)`ها مربوط به یک جمله است.

        """
        assert self.model is not None, "you should load model first..."
        return [self.__tag(tokens) for tokens in sentences]

    def train(
        self,
        tagged_list,
        c1=0.4,
        c2=0.04,
        max_iteration=400,
        verbose=True,
        file_name="crf.model",
        report_duration=True,
    ):
        """لیستی از جملات را می‌گیرد و بر اساس آن مدل را آموزش می‌دهد.

        هر جمله، لیستی از `(توکن، برچسب)`هاست.

        Examples:
            >>> tagger = SequenceTagger()
            >>> tagger.train(tagged_list = [[('من', 'PRON'), ('به', 'ADP'), ('مدرسه', 'NOUN,EZ'), ('ایران', 'NOUN'), ('رفته_بودم', 'VERB'), ('.', 'PUNCT')]], c1 = 0.5, c2 = 0.5, max_iteration = 100, verbose = True, file_name = 'tagger.model', report_duration = True)
            Feature generation
            type: CRF1d
            feature.minfreq: 0.000000
            feature.possible_states: 0
            feature.possible_transitions: 1
            0....1....2....3....4....5....6....7....8....9....10
            Number of features: 150
            Seconds required: 0.001
            ...
            Writing feature references for attributes
            Seconds required: 0.000

            training time: 0.01 sec

        Args:
            tagged_list (List[{List[Tuple[str,str]]]): جملاتی که مدل از روی آن‌ها آموزش می‌بیند.
            c1 (float): مقدار L1 regularization.
            c2 (float): مقدار L2 regularization.
            max_iteration (int): تعداد تکرار آموزش بر کل دیتا.
            verbose (boolean): نمایش اطلاعات مربوط به آموزش.
            file_name (str): نام و مسیر فایلی که می‌خواهید مدل در آن ذخیره شود.
            report_duration (boolean): نمایش گزارشات مربوط به زمان.

        """
        X = self.data_maker(
            [[x for x, _ in tagged_sent] for tagged_sent in tagged_list],
        )
        y = [[y for _, y in tagged_sent] for tagged_sent in tagged_list]

        args = {
            "c1": c1,
            "c2": c2,
            "max_iterations": max_iteration,
            "feature.possible_transitions": True,
        }

        self.__train(X, y, args, verbose, file_name, report_duration)

    def save_model(self, filename):
        """مدل تهیه‌شده توسط تابع [train()][hazm.SequenceTagger.SequenceTagger.train]
        را ذخیره می‌کند.

        Examples:
            >>> tagger = SequenceTagger()
            >>> tagger.train(tagged_list = [[('من', 'PRON'), ('به', 'ADP'), ('مدرسه', 'NOUN,EZ'), ('ایران', 'NOUN'), ('رفته_بودم', 'VERB'), ('.', 'PUNCT')]], c1 = 0.5, c2 = 0.5, max_iteration = 100, verbose = True, file_name = 'tagger.model', report_duration = True)
            >>> tagger.save_model(file_name = 'new_tagger.model')

        Args:
            filename (str): نام و مسیر فایلی که می‌خواهید مدل در آن ذخیره شود.

        """
        assert self.model is not None, "you should load model first..."
        self.model.dump(filename)

    def evaluate(self, tagged_sent):
        """داده صحیح دریافت شده را با استفاده از مدل لیبل می‌زند و دقت مدل را برمی‌گرداند.

        Examples:
            >>> tagger = SequenceTagger(model = 'tagger.model')
            >>> tagger.evaluate([[('نامه', 'NOUN,EZ'), ('ایشان', 'PRON'), ('را', 'ADP'), ('دریافت', 'NOUN'), ('داشتم', 'VERB'), ('.', 'PUNCT')]])
            1.0
        Args:
            tagged_sent (List[List[Tuple[str,str]]]): جملات لیبل‌داری که با استفاده از آن مدل را ارزیابی می‌کنیم.

        Returns:
            (Float): دقت مدل

        """
        assert self.model != None, "you should load model first..."
        extract_labels = lambda tagged_list: [
            [label for _, label in sent] for sent in tagged_list
        ]
        tokens = [[word for word, _ in sent] for sent in tagged_sent]
        predicted_tagged_sent = self.tag_sents(tokens)
        return self.__evaluate(
            extract_labels(tagged_sent), extract_labels(predicted_tagged_sent)
        )


class IOBTagger(SequenceTagger):
    """ """

    def __init__(self, model=None, data_maker=iob_data_maker) -> None:
        super().__init__(model, data_maker)

    def __IOB_format(self, tagged_data, chunk_tags):
        return [
            (token[0], token[1], chunk_tag[1])
            for token, chunk_tag in zip(tagged_data, chunk_tags)
        ]

    def tag(self, tagged_data):
        """یک جمله را در قالب لیستی از توکن‌ها و تگ‌ها دریافت می‌کند و در خروجی لیستی از
        `(توکن، تگ، برچسب)`ها برمی‌گرداند.

        Examples:
            >>> iobTagger = IOBTagger(model = 'tagger.model')
            >>> iobTagger.tag(tagged_data = [('من', 'PRON'), ('به', 'ADP'), ('مدرسه', 'NOUN,EZ'), ('ایران', 'NOUN'), ('رفته_بودم', 'VERB'), ('.', 'PUNCT')])
            [('من', 'PRON', 'B-NP'), ('به', 'ADP', 'B-PP'), ('مدرسه', 'NOUN,EZ', 'B-NP'), ('ایران', 'NOUN', 'I-NP'), ('رفته_بودم', 'VERB', 'B-VP'), ('.', 'PUNCT', 'O')]

        Args:
            tagged_data (List[Tuple[str, str]]): لیستی از توکن‌های یک جمله که باید برچسب‌گذاری شود.

        Returns:
            (List[Tuple[str, str, str]]): ‌لیستی از `(توکن، تگ، برچسب)`ها.

        """
        chunk_tags = super().tag(tagged_data)
        return self.__IOB_format(tagged_data, chunk_tags)

    def tag_sents(self, sentences):
        """جملات را در قالب لیستی لیستی از توکن‌ها و تگ‌ها دریافت می‌کند
        و در خروجی، لیستی از لیستی از `(توکن، تگ، برچسب)`ها برمی‌گرداند.

        هر لیست از `(توکن، برچسب)`ها مربوط به یک جمله است.

        Examples:
            >>> iobTagger = IOBTagger(model = 'tagger.model')
            >>> iobTagger.tag_sents(tagged_data = [[('من', 'PRON'), ('به', 'ADP'), ('مدرسه', 'NOUN,EZ'), ('ایران', 'NOUN'), ('رفته_بودم', 'VERB'), ('.', 'PUNCT')]])
            [[('من', 'PRON', 'B-NP'), ('به', 'ADP', 'B-PP'), ('مدرسه', 'NOUN,EZ', 'B-NP'), ('ایران', 'NOUN', 'I-NP'), ('رفته_بودم', 'VERB', 'B-VP'), ('.', 'PUNCT', 'O')]]

        Args:
            sentences (List[List[str]]): لیستی از جملات که باید برچسب‌گذاری شود.

        Returns:
            (List[List[Tuple[str,str]]]): لیستی از لیستی از `(توکن، تگ، برچسب)`ها.
                    هر لیست از `(توکن، تگ، برچسب)`ها مربوط به یک جمله است.

        """
        chunk_tags = super().tag_sents(sentences)
        return [
            self.__IOB_format(tagged_data, chunks)
            for tagged_data, chunks in zip(sentences, chunk_tags)
        ]

    def train(
        self,
        tagged_list,
        c1=0.4,
        c2=0.04,
        max_iteration=400,
        verbose=True,
        file_name="crf.model",
        report_duration=True,
    ):
        """لیستی از جملات را می‌گیرد و بر اساس آن مدل را آموزش می‌دهد.

        هر جمله، لیستی از `(توکن، تگ، برچسب)`هاست.

        Examples:
            >>> iobTagger = IOBTagger()
            >>> iobTagger.train(tagged_list = [[('من', 'PRON', 'B-NP'), ('به', 'ADP', 'B-PP'), ('مدرسه', 'NOUN,EZ', 'B-NP'), ('ایران', 'NOUN', 'I-NP'), ('رفته_بودم', 'VERB', 'B-VP'), ('.', 'PUNCT', 'O')]], c1 = 0.5, c2 = 0.5, max_iteration = 100, verbose = True, file_name = 'newIOBTagger.model', report_duration = True)
            Feature generation
            type: CRF1d
            feature.minfreq: 0.000000
            feature.possible_states: 0
            feature.possible_transitions: 1
            0....1....2....3....4....5....6....7....8....9....10
            Number of features: 150
            Seconds required: 0.001
            ...
            Writing feature references for attributes
            Seconds required: 0.000

            training time: 0.01 sec

        Args:
            tagged_list (List[List[Tuple[str, str, str]]]): جملاتی که مدل از روی آن‌ها آموزش می‌بیند.
            c1 (float): مقدار L1 regularization.
            c2 (float): مقدار L2 regularization.
            max_iteration (int): تعداد تکرار آموزش بر کل دیتا.
            verbose (boolean): نمایش اطلاعات مربوط به آموزش.
            file_name (str): نام و مسیر فایلی که می‌خواهید مدل در آن ذخیره شود.
            report_duraion (boolean): نمایش گزارشات مربوط به زمان.

        """
        tagged_list = [
            [((word, tag), chunk) for word, tag, chunk in tagged_sent]
            for tagged_sent in tagged_list
        ]
        return super().train(
            tagged_list,
            c1,
            c2,
            max_iteration,
            verbose,
            file_name,
            report_duration,
        )

    def evaluate(self, tagged_sent):
        """داده صحیح دریافت شده را با استفاده از مدل لیبل می‌زند و دقت مدل را برمی‌گرداند.

        Examples:
            >>> iobTagger = IOBTagger(model = 'tagger.model')
            >>> iobTagger.evaluate([[('نامه', 'NOUN,EZ', 'B-NP'), ('ایشان', 'PRON', 'I-NP'), ('را', 'ADP', 'B-POSTP'), ('دریافت', 'NOUN', 'B-VP'), ('داشتم', 'VERB', 'I-VP'), ('.', 'PUNCT', 'O')]])
            1.0
        Args:
            tagged_sent (List[List[Tuple[str, str, str]]]): جملات لیبل‌داری که با استفاده از آن مدل را ارزیابی می‌کنیم.

        Returns:
            (Float): دقت مدل

        """
        assert self.model != None, "you should load model first..."
        extract_labels = lambda tagged_list: [
            [token[-1] for token in sent] for sent in tagged_list
        ]
        tokens = [[token[:-1] for token in sent] for sent in tagged_sent]
        predicted_tagged_sent = self.tag_sents(tokens)
        return super()._SequenceTagger__evaluate(
            extract_labels(tagged_sent), extract_labels(predicted_tagged_sent)
        )



punctuation_list = [
    '"',
    "#",
    "(",
    ")",
    "*",
    ",",
    "-",
    ".",
    "/",
    ":",
    "[",
    "]",
    "«",
    "»",
    "،",
    ";",
    "?",
    "!",
]


class POSTagger(SequenceTagger):
    """این کلاس‌ها شامل توابعی برای برچسب‌گذاری توکن‌هاست. **میزان دقت برچسب‌زنی در
    نسخهٔ حاضر ۹۷.۲ درصد [^1] است.** این کلاس تمام توابع خود را از کلاس
    [SequenceTagger][hazm.SequenceTagger.SequenceTagger] به ارث می‌برد.
    [^1]:
    این عدد با انتشار هر نسخه بروزرسانی می‌شود.

    """

    def __init__(self, model=None, data_maker=None, universal_tag=False) -> None:
        data_maker = self.data_maker if data_maker is None else data_maker
        self.__is_universal = universal_tag
        super().__init__(model, data_maker)

    def __universal_converter(self, tagged_list):
        return [(word, tag.split(",")[0]) for word, tag in tagged_list]

    def __is_punc(self, word):
        return word in punctuation_list

    def data_maker(self, tokens):
        """تابعی که لیستی از لیستی از کلمات توکنایز شده را گرفته و لیست دو بعدی از از دیکشنری‌هایی که تعیین‌کننده ویژگی‌ها هر کلمه هستند را برمی‌گرداند.

        Examples:
            >>> posTagger = POSTagger(model = 'resources/POSTagger.model')
            >>> posTagger.data_maker(tokens = [['دلم', 'اینجا', 'مانده‌است', '.']])
            [[{'word': 'دلم', 'is_first': True, 'is_last': False, 'prefix-1': 'د', 'prefix-2': 'دل', 'prefix-3': 'دلم', 'suffix-1': 'م', 'suffix-2': 'لم', 'suffix-3': 'دلم', 'prev_word': '', 'two_prev_word': '', 'next_word': 'اینجا', 'two_next_word': 'مانده\u200cاست', 'is_numeric': False, 'prev_is_numeric': '', 'next_is_numeric': False, 'is_punc': False, 'prev_is_punc': '', 'next_is_punc': False}, {'word': 'اینجا', 'is_first': False, 'is_last': False, 'prefix-1': 'ا', 'prefix-2': 'ای', 'prefix-3': 'این', 'suffix-1': 'ا', 'suffix-2': 'جا', 'suffix-3': 'نجا', 'prev_word': 'دلم', 'two_prev_word': '.', 'next_word': 'مانده\u200cاست', 'two_next_word': '.', 'is_numeric': False, 'prev_is_numeric': False, 'next_is_numeric': False, 'is_punc': False, 'prev_is_punc': False, 'next_is_punc': False}, {'word': 'مانده\u200cاست', 'is_first': False, 'is_last': False, 'prefix-1': 'م', 'prefix-2': 'ما', 'prefix-3': 'مان', 'suffix-1': 'ت', 'suffix-2': 'ست', 'suffix-3': 'است', 'prev_word': 'اینجا', 'two_prev_word': 'دلم', 'next_word': '.', 'two_next_word': '', 'is_numeric': False, 'prev_is_numeric': False, 'next_is_numeric': False, 'is_punc': False, 'prev_is_punc': False, 'next_is_punc': True}, {'word': '.', 'is_first': False, 'is_last': True, 'prefix-1': '.', 'prefix-2': '.', 'prefix-3': '.', 'suffix-1': '.', 'suffix-2': '.', 'suffix-3': '.', 'prev_word': 'مانده\u200cاست', 'two_prev_word': 'اینجا', 'next_word': '', 'two_next_word': '', 'is_numeric': False, 'prev_is_numeric': False, 'next_is_numeric': '', 'is_punc': True, 'prev_is_punc': False, 'next_is_punc': ''}]]

        Args:
            tokens (List[List[str]]): جملاتی که نیاز به تبدیل آن به برداری از ویژگی‌ها است.

        Returns:
            List(List(Dict())): لیستی از لیستی از دیکشنری‌های بیان‌کننده ویژگی‌های یک کلمه.
        """
        return [
            [self.features(token, index) for index in range(len(token))]
            for token in tokens
        ]

    def features(self, sentence, index):
        return {
            "word": sentence[index],
            "is_first": index == 0,
            "is_last": index == len(sentence) - 1,
            # *ix
            "prefix-1": sentence[index][0],
            "prefix-2": sentence[index][:2],
            "prefix-3": sentence[index][:3],
            "suffix-1": sentence[index][-1],
            "suffix-2": sentence[index][-2:],
            "suffix-3": sentence[index][-3:],
            # word
            "prev_word": "" if index == 0 else sentence[index - 1],
            "two_prev_word": "" if index == 0 else sentence[index - 2],
            "next_word": "" if index == len(sentence) - 1 else sentence[index + 1],
            "two_next_word": (
                ""
                if (index == len(sentence) - 1 or index == len(sentence) - 2)
                else sentence[index + 2]
            ),
            # digit
            "is_numeric": sentence[index].isdigit(),
            "prev_is_numeric": "" if index == 0 else sentence[index - 1].isdigit(),
            "next_is_numeric": (
                "" if index == len(sentence) - 1 else sentence[index + 1].isdigit()
            ),
            # punc
            "is_punc": self.__is_punc(sentence[index]),
            "prev_is_punc": "" if index == 0 else self.__is_punc(sentence[index - 1]),
            "next_is_punc": (
                ""
                if index == len(sentence) - 1
                else self.__is_punc(sentence[index + 1])
            ),
        }

    def tag(self, tokens):
        """یک جمله را در قالب لیستی از توکن‌ها دریافت می‌کند و در خروجی لیستی از
        `(توکن، برچسب)`ها برمی‌گرداند.

        Examples:
            >>> posTagger = POSTagger(model = 'resources/POSTagger.model')
            >>> posTagger.tag(tokens = ['من', 'به', 'مدرسه', 'ایران', 'رفته_بودم', '.'])
            [('من', 'PRON'), ('به', 'ADP'), ('مدرسه', 'NOUN,EZ'), ('ایران', 'NOUN'), ('رفته_بودم', 'VERB'), ('.', 'PUNCT')]

            >>> posTagger = POSTagger(model = 'resources/POSTagger.model', universal_tag = True)
            >>> posTagger.tag(tokens = ['من', 'به', 'مدرسه', 'ایران', 'رفته_بودم', '.'])
            [('من', 'PRON'), ('به', 'ADP'), ('مدرسه', 'NOUN'), ('ایران', 'NOUN'), ('رفته_بودم', 'VERB'), ('.', 'PUNCT')]

        Args:
            tokens (List[str]): لیستی از توکن‌های یک جمله که باید برچسب‌گذاری شود.

        Returns:
            (List[Tuple[str,str]]): ‌لیستی از `(توکن، برچسب)`ها.

        """
        tagged_token = super().tag(tokens)
        return (
            self.__universal_converter(tagged_token)
            if self.__is_universal
            else tagged_token
        )

    def tag_sents(self, sentences):
        """جملات را در قالب لیستی از توکن‌ها دریافت می‌کند
        و در خروجی، لیستی از لیستی از `(توکن، برچسب)`ها برمی‌گرداند.

        هر لیست از `(توکن، برچسب)`ها مربوط به یک جمله است.

        Examples:
            >>> posTagger = POSTagger(model = 'resources/POSTagger.model')
            >>> posTagger.tag_sents(sentences = [['من', 'به', 'مدرسه', 'ایران', 'رفته_بودم', '.']])
            [[('من', 'PRON'), ('به', 'ADP'), ('مدرسه', 'NOUN,EZ'), ('ایران', 'NOUN'), ('رفته_بودم', 'VERB'), ('.', 'PUNCT')]]

            >>> posTagger = POSTagger(model = 'resources/POSTagger.model', universal_tag = True)
            >>> posTagger.tag_sents(sentences = [['من', 'به', 'مدرسه', 'ایران', 'رفته_بودم', '.']])
            [[('من', 'PRON'), ('به', 'ADP'), ('مدرسه', 'NOUN'), ('ایران', 'NOUN'), ('رفته_بودم', 'VERB'), ('.', 'PUNCT')]]

        Args:
            sentences (List[List[str]]): لیستی از جملات که باید برچسب‌گذاری شود.

        Returns:
            (List[List[Tuple[str,str]]]): لیستی از لیستی از `(توکن، برچسب)`ها.
                    هر لیست از `(توکن،برچسب)`ها مربوط به یک جمله است.

        """
        tagged_sents = super().tag_sents(sentences)
        return (
            [self.__universal_converter(tagged_sent) for tagged_sent in tagged_sents]
            if self.__is_universal
            else tagged_sents
        )

