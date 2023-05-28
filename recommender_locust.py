from locust import HttpUser, between, task
import numpy as np

big_sample_text = 'سفارت ایران در مادرید درباره فیلم منتشرشده از «حسن قشقاوی» در مراسم سال نو در کاخ سلطنتی اسپانیا و حاشیه‌سازی‌ها در فضای مجازی اعلام کرد: به تشریفات دربار کتباً اعلام شد سفیر بدون همراه در مراسم حضور خواهد داشت و همچون قبل به دلایل تشریفاتی نمی‌تواند با ملکه دست بدهد. همان‌گونه که کارشناس رسمی تشریفات در توضیحات خود به یک نشریه اسپانیایی گفت این موضوع توضیح مذهبی داشته و هرگز به معنی بی‌احترامی به مقام و شخصیت زن آن هم در سطح ملکه محترمه یک کشور نیست.'
small_sample_text = 'در جنگل ایران گونه‌های جانوری زیادی وجود دارد.'
small_sample_text1 = 'آمازون شامل ببرهای وحشی زیادی است.'

sample_summary_list = [big_sample_text, small_sample_text, small_sample_text1]

class Recommender_user(HttpUser):
    wait_time = between(9,10)

    @task
    def insert_book(self):
        data = {
            "id": np.random.randint(999999999999),
            "summary": sample_summary_list[np.random.randint(0,3)]
        }
        self.client.post('/insert_book', data=data)

    @task
    def ask_book(self):
        data = {
            "id": 5
        }
        self.client.post('/ask_book', data=data)

