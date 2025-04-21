from django.core.management.base import BaseCommand
from apps.docs.models import Document
from apps.docs.utils import collection, chunk_text
import os
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Store unprocessed documents in Chroma DB'

    def handle(self, *args, **options):
        # Get all unprocessed documents
        documents = Document.objects.filter(is_processed=False, extracted=True)
        
        for document in documents:
            try:
                # Read the text file
                if not document.txt_file:
                    logger.warning(f"Document {document.id} has no text file")
                    continue

                text_file_path = os.path.join(settings.MEDIA_ROOT, document.txt_file.name)
                with open(text_file_path, 'r', encoding='utf-8') as f:
                    text = f.read()

                # Split text into chunks
                chunks = chunk_text(text)
                
                # Prepare data for Chroma
                ids = [f"{document.id}_{i}" for i in range(len(chunks))]
                metadatas = [{"document_id": str(document.id)} for _ in chunks]
                
                # Add to Chroma
                collection.add(
                    documents=chunks,
                    ids=ids,
                    metadatas=metadatas
                )

                # Update document status
                document.is_processed = True
                document.save()

                self.stdout.write(self.style.SUCCESS(f'Successfully stored document {document.id} in Chroma DB'))

            except Exception as e:
                logger.error(f"Error processing document {document.id}: {str(e)}")
                self.stdout.write(self.style.ERROR(f'Error processing document {document.id}: {str(e)}')) 