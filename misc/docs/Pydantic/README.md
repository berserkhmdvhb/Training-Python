# 📘 Best Practices for Designing API Schemas with FastAPI + Pydantic

## ✅ Why Care About Schema Design?
When building APIs with **FastAPI** and **Pydantic**, schema design impacts:
- **Maintainability**: Easier to evolve without breaking clients.
- **Reusability**: Avoid duplication across routes and services.
- **Validation & Normalization**: Ensure clean, predictable data.
- **Clear Boundaries**: Separate internal models from API-facing DTOs.

---

## 🔍 Core Principles
1. **Separate Concerns**:
   - **Item-level DTOs**: Represent a single entity (e.g., a scraped item).
   - **Envelope-level DTOs**: Represent a response that wraps multiple items plus metadata.

2. **Use Composition, Not Monoliths**:
   - Don’t mix unrelated fields (e.g., job stats with item details).
   - Compose schemas: `ScrapeResult` contains `ScrapedItemDTO`.

3. **Control Extra Fields**:
   - `extra="ignore"` for strict schemas.
   - `extra="allow"` for dynamic schemas (e.g., LLM-driven extra fields).

4. **Normalize Inputs**:
   - Use validators to clean empty strings, enforce types, etc.

---

## 🏗 Example: News Scraper API

### 1. **Item-Level DTO**
```python
from pydantic import BaseModel, HttpUrl, Field, ConfigDict, field_validator

def normalize_optional_str(value: str | None) -> str | None:
    return value.strip() or None if value else None

class ArticleDTO(BaseModel):
    'Represents a single scraped article.'
    url: HttpUrl
    title: str | None = Field(default=None, description='Article title')
    author: str | None = Field(default=None, description='Author name')
    published_date: str | None = Field(default=None, description='Publication date')

    # Normalize empty strings
    _clean_title = field_validator('title', mode='before')(normalize_optional_str)
    _clean_author = field_validator('author', mode='before')(normalize_optional_str)

    model_config = ConfigDict(extra='ignore')  # Strict by default
```

---

### 2. **Dynamic Item DTO**
```python
class ArticleDynamicDTO(ArticleDTO):
    'Allows extra fields for adaptive scraping.'
    model_config = ConfigDict(extra='allow')
```

---

### 3. **Result Envelope**
```python
class ScrapeResultBase(BaseModel):
    stats: dict[str, str] = Field(..., description='Execution metrics')

class ScrapeResultDynamic(ScrapeResultBase):
    items: list[ArticleDynamicDTO] = Field(..., description='Scraped articles')

    @classmethod
    def from_internal(cls, items, stats):
        return cls(items=[ArticleDynamicDTO.model_validate(i) for i in items], stats=stats)
```

---

## ✅ Why Multiple Schemas?
- **Item DTO**: Reusable across routes, debugging, persistence.
- **Result DTO**: Adds job-level metadata, aggregates items.
- **Dynamic vs Fixed**: Supports flexible schemas for LLM-driven extraction.

---

## 🔑 Best Practice Checklist
- ✔ Define **Base DTO** for common fields.
- ✔ Use **validators** for normalization.
- ✔ Create **envelope schemas** for responses.
- ✔ Control `extra` behavior (`ignore` vs `allow`).
- ✔ Provide **factory methods** (`from_internal`) for clean conversion.

---

## 📌 When to Use Multiple DTOs?
- When you have **different layers of data** (item vs job).
- When you need **dynamic fields** for adaptive agents.
- When you want **future-proof design** for schema evolution.

---

### ✅ TL;DR
- **Item DTOs** = “What does one entity look like?”
- **Result DTOs** = “What does the whole response look like?”
- **Dynamic DTOs** = “Allow extra fields for flexibility.”

---

👉 Do you want me to **extend this doc with diagrams** (class relationships + flow in FastAPI routes) and **add a section on common mistakes to avoid**? Or should I **prepare a full README template for your repo** with this as a best-practice guide?
