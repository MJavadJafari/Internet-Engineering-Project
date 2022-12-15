from rest_framework import serializers
from django.contrib.auth import get_user_model

from Book.models import Book


class BookSerializer(serializers.ModelSerializer):

    class Meta:
        model = Book
        fields = '__all__'

    def create(self, validated_data):
        tour = Book.objects.create(**validated_data, donator=self.context['request'].user)
        return tour
