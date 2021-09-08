from rest_framework import serializers
from ytmusicapi import YTMusic
import numpy as np
import librosa

from mir_sys.retriever.retriever import Retriever

MAX_DURATION_SEC = 15
MIN_DURATION_SEC = 5
YT = YTMusic()
RETRIEVER = Retriever()


class RetrieveReqFileSerializer(serializers.Serializer):
    MAX_DURATION_SAMPLES = librosa.time_to_samples(MAX_DURATION_SEC, sr=16000)
    MIN_DURATION_SAMPLES = librosa.time_to_samples(MIN_DURATION_SEC, sr=16000)
    file_query = serializers.FileField(required=True)

    def validate_file_query(self, value):
        # if value.content_type != "audio/wav":
        #     raise serializers.ValidationError("invalid type")
        try:
            samples, sr = librosa.load("newSong.wav", sr=16000)
        except :
            raise serializers.ValidationError("content of file is not valid")
        print(samples.shape)
        if len(samples) > self.MAX_DURATION_SAMPLES:
            raise serializers.ValidationError("size of file is greater than valid size")
        elif len(samples) < self.MIN_DURATION_SAMPLES:
            raise serializers.ValidationError("size of file is lower than valid size")
        return samples

    def save(self, **kwargs):
        result = RETRIEVER.retrieve(self.validated_data['file_query'])
        if result is not None:
            for i in range(5):
                try:
                    self.instance = YT.get_song("7c_VcZzS6LE").get('videoDetails', None)
                    return self.instance
                except Exception as e:
                    print(str(e))
                    pass
        return None

    def to_representation(self, instance):
        if instance:
            obj = {
                "author": instance['author'],
                "averageRating": instance['averageRating'],
                "title": instance['title'],
                "viewCount": instance['viewCount'],
                "thumbnail": instance['thumbnail']['thumbnails'][1]['url']
            }
            return RetrieveResponseSerializer(instance=obj).data
        return {}


class RetrieveReqSampleSerializer(serializers.Serializer):
    MAX_DURATION_SAMPLES = librosa.time_to_samples(MAX_DURATION_SEC, sr=16000)
    MIN_DURATION_SAMPLES = librosa.time_to_samples(MIN_DURATION_SEC, sr=16000)
    samples = serializers.ListField(child=serializers.FloatField(), required=True)

    def validate_samples(self, value):
        if len(value) > self.MAX_DURATION_SAMPLES:
            raise serializers.ValidationError("size of file is greater than valid size")
        elif len(value) < self.MIN_DURATION_SAMPLES:
            raise serializers.ValidationError("size of file is lower than valid size")
        return np.array(value)

    def save(self, **kwargs):
        pass
        # self.result = Retriever().retrieve(self.validated_data['samples'])
        # return self.result

    def to_representation(self, instance):
        pass


class RetrieveResponseSerializer(serializers.Serializer):
    title = serializers.CharField()
    author = serializers.CharField()
    averageRating = serializers.FloatField()
    viewCount = serializers.CharField()
    thumbnail = serializers.URLField()