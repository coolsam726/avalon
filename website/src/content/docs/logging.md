---
title: Logging
description: Application logging arrives with the exception handler in M8.
---

:::caution[Not shipped yet]
There is no `config/logging.py` or `log()` helper in framework core yet. **M8** ships logging together with the exception `Handler` so `report()` has a real destination.
:::

## Planned shape (M8)

- `config/logging.py` with channels (`stack`, `single`, `daily`, `stderr`)
- Levels and context; `log()` helper
- Exception `report()` writes through the logger
- Console (M9) reuses the same handler for uncaught command errors

## Until then

Use Python's `logging` module in application code if you need diagnostics, or wait for M8 for the Laravel-shaped façade.

## Related

- [Error Handling](/errors/)
