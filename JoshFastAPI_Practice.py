
from fastapi import FastAPI, HTTPException, Path, status
from pydantic import BaseModel, field_validator


# ==========================================
# 1. SCHEMAS (Data Validation Gatekeepers)
# ==========================================
class User(BaseModel):
    name: str
    age: int
    role: str
    website: str

    # Automatically converts name to lowercase on creation
    @field_validator("name")
    @classmethod
    def lower_name(cls, value: str) -> str:
        return value.lower()


class UpdateUser(BaseModel):
    name: str | None = None
    age: int | None = None
    role: str | None = None
    website: str | None = None


# ==========================================
# 2. IN-MEMORY DATABASE
# ==========================================
users = {
    1: {
        "name": "josh",
        "website": "www.zerotoknowing.com",
        "age": 28,
        "role": "developer",
    }
}

app = FastAPI()


# ==========================================
# 3. API ENDPOINTS (Routes)
# ==========================================


# Root Endpoint
@app.get("/")
def root():
    return {"message": "My first FastAPI call"}


# Search Endpoint (MUST be defined before /users/{user_id})
@app.get("/users/search/")
def search_by_name(name: str | None = None):
    if not name:
        return {"message": "Name parameter is required"}

    search_term = name.lower()
    for user in users.values():
        if user["name"].lower() == search_term:
            return user

    raise HTTPException(status_code=404, detail="User not found")


# Read Single User (GET)
@app.get("/users/{user_id}")
def get_user(
    user_id: int = Path(
        ..., description="The ID you want to get", gt=0, lt=100
    ),
):
    if user_id not in users:
        raise HTTPException(status_code=404, detail="User not found")
    return users[user_id]


# Create User (POST)
@app.post("/users/{user_id}", status_code=status.HTTP_201_CREATED)
def create_user(user_id: int, user: User):
    if user_id in users:
        raise HTTPException(status_code=400, detail="User already exists")

    # Save to dictionary using model_dump() (Pydantic V2)
    users[user_id] = user.model_dump()
    return users[user_id]


# Partial Update User (PATCH)
@app.patch("/users/{user_id}")
def update_user(user_id: int, user: UpdateUser):
    if user_id not in users:
        raise HTTPException(status_code=404, detail="User not found")

    # Get only the fields explicitly provided by client
    update_data = user.model_dump(exclude_unset=True)

    # Lowercase name if it was passed in the update
    if "name" in update_data and update_data["name"]:
        update_data["name"] = update_data["name"].lower()

    users[user_id].update(update_data)
    return users[user_id]


# Delete User (DELETE)
@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    if user_id not in users:
        raise HTTPException(status_code=404, detail="User not found")

    deleted_user = users.pop(user_id)
    return {"message": "User has been deleted", "deleted_user": deleted_user}