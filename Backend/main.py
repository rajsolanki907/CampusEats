from fastapi import FastAPI, Depends, HTTPException, status 
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
import models, database, schemas, token_logic, config
from typing import List
from hashing import Hash
from jose import jwt
from typing import List

app = FastAPI()

app.add_middleware(
    CORSMiddleware  ,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

models.Base.metadata.create_all(bind=database.engine)

# Dependency to get the database session
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Helper to decode the token and get the username
def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, token_logic.SECRET_KEY, algorithms=[token_logic.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except Exception:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

@app.post("/register", response_model=schemas.UserResponse)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_pass = Hash.bcrypt(user.password)
    
    new_user = models.User(
        username=user.username, 
        email=user.email, 
        hashed_password=hashed_pass 
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/login")
def login(request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == request.username).first()
    
    if not user or not Hash.verify(user.hashed_password, request.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, # Changed to 401 for security
            detail="Invalid Credentials"
        )
    
    access_token = token_logic.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me")
def read_users_me(current_user: str = Depends(get_current_user)):
    return {"username": current_user, "message": "You are authorized!"}

@app.post("/vendors/", response_model=schemas.VendorResponse)
def create_vendor(
    vendor: schemas.VendorCreate, 
    db: Session = Depends(get_db), 
    current_user_name: str = Depends(get_current_user)
):
    user = db.query(models.User).filter(models.User.username == current_user_name).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    existing_vendor = db.query(models.Vendor).filter(models.Vendor.owner_id == user.id).first()
    if existing_vendor:
        raise HTTPException(status_code=400, detail="You already have a vendor profile")

    new_vendor = models.Vendor(
        restaurant_name=vendor.restaurant_name,
        description=vendor.description,
        owner_id=user.id
    )
    db.add(new_vendor)
    db.commit()
    db.refresh(new_vendor)
    return new_vendor


@app.post("/vendors/my-menu/items", response_model=schemas.FoodResponse)
def add_food_item(
    food: schemas.FoodCreate, 
    db: Session = Depends(get_db), 
    current_user_name: str = Depends(get_current_user)
):
    # 1. Find the User
    user = db.query(models.User).filter(models.User.username == current_user_name).first()
    
    # 2. Find the Vendor owned by this User
    vendor = db.query(models.Vendor).filter(models.Vendor.owner_id == user.id).first()
    
    if not vendor:
        raise HTTPException(status_code=403, detail="Only vendors can add food items.")

    # 3. Create the Food Item
    new_food = models.FoodItem(
        name=food.name,
        price=food.price,
        vendor_id=vendor.id
    )
    db.add(new_food)
    db.commit()
    db.refresh(new_food)
    return new_food

@app.get("/vendor/dashboard", response_model=List[schemas.OrderResponse])
def get_vendor_dashboard(
    db: Session = Depends(get_db), 
    current_user_name: str = Depends(get_current_user)
):
    # 1. Identify the user
    user = db.query(models.User).filter(models.User.username == current_user_name).first()
    
    # 2. Find the vendor owned by this user
    vendor = db.query(models.Vendor).filter(models.Vendor.owner_id == user.id).first()
    
    if not vendor:
        raise HTTPException(status_code=404, detail="You are not registered as a vendor.")

    # 3. Fetch all orders for this specific vendor
    orders = db.query(models.Order).filter(models.Order.vendor_id == vendor.id).all()
    
    return orders

@app.put("/vendor/orders/{order_id}/status", response_model=schemas.OrderResponse)
def update_order_status(
    order_id: int, 
    new_status: str, 
    db: Session = Depends(get_db), 
    current_user_name: str = Depends(get_current_user)
):
    # Security: Verify the user owns the vendor that received this order
    user = db.query(models.User).filter(models.User.username == current_user_name).first()
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
        
    vendor = db.query(models.Vendor).filter(models.Vendor.id == order.vendor_id).first()
    if vendor.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this order")

    # Update and save
    order.status = new_status
    db.commit()
    db.refresh(order)
    return order

# Route to see ALL food from ALL vendors
@app.get("/menu/", response_model=List[schemas.FoodResponse])
def get_all_menu_items(db: Session = Depends(get_db)):
    items = db.query(models.FoodItem).all()
    return items

# Route to see menu items for a SPECIFIC vendor
@app.get("/vendors/{vendor_id}/menu", response_model=List[schemas.FoodResponse])
def get_vendor_menu(vendor_id: int, db: Session = Depends(get_db)):
    items = db.query(models.FoodItem).filter(models.FoodItem.vendor_id == vendor_id).all()
    return items

# 1. ADD ITEM TO CART
@app.post("/cart/", response_model=schemas.CartItemResponse)
def add_to_cart(
    item: schemas.CartItemCreate, 
    db: Session = Depends(get_db), 
    current_user_name: str = Depends(get_current_user)
):
    # Identify user
    user = db.query(models.User).filter(models.User.username == current_user_name).first()
    
    # Check if item already exists in cart for this user
    existing_item = db.query(models.CartItem).filter(
        models.CartItem.user_id == user.id, 
        models.CartItem.food_id == item.food_id
    ).first()

    if existing_item:
        existing_item.quantity += item.quantity
        db.commit()
        db.refresh(existing_item)
        return existing_item

    # If new, create entry
    new_cart_item = models.CartItem(user_id=user.id, food_id=item.food_id, quantity=item.quantity)
    db.add(new_cart_item)
    db.commit()
    db.refresh(new_cart_item)
    return new_cart_item

# 2. VIEW MY CART
@app.get("/cart/", response_model=List[schemas.CartItemResponse])
def get_cart(db: Session = Depends(get_db), current_user_name: str = Depends(get_current_user)):
    user = db.query(models.User).filter(models.User.username == current_user_name).first()
    return db.query(models.CartItem).filter(models.CartItem.user_id == user.id).all()

@app.post("/cart/checkout", response_model=schemas.OrderResponse)
def checkout(
    db: Session = Depends(get_db), 
    current_user_name: str = Depends(get_current_user)
):
    # 1. Get User
    user = db.query(models.User).filter(models.User.username == current_user_name).first()
    
    # 2. Get all items in this user's cart
    cart_items = db.query(models.CartItem).filter(models.CartItem.user_id == user.id).all()
    
    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    # Enforce single-vendor carts for now to keep the data model simple.
    vendor_ids = {item.food.vendor_id for item in cart_items}
    if len(vendor_ids) > 1:
        raise HTTPException(
            status_code=400,
            detail="Cart contains items from multiple vendors. Please clear your cart and order from one restaurant at a time.",
        )

    # 3. Calculate total price
    total = sum(item.food.price * item.quantity for item in cart_items)
    
    # 4. Create the Order for this user and vendor
    new_order = models.Order(
        user_id=user.id,
        vendor_id=cart_items[0].food.vendor_id,
        total_price=total,
        status="Pending"
    )
    
    db.add(new_order)
    db.flush()

    # 5. Create order items capturing the price at purchase time
    for item in cart_items:
        order_item = models.OrderItem(
            order_id=new_order.id,
            food_id=item.food_id,
            quantity=item.quantity,
            unit_price=item.food.price,
        )
        db.add(order_item)
        db.delete(item)
    
    db.commit()
    db.refresh(new_order)
    return new_order

@app.get("/orders/me", response_model=List[schemas.OrderResponse])
def get_my_order_history(
    db: Session = Depends(get_db), 
    current_user_name: str = Depends(get_current_user)
):
    # 1. Find the logged-in user
    user = db.query(models.User).filter(models.User.username == current_user_name).first()
    
    # 2. Fetch only the orders belonging to this user
    # We use the 'orders' relationship we added to the User model earlier
    return user.orders