from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from apps.docs.models import Document
from .serializers import DocumentSerializer, DocumentUploadSerializer

# Create your views here.

class DocumentListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        documents = Document.objects.all()
        serializer = DocumentSerializer(documents, many=True, context={"request": request})
        return Response(serializer.data)

class DocumentDetailView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, pk):
        document = get_object_or_404(Document, pk=pk)
        serializer = DocumentSerializer(document, context={"request": request})
        return Response(serializer.data)

    def delete(self, request, pk):
        document = get_object_or_404(Document, pk=pk)
        document.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class DocumentDownloadView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        document = get_object_or_404(Document, pk=pk)
        return FileResponse(document.file, as_attachment=True, filename=document.original_name)

class DocumentUploadView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = DocumentUploadSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
