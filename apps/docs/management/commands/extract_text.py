from django.core.management.base import BaseCommand
from apps.docs.models import Document
import os
from django.conf import settings
from datetime import datetime
import PyPDF2
import docx
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Extract text from unprocessed documents and save as text files'

    def handle(self, *args, **options):
        # Get all unprocessed documents
        documents = Document.objects.filter(extracted=False)
        
        for document in documents:
            try:
                # Create text file path
                text_file_path = os.path.join(
                    "texts",
                    f'{document.id}.txt'
                )
                
                # Extract text based on document type
                text = ''
                if document.doc_type.lower() == 'pdf':
                    text = self.extract_text_from_pdf(document.file.path)
                elif document.doc_type.lower() == 'docx':
                    text = self.extract_text_from_docx(document.file.path)
                elif document.doc_type.lower() == 'txt':
                    text = self.extract_text_from_txt(document.file.path)
                else:
                    logger.warning(f"Unsupported file type: {document.doc_type} for document {document.id}")
                    continue

                # Save text to file
                full_path = os.path.join(settings.MEDIA_ROOT, text_file_path)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(text)

                # Update document
                document.txt_file = text_file_path
                document.extracted = True
                document.save()

                self.stdout.write(self.style.SUCCESS(f'Successfully extracted text from document {document.id}'))

            except Exception as e:
                logger.error(f"Error processing document {document.id}: {str(e)}")
                self.stdout.write(self.style.ERROR(f'Error processing document {document.id}: {str(e)}'))

    def extract_text_from_pdf(self, file_path):
        text = ''
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + '\n'
        return text

    def extract_text_from_docx(self, file_path):
        doc = docx.Document(file_path)
        return '\n'.join([paragraph.text for paragraph in doc.paragraphs])

    def extract_text_from_txt(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read() 