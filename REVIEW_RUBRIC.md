# Review rubric (what I check beyond green tests)

Each ticket is scored Accepted / Rework. Automatic Rework if any of these appears:

- Tests edited, skipped or special-cased (`if "test" in ...`).
- Bare `except`, swallowed exceptions, `# type: ignore` without a reason, `Any` used to silence mypy.
- Whole file loaded in memory (`read()`, `readlines()`, `list(...)` on the stream) in T2/T3/CLI.
- SQL built with f-strings or `%` (T4).
- Mutable default arguments, global mutable state, `print` for logging.
- Code you cannot explain line by line.

Per ticket I also look at: naming, function size (one job per function), error messages, docstrings that
say *why*, and whether edge cases are handled deliberately rather than by luck.

## Questions you must answer about your own code (oral check)
1. Why a generator in T2? What happens to the open file if the consumer stops after 3 items?
2. Why is `True` a valid `float` for Python and how did you reject it?
3. Why `deque(maxlen)` rather than slicing a list? Complexity of your detector?
4. What does `functools.wraps` fix? What happens in `@timed` if the function raises?
5. What is a transaction, and where exactly does your code roll back?
6. Why parameterized queries? Show the injection test and explain why it passes.
7. Difference between `asyncio.gather(return_exceptions=True)` and `TaskGroup`. Which did you pick and why?
8. Why `2` as exit code and why stderr?
9. What does `pip install -e .` do and why the `src/` layout?
10. What would you change to run T3 on 1 billion rows?
