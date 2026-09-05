---
title: Strings
description: Str, Stringable, and the str_() helper for fluent string work.
---

## Introduction

Avalon’s string utilities live in `avalon.support`. Like other Support helpers,
they are **not** Python globals and are **not** on the `avalon` package root —
import them explicitly:

```python
from avalon.support import Str, Stringable, str_
```

| Entry | Role |
| --- | --- |
| `Str` | Static methods (`Str.slug(...)`, `Str.camel(...)`, …) |
| `str_(value)` | Returns a fluent `Stringable` |
| `Str.of(value)` | Same as `str_(value)` |
| `Stringable` | Chainable wrapper; most methods return another `Stringable` |

`str_` is spelled with a trailing underscore because Python reserves `str`.

```python
Str.slug("Hello World!")          # "hello-world"
Str.camel("foo_bar")              # "fooBar"
Str.snake("FooBar")               # "foo_bar"
Str.limit("abcdef", 3)            # "abc..."
Str.uuid()                        # RFC 4122 string
Str.plural("child")               # "children"

str_("FooBar").snake().upper()    # Stringable → "FOO_BAR"
```

## Fluent strings

Begin a chain with `str_()` or `Str.of()`:

```python
title = (
    str_("steve_jobs")
    .headline()
    .append(" — Avalon")
    .to_string()
)
# "Steve Jobs — Avalon"
```

Most transformers return a new `Stringable`. Finish with `to_string()` /
`__str__` when you need a plain `str`. Boolean / scalar checks return Python
values instead of wrapping:

```python
str_("Avalon").contains("val")       # True
str_("Avalon").starts_with("Ava")    # True
str_("Avalon").length()              # 6
```

## Case conversion

```python
Str.camel("foo_bar")       # "fooBar"
Str.studly("foo_bar")      # "FooBar"
Str.snake("FooBar")        # "foo_bar"
Str.kebab("FooBar")        # "foo-bar"
Str.title("hello world")   # "Hello World"
Str.headline("steve_jobs") # "Steve Jobs"
Str.lower("ADA")           # "ada"
Str.upper("ada")           # "ADA"
Str.lcfirst("Ada")         # "ada"
Str.ucfirst("ada")         # "Ada"
```

## Inspection

```python
Str.contains("Avalon", "val")
Str.contains_all("Avalon", ["Ava", "lon"])
Str.doesnt_contain("Avalon", "php")
Str.starts_with("Avalon", "Ava")
Str.ends_with("Avalon", "lon")
Str.is_("*.py", "app.py")      # also Str.is(...)
Str.is_ascii("Ada")
Str.is_json('{"a":1}')
Str.is_url("https://example.com")
Str.is_uuid("…")
Str.is_ulid("…")
Str.length("Avalon")
Str.position("Avalon", "val")
```

`is` is a Python keyword, so prefer `Str.is_()` in typed code; `Str.is` is
available as an alias where the runtime allows it.

## Truncation & excerpts

```python
Str.limit("The quick brown fox", 10)          # "The quick..."
Str.words("The quick brown fox", 2)           # "The quick..."
Str.take("Avalon", 3)                         # "Ava"
Str.excerpt("… long text …", phrase="long")
```

## Replace, remove, pad

```python
Str.replace("world", "Avalon", "Hello world")
Str.replace_first("a", "x", "a a a")
Str.replace_last("a", "x", "a a a")
Str.replace_start("Hello", "Hi", "Hello world")
Str.replace_end("world", "Avalon", "Hello world")
Str.remove(["-", "_"], "a-b_c")
Str.mask("1234567890", "*", 2, 4)             # "12****7890"
Str.pad_left("7", 3, "0")                     # "007"
Str.pad_right("7", 3, "0")                    # "700"
Str.pad_both("7", 5, "0")                     # "00700"
Str.wrap("Ada", "[", "]")                     # "[Ada]"
Str.unwrap("[Ada]", "[", "]")                 # "Ada"
Str.trim("  Ada  ")
Str.squish("Ada   Lovelace")                  # collapse whitespace
```

## Affixes & substrings

```python
Str.after("users.ada@example.com", "@")
Str.after_last("/a/b/c", "/")
Str.before("users.ada@example.com", "@")
Str.before_last("/a/b/c", "/")
Str.between("[a]", "[", "]")
Str.start("path", "/")
Str.finish("path", "/")
Str.substr("Avalon", 0, 3)
Str.chop_start("xxAda", "xx")
Str.chop_end("Adaxx", "xx")
```

## Pluralization & random

```python
Str.plural("child")                 # "children"
Str.singular("children")            # "child"
Str.plural_studly("UserAccount")
Str.random(16)
Str.password(32)
Str.uuid()
Str.ordered_uuid()
Str.ulid()
```

## Encoding & markdown

```python
Str.ascii("ü")
Str.transliterate("café")
Str.to_base64("Ada")
Str.from_base64("…")
Str.markdown("# Hello")
Str.inline_markdown("**bold**")
Str.slug("Hello World!")            # "hello-world"
```

## Fluent `Stringable` notes

Every static method above is available on `Stringable` with the subject already
bound:

```python
str_("Hello World!").slug().append("-app").to_string()
# "hello-world-app"
```

CamelCase aliases (`replaceFirst`, `startsWith`, …) exist for familiarity;
prefer snake_case in Avalon application code.

## Related

- [Helpers](/helpers/) — `Arr`, `Number`, misc utilities
- [Collections](/collections/) — `collect()`
