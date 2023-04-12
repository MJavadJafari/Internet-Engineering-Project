from rest_framework import serializers
from Book.models import Book, BookRequest


class BookSerializer(serializers.ModelSerializer):

    class Meta:
        model = Book
        exclude = ('created_at', 'ranking')
        read_only_fields = ['is_donated', 'is_received', 'donator', 'book_id', 'number_of_request']

    def create(self, validated_data):
        book = Book.objects.create(**validated_data, donator=self.context['request'].user)
        # try:
        #     from Recommender.Recommender import SingletonRecommender
        #     rec = SingletonRecommender()
        #     rec.insert_book(book.book_id, book.description)
        # except Exception as e:
        #     print(e)
        # TODO: add book to recommender
        return book


class AllBooksSerializer(serializers.ModelSerializer):

    class Meta:
        model = Book
        exclude = ('created_at', 'ranking')
        read_only_fields = ['is_donated', 'is_received', 'donator', 'book_id', 'number_of_request']

    def to_representation(self, instance):
        assert isinstance(instance, Book)
        result = super().to_representation(instance)
        result['is_requested_before'] = BookRequest.objects.filter(book=instance, user=self.context['request'].user).exists()
        return result


class BookRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookRequest
        exclude = ('created_at', 'id')
        read_only_fields = ['status', 'created_at', 'id']

    def create(self, validated_data):
        user = self.context['request'].user
        prev_req = BookRequest.objects.filter(**validated_data, user=self.context['request'].user)
        print(prev_req)
        if prev_req.exists():
            return prev_req[0]

        if user.rooyesh == 0:
            raise serializers.ValidationError('Not enough rooyesh')

        request = BookRequest.objects.create(**validated_data, user=self.context['request'].user)
        user.change_rooyesh(-1)

        print(user.rooyesh)
        return request


class MyRequestsSerializer(serializers.ModelSerializer):
    book = BookSerializer()

    class Meta:
        model = BookRequest
        exclude = ('created_at', 'id')
        read_only_fields = ['status', 'created_at', 'id']

    def to_representation(self, instance):
        result = super().to_representation(instance)
        if isinstance(instance, BookRequest) and instance.status == BookRequest.APPROVED:
            result['phone_number'] = instance.book.donator.phone_number
        return result
