from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models import Q
from apps.docs.models import Document, DocumentPermission
from apps.docs.utils import query_documents, delete_documents_with_prefix
from .serializers import (
    DocumentSerializer, 
    DocumentUploadSerializer,
    UserSerializer,
    DocumentPermissionSerializer,
    GrantPermissionSerializer,
    QueryResponseSerializer
)
from openai import OpenAI
from django.conf import settings

User = get_user_model()

# Create your views here.

class DocumentQueryView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        query = request.data.get('q', '')
        if not query:
            return Response(
                {"detail": "'q' is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get document IDs to search within, if provided
        document_ids = request.data.get('document_ids', None)
        if document_ids:
            try:
                document_ids = [int(doc_id) for doc_id in document_ids]
            except ValueError:
                return Response(
                    {"detail": "Invalid document ID format"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        if not request.user.is_staff:
            # Get accessible documents for the user
            accessible_doc_records = DocumentPermission.objects.filter(user=request.user)
            doc_ids = [r.document_id for r in accessible_doc_records]
            accessible_docs = Document.objects.filter(
                id__in=doc_ids
            )
        else:
            accessible_docs = Document.objects.all()

        # If specific documents are requested, filter them by accessibility
        if document_ids:
            accessible_docs = accessible_docs.filter(id__in=document_ids)
            if not accessible_docs.exists():
                return Response(
                    {"detail": "No accessible documents found with the provided IDs"},
                    status=status.HTTP_404_NOT_FOUND
                )
            document_ids = list(accessible_docs.values_list('id', flat=True))

        # Get relevant chunks
        results = query_documents(
            query, 
            document_ids=document_ids if document_ids else None
        )
        
        # Filter results to only include documents the user has access to
        # (This is a safeguard, though the document_ids filter should handle this)
        accessible_doc_ids = set(accessible_docs.values_list('id', flat=True))
        filtered_results = [
            result for result in results 
            if result['document'].id in accessible_doc_ids
        ]
        
        serializer = QueryResponseSerializer(filtered_results, many=True)
        return Response(serializer.data)

class DocumentListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_staff:
            user_documents = DocumentPermission.objects.filter(user=request.user).values_list('document_id', flat=True)
            documents = Document.objects.filter(id__in=user_documents)
        else:
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
        if document.is_processed:
            n = delete_documents_with_prefix(f"{document.id}_")
        document.delete()
        return Response({"deleted": n}, status=status.HTTP_204_NO_CONTENT)

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

class UserSearchView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        query = request.query_params.get('q', None)
        users = User.objects.all()
        if query:
            users = users.filter(
                Q(username__icontains=query) |
                Q(email__icontains=query) |
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query)
            )
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

class DocumentPermissionView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, document_id):
        permissions = DocumentPermission.objects.filter(document_id=document_id)
        serializer = DocumentPermissionSerializer(permissions, many=True)
        return Response(serializer.data)

    def post(self, request, document_id):
        serializer = GrantPermissionSerializer(data={
            'user_id': request.data.get('user_id'),
            'document_id': document_id
        })
        if serializer.is_valid():
            user = serializer.validated_data['user']
            document = serializer.validated_data['document']
            
            # Create permission
            permission = DocumentPermission.objects.create(
                document=document,
                user=user,
                granted_by=request.user
            )
            
            return Response(
                DocumentPermissionSerializer(permission).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, document_id):
        user_id = request.data.get('user_id')
        if not user_id:
            return Response(
                {"detail": "user_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        permission = get_object_or_404(
            DocumentPermission,
            document_id=document_id,
            user_id=user_id
        )
        permission.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class DocumentQueryWithResponseView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        query = request.data.get('q', '')
        if not query:
            return Response(
                {"detail": "'q' is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get document IDs to search within, if provided
        document_ids = request.data.get('document_ids', None)
        if document_ids:
            try:
                document_ids = [int(doc_id) for doc_id in document_ids]
            except ValueError:
                return Response(
                    {"detail": "Invalid document ID format"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        if not request.user.is_staff:
            # Get accessible documents for the user
            accessible_doc_records = DocumentPermission.objects.filter(user=request.user)
            doc_ids = [r.document_id for r in accessible_doc_records]
            accessible_docs = Document.objects.filter(id__in=doc_ids)
        else:
            accessible_docs = Document.objects.all()

        # If specific document IDs were provided, filter to only those that are accessible
        if document_ids:
            accessible_docs = accessible_docs.filter(id__in=document_ids)

        # Get relevant text chunks from ChromaDB
        relevant_chunks = query_documents(
            query_text=query,
            n_results=5,
            document_ids=[doc.id for doc in accessible_docs]
        )

        if not relevant_chunks:
            return Response(
                {"detail": "No relevant documents found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Prepare context for OpenAI
        context = "\n\n".join([chunk['text'] for chunk in relevant_chunks])
        
        # Create OpenAI client
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Generate response using OpenAI
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that answers questions based on the provided context. If the answer cannot be found in the context, say so."},
                    {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            return Response({
                "response": response.choices[0].message.content,
                "sources": [{
                    "document_id": chunk['document'].id,
                    "document_name": chunk['document'].original_name,
                    "text": chunk['text'],
                    "similarity": chunk['distance']
                } for chunk in relevant_chunks]
            })
            
        except Exception as e:
            return Response(
                {"detail": f"Error generating response: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
