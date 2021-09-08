from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView

from .serializers import RetrieveReqFileSerializer


class SearchFileView(CreateAPIView):
    serializer_class = RetrieveReqFileSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = self.perform_create(serializer)
        if obj is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK, headers=headers)

    def perform_create(self, serializer):
        return serializer.save()

