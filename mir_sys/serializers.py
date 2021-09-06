from rest_framework import serializers
import numpy as np
import librosa

from mir_sys.retriever.retriever import Retriever

MAX_DURATION_SEC = 15
MIN_DURATION_SEC = 5


class RetrieveReqFileSerializer(serializers.Serializer):
    file_query = serializers.FileField(required=True)

    def validate_file_query(self, value):
        if value.content_type != "audio/wav":
            raise serializers.ValidationError("invalid type")
        return value

    def save(self, **kwargs):
        Retriever().retrieve("")


class RetrieveReqSampleSerializer(serializers.Serializer):
    MAX_DURATION_SAMPLES = librosa.time_to_samples(MAX_DURATION_SEC, sr=16000)
    MIN_DURATION_SAMPLES = librosa.time_to_samples(MIN_DURATION_SEC, sr=16000)
    samples = serializers.ListField(child=serializers.FloatField, required=True)

    def validate_samples(self, value):
        if len(value) > self.MAX_DURATION_SAMPLES:
            raise serializers.ValidationError("size of file is greater than valid size")
        elif len(value) < self.MIN_DURATION_SAMPLES:
            raise serializers.ValidationError("size of file is lower than valid size")
        return np.array(value)

    def save(self, **kwargs):
        self.result = Retriever().retrieve(self.validated_data['samples'])
        return self.result

    def to_representation(self, instance):
        pass


class RetrieveResponseSerializer(serializers.Serializer):
    title = serializers.CharField()