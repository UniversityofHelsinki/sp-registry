from rest_framework import serializers


class ActiveListSerializer(serializers.ListSerializer):
    def to_representation(self, data):
        data = data.filter(end_at=None)
        return super(ActiveListSerializer, self).to_representation(data)
