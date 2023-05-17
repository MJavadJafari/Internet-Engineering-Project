from rest_framework import serializers
from Book.models import Book, BookRequest


class BookSerializer(serializers.ModelSerializer):

    class Meta:
        model = Book
        exclude = ('created_at', 'ranking')
        read_only_fields = ['is_donated', 'is_received', 'donator', 'book_id', 'number_of_request']

    def create(self, validated_data):
        book = Book.objects.create(**validated_data, donator=self.context['request'].user)
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
        book = validated_data['book']
        if book.is_donated:
            raise serializers.ValidationError({'detail': 'Book is already donated'})

        prev_req = BookRequest.objects.filter(**validated_data, user=self.context['request'].user)
        if prev_req.exists():
            return prev_req[0]

        if user.rooyesh == 0:
            raise serializers.ValidationError({'detail': 'Not enough rooyesh'})

        request = BookRequest.objects.create(**validated_data, user=self.context['request'].user)
        user.change_rooyesh(-1)

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
