from rest_framework import serializers
from apps.docs.models import Document

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