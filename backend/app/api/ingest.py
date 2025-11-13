"""
Document ingestion API endpoints
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel, HttpUrl
from typing import Optional
from loguru import logger
import tempfile
import os

from app.services.document_service import DocumentService

router = APIRouter()
document_service = DocumentService()


class URLIngestRequest(BaseModel):
    """URL ingestion request"""
    document_id: int
    source: HttpUrl


class PDFIngestRequest(BaseModel):
    """PDF ingestion request"""
    document_id: int
    source: Optional[str] = None
    file_content: Optional[str] = None
    filename: Optional[str] = None


class IngestResponse(BaseModel):
    """Ingestion response"""
    success: bool
    chunks: Optional[int] = None
    error: Optional[str] = None


@router.post("/ingest/url", response_model=IngestResponse)
async def ingest_url(request: URLIngestRequest):
    """
    Ingest content from a URL

    Args:
        request: URL ingestion request

    Returns:
        Ingestion result
    """
    try:
        logger.info(f"Ingesting URL for document {request.document_id}: {request.source}")

        result = await document_service.ingest_url(
            document_id=request.document_id,
            url=str(request.source)
        )

        if result['success']:
            return IngestResponse(
                success=True,
                chunks=result['chunks']
            )
        else:
            raise HTTPException(status_code=400, detail=result.get('error', 'Ingestion failed'))

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"URL ingestion error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ingest/pdf", response_model=IngestResponse)
async def ingest_pdf(request: PDFIngestRequest):
    """
    Ingest a PDF document

    Args:
        request: PDF ingestion request

    Returns:
        Ingestion result
    """
    try:
        logger.info(f"Ingesting PDF for document {request.document_id}")

        result = await document_service.ingest_pdf(
            document_id=request.document_id,
            file_path=request.source,
            file_content=request.file_content,
            filename=request.filename
        )

        if result['success']:
            return IngestResponse(
                success=True,
                chunks=result['chunks']
            )
        else:
            raise HTTPException(status_code=400, detail=result.get('error', 'Ingestion failed'))

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"PDF ingestion error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ingest/pdf/upload")
async def upload_and_ingest_pdf(
    document_id: int = Form(...),
    file: UploadFile = File(...)
):
    """
    Upload and ingest a PDF file

    Args:
        document_id: Moodle document ID
        file: Uploaded PDF file

    Returns:
        Ingestion result
    """
    try:
        logger.info(f"Uploading and ingesting PDF for document {document_id}: {file.filename}")

        # Validate file type
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="File must be a PDF")

        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name

        try:
            # Ingest the PDF
            result = await document_service.ingest_pdf(
                document_id=document_id,
                file_path=tmp_path,
                filename=file.filename
            )

            if result['success']:
                return IngestResponse(
                    success=True,
                    chunks=result['chunks']
                )
            else:
                raise HTTPException(status_code=400, detail=result.get('error', 'Ingestion failed'))

        finally:
            # Clean up temporary file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"PDF upload error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/documents/{document_id}")
async def delete_document(document_id: int):
    """
    Delete a document from the vector store

    Args:
        document_id: Moodle document ID

    Returns:
        Deletion result
    """
    try:
        logger.info(f"Deleting document {document_id}")

        success = await document_service.delete_document(document_id)

        if success:
            return {"success": True, "message": "Document deleted"}
        else:
            raise HTTPException(status_code=404, detail="Document not found")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
