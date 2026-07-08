from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base

class ProductDB(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)
    url = Column(String(500), unique=True, index=True, nullable=False)
    brand = Column(String(100), nullable=True)
    source_site = Column(String(100), default="dentstore.bg")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Inventory fields
    quantity = Column(Integer, default=10, nullable=False)
    max_quantity = Column(Integer, default=10, nullable=False)

    # Establish one-to-many relationship with price history
    price = relationship(
        "PriceHistoryDB", back_populates="product", cascade="all, delete-orphan"
    )

class PriceHistoryDB(Base):
    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(
        Integer,
        ForeignKey("products.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    # Numeric type Prevent rounding Calculation errors for money
    old_price = Column(Numeric(10, 2), nullable=False)
    new_price = Column(Numeric(10, 2), nullable=False)

    is_promotion = Column(Boolean, default=False, index=True)
    scrapped_at = Column(DateTime(timezone=True), server_default=func.now())

    product = relationship("ProductDB", back_populates="price")
