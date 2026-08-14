"""
Marketplace business-logic service.

The service layer controls marketplace listing retrieval,
validation, creation, ownership and lifecycle operations.

Routes coordinate HTTP requests only.
"""

from app.database import db
from app.models.marketplace_listing import MarketplaceListing
from app.models.user import User
from app.services.message_service import get_or_create_conversation


PUBLISHED_STATUS = "published"

VALID_LISTING_STATUSES = {
    "draft",
    "published",
    "archived",
}


# ============================================================
# ACCOUNT VALIDATION
# ============================================================

def get_business_user(user_id):
    """
    Return a valid business account.

    Marketplace listings belong to business/admin accounts.
    """

    if not user_id:
        return None

    return (
        User.query
        .filter(
            User.id == user_id,
            User.account_type == "admin",
        )
        .first()
    )


# ============================================================
# PUBLIC MARKETPLACE
# ============================================================

def get_published_listings():
    """
    Return listings currently visible in the public marketplace.

    Draft and archived listings are excluded.
    """

    return (
        MarketplaceListing.query
        .filter(
            MarketplaceListing.status == PUBLISHED_STATUS
        )
        .order_by(
            MarketplaceListing.featured.desc(),
            MarketplaceListing.created_at.desc(),
        )
        .all()
    )


def get_listing_by_id(listing_id):
    """
    Return one published marketplace listing.
    """

    if not listing_id:
        return None

    return (
        MarketplaceListing.query
        .filter(
            MarketplaceListing.id == listing_id,
            MarketplaceListing.status == PUBLISHED_STATUS,
        )
        .first()
    )


# ============================================================
# BUSINESS LISTINGS
# ============================================================

def get_business_listings(business_id):
    """
    Return all listings owned by a business.

    Draft, published and archived listings are included.
    """

    if not business_id:
        return []

    return (
        MarketplaceListing.query
        .filter(
            MarketplaceListing.business_id == business_id
        )
        .order_by(
            MarketplaceListing.created_at.desc()
        )
        .all()
    )


def get_business_listing(listing_id, business_id):
    """
    Return a listing only when it belongs to the supplied business.
    """

    if not listing_id or not business_id:
        return None

    return (
        MarketplaceListing.query
        .filter(
            MarketplaceListing.id == listing_id,
            MarketplaceListing.business_id == business_id,
        )
        .first()
    )


# ============================================================
# VALIDATION
# ============================================================

def validate_listing_data(
    title,
    description=None,
    category=None,
    price=None,
    currency="NGN",
    status="draft",
):
    """
    Validate marketplace listing data.

    Raises ValueError for invalid supplied data.
    """

    title = (title or "").strip()

    if not title:
        raise ValueError(
            "Marketplace listing title is required."
        )

    if len(title) > 255:
        raise ValueError(
            "Marketplace listing title cannot exceed 255 characters."
        )

    if description is not None:
        description = description.strip()

        if len(description) > 5000:
            raise ValueError(
                "Marketplace listing description cannot exceed 5000 characters."
            )

    if category is not None:
        category = category.strip()

        if len(category) > 100:
            raise ValueError(
                "Marketplace listing category cannot exceed 100 characters."
            )

    currency = (currency or "NGN").strip().upper()

    if len(currency) != 3 or not currency.isalpha():
        raise ValueError(
            "Currency must be a valid three-letter currency code."
        )

    if status not in VALID_LISTING_STATUSES:
        raise ValueError(
            "Invalid marketplace listing status."
        )

    normalized_price = None

    if price not in (None, ""):

        try:
            normalized_price = float(price)
        except (TypeError, ValueError):
            raise ValueError(
                "Marketplace listing price must be a valid number."
            )

        if normalized_price < 0:
            raise ValueError(
                "Marketplace listing price cannot be negative."
            )

    return {
        "title": title,
        "description": description,
        "category": category,
        "price": normalized_price,
        "currency": currency,
        "status": status,
    }


# ============================================================
# CREATE
# ============================================================

def create_listing(
    business_id,
    title,
    description=None,
    category=None,
    price=None,
    currency="NGN",
    style_id=None,
    image_path=None,
    status="draft",
    featured=False,
):
    """
    Create a marketplace listing owned by a business account.
    """

    business = get_business_user(business_id)

    if not business:
        raise ValueError(
            "A valid business account is required."
        )

    data = validate_listing_data(
        title=title,
        description=description,
        category=category,
        price=price,
        currency=currency,
        status=status,
    )

    listing = MarketplaceListing(
        business_id=business.id,
        style_id=style_id,
        image_path=image_path,
        featured=bool(featured),
        **data,
    )

    db.session.add(listing)
    db.session.commit()

    return listing


# ============================================================
# UPDATE
# ============================================================

def update_listing(
    listing,
    title,
    description=None,
    category=None,
    price=None,
    currency="NGN",
    style_id=None,
    image_path=None,
    status="draft",
    featured=False,
):
    """
    Update an existing listing.
    """

    if not listing:
        raise ValueError(
            "Marketplace listing could not be found."
        )

    data = validate_listing_data(
        title=title,
        description=description,
        category=category,
        price=price,
        currency=currency,
        status=status,
    )

    listing.title = data["title"]
    listing.description = data["description"]
    listing.category = data["category"]
    listing.price = data["price"]
    listing.currency = data["currency"]
    listing.status = data["status"]
    listing.style_id = style_id
    listing.image_path = image_path
    listing.featured = bool(featured)

    db.session.commit()

    return listing


# ============================================================
# LIFECYCLE
# ============================================================

def publish_listing(listing):
    """
    Publish a listing.
    """

    if not listing:
        raise ValueError(
            "Marketplace listing could not be found."
        )

    listing.status = "published"

    db.session.commit()

    return listing


def archive_listing(listing):
    """
    Archive a listing without deleting its database record.
    """

    if not listing:
        raise ValueError(
            "Marketplace listing could not be found."
        )

    listing.status = "archived"

    db.session.commit()

    return listing

# ============================================================
# MARKETPLACE -> MESSAGING
# ============================================================

def start_listing_conversation(listing, client_id):
    """
    Start or retrieve a conversation between a client and
    the business that owns a marketplace listing.

    The listing itself provides the business identity.

    A marketplace conversation is initially not tied to an
    order because the client may be making a pre-purchase
    enquiry.
    """

    if not listing:
        raise ValueError(
            "Marketplace listing could not be found."
        )

    if not client_id:
        raise ValueError(
            "A client account is required."
        )

    if listing.business_id == client_id:
        raise ValueError(
            "A business cannot start a conversation with itself."
        )

    client = (
        User.query
        .filter(
            User.id == client_id,
            User.account_type == "client",
        )
        .first()
    )

    if not client:
        raise ValueError(
            "Only client accounts can contact marketplace businesses."
        )

    business = (
        User.query
        .filter(
            User.id == listing.business_id,
            User.account_type == "admin",
        )
        .first()
    )

    if not business:
        raise ValueError(
            "The marketplace business could not be found."
        )

    conversation, created = get_or_create_conversation(
        client_id=client.id,
        business_id=business.id,
        order_id=None,
        listing_id=listing.id,
    )

    return conversation, created
