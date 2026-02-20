from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models, hashing

# Create the tables in the new DB file
models.Base.metadata.create_all(bind=engine)

def force_seed():
    db: Session = SessionLocal()
    
    # 1. Create the Vendor User
    vendor_user = models.User(
        username="pizza_king", 
        email="owner@pizza.com", 
        hashed_password=hashing.Hash.bcrypt("password123")
    )
    db.add(vendor_user)
    db.commit()
    db.refresh(vendor_user)

    # 2. Create the Vendor Profile LINKED to that user
    new_vendor = models.Vendor(
        restaurant_name="Pizza King HQ",
        description="Best slices in the campus!",
        owner_id=vendor_user.id
    )
    db.add(new_vendor)
    db.commit()
    db.refresh(new_vendor)

    # 3. Add some Food Items
    food = models.FoodItem(name="Margherita", price=10.0, vendor_id=new_vendor.id)
    db.add(food)
    
    # 4. Add a dummy Order
    test_order = models.Order(
        user_id=vendor_user.id, # Ordering from himself for testing
        vendor_id=new_vendor.id,
        total_price=10.0,
        status="Pending"
    )
    db.add(test_order)
    db.commit()
    
    print(f"✅ Created Vendor User (ID: {vendor_user.id}) and Vendor Profile (OwnerID: {new_vendor.owner_id})")
    db.close()

if __name__ == "__main__":
    force_seed()