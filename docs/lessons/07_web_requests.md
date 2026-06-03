# Lesson 7 — Web Requests

**Goal:** Fetch data from the internet and read the response.

## Vocabulary

| Word | Meaning |
|------|---------|
| `get "url"` | Fetch a web page (HTTP GET) |
| `post "url", body` | Send data to a server (HTTP POST) |
| `status of resp` | The HTTP status code (200 = OK) |
| `body of resp` | The response text (HTML, JSON, etc.) |
| `timeout 5` | Optional: max seconds to wait (default 10) |

## Teacher's guide

### Concept

The internet is just computers talking to each other. Your E program
can talk to any web server by sending a **request** and getting a
**response**. The two most common types of requests are:

- **GET** — "Give me this page" (reading)
- **POST** — "Here is some data" (sending)

### Talking points

- `get` fetches a URL and returns a **response object**.
- Use `status of` to check if the request worked (200 = success).
- Use `body of` to get the actual content.
- `timeout 5` limits how long to wait (in seconds).

### Example

```
let resp be get "https://example.com"
say status of resp
say body of resp
```

Run this and discuss:
- What does `200` mean?
- What does the body look like?

## Tinker

1. Try a URL that doesn't exist (e.g. `https://httpstat.us/404`).
   What status code do you get?
2. Add `timeout 1` — what happens on a slow site?
3. Try `post "https://httpstat.us/200", "hello"`.
   What status code comes back?

## Challenge

Write a program that:
1. Fetches `https://httpstat.us/200`
2. Checks the status code
3. Says "Success!" if it's 200, otherwise says "Failed"
