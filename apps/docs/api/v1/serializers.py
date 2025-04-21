from rest_framework import serializers
from apps.docs.models import Document, DocumentPermission
from django.contrib.auth import get_user_model

User = get_user_model()

class QueryResponseSerializer(serializers.Serializer):
    text = serializers.CharField()
    document = serializers.SerializerMethodField()
    distance = serializers.FloatField()

    def get_document(self, obj):
        return {
            'id': obj['document'].id,
            'original_name': obj['document'].original_name,
            'upload_date': obj['document'].upload_date
        }

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class DocumentPermissionSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    granted_by = UserSerializer(read_only=True)

    class Meta:
        model = DocumentPermission
        fields = ['id', 'user', 'granted_at', 'granted_by', 'document']
        read_only_fields = ['granted_at', 'granted_by']

class GrantPermissionSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    document_id = serializers.IntegerField()

    def validate(self, attrs):
        try:
            user = User.objects.get(id=attrs['user_id'])
            document = Document.objects.get(id=attrs['document_id'])
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found")
        except Document.DoesNotExist:
            raise serializers.ValidationError("Document not found")
        
        attrs['user'] = user
        attrs['document'] = document
        return attrs

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'original_name', 'upload_date', 'is_processed', 'user', 'doc_type', 'file', 'extracted']
        read_only_fields = ['upload_date', 'user']

class DocumentUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['file'] 
    
    def validate(self, attrs):
        data = super().validate(attrs)
        original_name = data['file'].name
        try:
            doc_type = data['file'].name.split('.')[-1]
        except:
            raise serializers.ValidationError('Unknown file type')
        if doc_type.lower() not in ['pdf', 'docx', 'txt']:
            raise serializers.ValidationError("file", "Supported file types are pdf, docx and txt.")
        data['original_name'] = original_name
        data['doc_type'] = doc_type.lower()
        return data