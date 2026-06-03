# Lesson 17 — JSON Parsing

**Goal:** Read and work with JSON data from the web.

## Vocabulary

| Word | Meaning |
|------|---------|
| `json parse text` | Convert JSON text into an E value |
| `json keys obj` | Get the keys of a JSON object |
| `json value obj, key` | Get one value from a JSON object |
| `json of resp` | Shorthand: parse the body of a response |
| `json of value` | Convert an E value back to JSON text |

## Teacher's guide

### Concept

**JSON** (JavaScript Object Notation) is the most common format for
data on the internet. APIs, websites, and apps all exchange data as
JSON. E can parse JSON so you can work with it like any other value.

### How JSON maps to E

| JSON | E |
|------|---|
| `"hello"` | `"hello"` (string) |
| `42` | `42` (number) |
| `true` / `false` | `true` / `false` |
| `null` | `nothing` |
| `{"name": "Alice"}` | `[["name", "Alice"]]` (list of pairs) |
| `[1, 2, 3]` | `[1, 2, 3]` (list) |

### Talking points

- JSON objects become **lists of pairs**: `[["key", "value"]]`.
- Use `json keys` to get just the keys.
- Use `json value` to get a specific value by key.
- `json of resp` is shorthand for `json parse body of resp`.

### Example

```
let resp be get "https://httpbin.org/get"
let data be json of resp
let keys be json keys data
say keys
```

Run this and discuss:
- What keys do you see?
- How would you get just the `"url"` value?

## Tinker

1. Try `json value data, "url"` — what do you get?
2. What happens if you try `json value data, "nonexistent"`?
3. Convert a list to JSON: `json of ["a", "b", "c"]`
4. Convert a number: `json of 42`

## Challenge

Write a program that:
1. Fetches `https://httpbin.org/get`
2. Parses the response
3. Extracts and prints the `"origin"` value (your IP address)
