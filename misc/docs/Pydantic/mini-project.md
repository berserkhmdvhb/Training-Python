

## ✅ Mini Project Structure

    mini_project/
    ├── models/
    │   ├── entity.py          # Entity models
    │   ├── dto.py             # DTO models
    │   ├── envelope.py        # Response wrapper
    │   ├── config.py          # Configuration model
    │   └── validation.py      # Validation model
    ├── services/
    │   └── user_service.py    # Business logic
    ├── api/
    │   └── main.py            # Simulated API layer
    └── run_demo.py            # Entry point

***

### **models/entity.py**

```python
from dataclasses import dataclass
from datetime import datetime

@dataclass
class User:
    id: int
    name: str
    email: str
    created_at: datetime
```

***

### **models/dto.py**

```python
from pydantic import BaseModel, EmailStr
from models.entity import User

class UserDTO(BaseModel):
    name: str
    email: EmailStr

    @classmethod
    def from_internal(cls, user: User):
        """Convert internal User entity to external DTO."""
        return cls(name=user.name, email=user.email)
```

***

### **models/envelope.py**

```python
from typing import Generic, TypeVar

T = TypeVar('T')

class ResponseEnvelope(Generic[T]):
    def __init__(self, data: T, status: str = "success", message: str = ""):
        self.data = data
        self.status = status
        self.message = message

    def to_dict(self):
        return {
            "status": self.status,
            "message": self.message,
            "data": self.data
        }

    @classmethod
    def from_internal(cls, dto: T, message: str = ""):
        """Wrap DTO in a standardized response envelope."""
        return cls(data=dto.dict(), message=message)
```

***

### **models/config.py**

```python
from pydantic import BaseModel

class AppConfig(BaseModel):
    debug: bool
    database_url: str
```

***

### **models/validation.py**

```python
from pydantic import BaseModel, EmailStr

class UserInput(BaseModel):
    name: str
    email: EmailStr

    def to_entity(self, user_id: int):
        """Convert validated input into an internal User entity."""
        from datetime import datetime
        from models.entity import User
        return User(id=user_id, name=self.name, email=self.email, created_at=datetime.utcnow())
```

***

### **services/user\_service.py**

```python
from models.validation import UserInput
from models.entity import User

class UserService:
    _id_counter = 1

    def create_user(self, input_data: UserInput) -> User:
        user = input_data.to_entity(user_id=self._id_counter)
        self._id_counter += 1
        return user
```

***

### **api/main.py**

```python
from models.dto import UserDTO
from models.envelope import ResponseEnvelope
from services.user_service import UserService
from models.validation import UserInput

def create_user_api(payload: dict):
    # Validate input
    validated_input = UserInput(**payload)

    # Business logic
    service = UserService()
    user_entity = service.create_user(validated_input)

    # Convert to DTO
    user_dto = UserDTO.from_internal(user_entity)

    # Wrap in envelope
    response = ResponseEnvelope.from_internal(user_dto, message="User created successfully")
    return response.to_dict()
```

***

### **run\_demo.py**

```python
from api.main import create_user_api

if __name__ == "__main__":
    payload = {"name": "Alice", "email": "alice@example.com"}
    result = create_user_api(payload)
    print(result)
```

***

## ✅ How `from_internal()` Fits In

*   **DTO** uses `from_internal()` to convert **Entity → DTO**.
*   **Envelope** uses `from_internal()` to wrap **DTO → Response**.
*   **Validation model** uses `to_entity()` to convert **validated input → Entity**.

This pattern:

*   Keeps **internal representation private**.
*   Makes **API responses clean and safe**.
*   Improves **maintainability** (you can change internal models without breaking external contracts).


✅ This mini project is **production-like**, modular, and demonstrates **best practices** for model separation and conversion.

***

