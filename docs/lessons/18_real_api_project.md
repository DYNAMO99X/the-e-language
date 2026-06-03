# Lesson 18 — Real API Project

**Goal:** Build a complete program that fetches, parses, and displays
real data from a public API.

## Vocabulary

| Word | Meaning |
|------|---------|
| Everything from lessons 7 and 17 | Review |

## Teacher's guide

### Concept

Now you have all the pieces: `get` to fetch data, `json parse` to
understand it, and lists/loops/functions to work with it. Let's combine
them into a real project.

### Project: Random joke fetcher

We'll use the Official Joke API — no signup needed:

```
to fetch_joke
    let resp be get "https://official-joke-api.appspot.com/random_joke"
    let joke be json of resp
    let setup be json value joke, "setup"
    let punchline be json value joke, "punchline"
    say setup
    say punchline
end

fetch_joke
```

### Walking through it step by step

1. `get` fetches a random joke from the API
2. `json of resp` parses the response
3. `json value joke, "setup"` extracts the question
4. `json value joke, "punchline"` extracts the answer
5. We put it in a function so we can call it again and again

### Talking points

- APIs return data in **structured formats** (usually JSON).
- The same `get` + `json parse` pattern works for *any* API.
- Error handling: what if the network is down? (We'll learn `if` soon.)

## Tinker

1. Call `fetch_joke` five times — do you get different jokes?
2. Modify the function to also extract `"type"` — what values do you see?
3. Try a different API:
   `https://api.agify.io?name=michael`
   What keys come back?

## Challenge

Build a **weather display**:
1. Fetch `https://wttr.in/YourCity?format=j1` (replace YourCity)
2. Parse the response
3. Extract and display:
   - The current temperature
   - The weather description
   - The "feels like" temperature

Hint: The JSON structure has nested objects. You may need to use
`json value` multiple times to drill down.
