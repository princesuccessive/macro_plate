from rest_framework import serializers


class CreateTaskSerializer(serializers.Serializer):
    """Data serializer to run celery task."""
    name = serializers.CharField()
    payload = serializers.JSONField(required=False)
    file = serializers.FileField(required=False)
