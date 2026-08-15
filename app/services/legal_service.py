from app.models.legal_document import LegalDocument


def get_active_legal_documents():
    """
    Return currently active legal documents.

    Only active documents are exposed to normal users.
    """
    return (
        LegalDocument.query
        .filter_by(is_active=True)
        .order_by(
            LegalDocument.document_type.asc(),
            LegalDocument.version.desc()
        )
        .all()
    )


def get_active_legal_document(document_type):
    """
    Return the currently active version of a legal document type.
    """
    return (
        LegalDocument.query
        .filter_by(
            document_type=document_type,
            is_active=True
        )
        .order_by(
            LegalDocument.version.desc()
        )
        .first()
    )


def get_legal_document(document_id):
    """
    Return a legal document by ID.
    """
    return (
        LegalDocument.query
        .filter_by(id=document_id)
        .first()
    )


def get_legal_document_by_version(
    document_type,
    version
):
    """
    Return an exact legal document version.
    """
    return (
        LegalDocument.query
        .filter_by(
            document_type=document_type,
            version=version
        )
        .first()
    )
