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

