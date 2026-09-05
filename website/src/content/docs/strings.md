---
title: Strings
description: Str and Stringable — Laravel Strings parity for Avalon.
---

## Overview

```python
from avalon.support import Str, str_

Str.slug("Hello World!")          # "hello-world"
Str.camel("foo_bar")              # "fooBar"
Str.snake("FooBar")               # "foo_bar"
Str.limit("abcdef", 3)            # "abc..."
Str.uuid()                        # RFC 4122 string
Str.plural("child")               # "children"

str_("FooBar").snake().upper()    # Stringable → "FOO_BAR"
```

`str_()` is Avalon’s spelling of Laravel’s `str()` (Python reserves `str`).

## Fluent strings

```python
from avalon.support import Str

title = (
    Str.of("steve_jobs")
    .headline()
    .append(" — Avalon")
    .to_string()
)
```

Boolean checks return values instead of a fluent wrapper:

```python
Str.of("Avalon").contains("val")      # True
Str.of("Avalon").starts_with("Ava")   # True
```

## Claimed surface

Includes (snake_case + CamelCase aliases where natural): `after`, `after_last`,
`before`, `before_last`, `between`, `camel`, `snake`, `kebab`, `studly`,
`slug`, `title`, `headline`, `limit`, `words`, `contains`, `contains_all`,
`starts_with`, `ends_with`, `replace_*`, `mask`, `pad_*`, `plural` /
`singular`, `uuid` / `ulid` / `ordered_uuid`, `ascii`, `markdown` /
`inline_markdown`, and the fluent `Stringable` wrappers.

`Str.is(...)` is exposed despite Python’s `is` keyword (also available as
`Str.is_`).

## Related

- [Helpers](/helpers/) — `Arr`, `Number`, misc utilities
- [Collections](/collections/)
