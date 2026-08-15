from datetime import datetime

from app import create_app
from app.database import db
from app.models.legal_document import LegalDocument


DOCUMENTS = [
    {
        "document_type": "terms",
        "title": "Terms & Conditions",
        "version": "1.0",
        "content": """
DEVELOPMENT DRAFT — NOT FINAL LEGAL TERMS

This document is a development placeholder for the Ateliier_fhm
Terms & Conditions.

The final production Terms & Conditions must be reviewed and
approved before this document is used as a binding agreement.

This document establishes the versioned legal-document workflow
used by Ateliier_fhm. Each published version is stored separately
so that historical consent records can identify the exact version
accepted by a user.

Production content will be inserted after legal review.
""".strip(),
    },
    {
        "document_type": "privacy_policy",
        "title": "Privacy Policy",
        "version": "1.0",
        "content": """
DEVELOPMENT DRAFT — NOT FINAL PRIVACY POLICY

This document is a development placeholder for the Ateliier_fhm
Privacy Policy.

The final production Privacy Policy must accurately describe the
personal data collected by the application, the purposes for which
that data is processed, applicable retention practices, user
rights, security measures, disclosures, and other legally required
information.

Production content will be inserted after legal review.
""".strip(),
    },
    {
        "document_type": "cookie_policy",
        "title": "Cookie Policy",
        "version": "1.0",
        "content": """
DEVELOPMENT DRAFT — NOT FINAL COOKIE POLICY

This document is a development placeholder for the Ateliier_fhm
Cookie Policy.

The final production policy must accurately describe any cookies,
local-storage mechanisms, analytics technologies, authentication
mechanisms, personalization technologies, and other tracking
technologies actually used by the application.

Production content will be inserted after technical and legal
review.
""".strip(),
    },
    {
        "document_type": "acceptable_use",
        "title": "Acceptable Use Policy",
        "version": "1.0",
        "content": """
DEVELOPMENT DRAFT — NOT FINAL ACCEPTABLE USE POLICY

This document is a development placeholder for the Ateliier_fhm
Acceptable Use Policy.

The final production policy must define prohibited uses,
unauthorized activity, misuse of the platform, account abuse,
security-related restrictions, enforcement procedures, and other
applicable requirements.

Production content will be inserted after legal review.
""".strip(),
    },
]


def seed_documents():
    app = create_app()

    with app.app_context():

        created_count = 0
        existing_count = 0

        for data in DOCUMENTS:

            existing = (
                LegalDocument.query
                .filter_by(
                    document_type=data["document_type"],
                    version=data["version"]
                )
                .first()
            )

            if existing:
                existing_count += 1
                print(
                    f"[EXISTS] "
                    f"{data['document_type']} v{data['version']}"
                )
                continue

            document = LegalDocument(
                document_type=data["document_type"],
                title=data["title"],
                version=data["version"],
                content=data["content"],
                effective_at=datetime.utcnow(),
                published_at=datetime.utcnow(),
                is_active=True,
            )

            db.session.add(document)
            created_count += 1

            print(
                f"[CREATED] "
                f"{data['document_type']} v{data['version']}"
            )

        db.session.commit()

        print()
        print("=" * 100)
        print("LEGAL DOCUMENT SEED COMPLETE")
        print("=" * 100)
        print("Created:", created_count)
        print("Already existed:", existing_count)
        print(
            "Total legal documents:",
            LegalDocument.query.count()
        )
        print("=" * 100)


if __name__ == "__main__":
    seed_documents()
