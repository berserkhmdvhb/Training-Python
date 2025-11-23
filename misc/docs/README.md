To measure runtime in python:

1 - `timeit`

```python
import timeit
# Time native len() on list
builtin_len_time = timeit.timeit('len(my_list)', globals=globals(), number=1_000_000)

# print statements
print(f"Time of native len() on list        - len(my_list):       {builtin_len_time:.6f} seconds")
```


2 - `perf_counter`

```python
from time import perf_counter as pc
t0 = pc();
floats /= 3;
pc() - t0
```


Option A — dict[str, Any] (mutable payloads)

Option B — Mapping[str, Any] (read-only / more general)

model_dump() returns a dict[str, Any] (or similar) because Pydantic cannot guarantee the exact types of nested fields.
Using Any everywhere is easy but hurts type safety and triggers linter/mypy warnings.
Instead, narrow the type to what you actually expect: usually dict[str, object] or Mapping[str, object].

Example:

```python
job_dict = cast(dict[str, object], job.model_dump())
```


If a model class is imported directly at the top-level of an API route file, and used it in route params, FastAPI treats as a Body (e.g., for POST), as long as there are no class dependencies in the route signatures pulling the model class into the Query path during inspection. This will avoid no forward‑ref trap.
When ones switches to to injecting the model class (or other helpers) via `Depends(...)`, FastAPI starts inspecting the callables involved and any nested annotations they reference. If any helper/dependency (including) annotates the class as (or causes FastAPI to infer it as) a `Query(...)` parameter, OpenAPI generation will try to build `Annotated[<class_name>, Query(...)]`, and with postponed annotations, that shows as a `ForwardRef('<class_name')` unless rebuilt.
If dependency injection is necessary, a solution would be to force the class to be a Body param, so it's used as following:

```
Annotated[<class_name, Body(...)],
```
