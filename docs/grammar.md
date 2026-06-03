# E — Formal Grammar Reference

This document specifies the grammar of E. It is intended for people who want
to understand the language precisely or contribute to its implementation.

## Lexical grammar

E source code is a stream of tokens. The lexer recognizes:

### Literals
- `NUMBER` — one or more digits, optionally followed by `.` and more digits, optionally preceded by `-` (when at the start of a statement or after a non-value token)
- `STRING` — `"..."`, `'...'`, or `` `...` `` (all equivalent). Supports escapes `\\`, `\n`, `\t`, `\"`, `\'`, `` \` ``. Cross-quote escapes also work (e.g. `\'` inside `"..."`).
- `true`, `false`, `nothing`

### Identifiers
- A letter or `_` followed by letters, digits, or `_`
- Case-insensitive for keywords

### Keywords
Single-word: `let`, `be`, `say`, `ask`, `if`, `then`, `else`, `end`, `while`,
`repeat`, `times`, `for`, `each`, `in`, `to`, `return`, `true`, `false`,
`nothing`, `and`, `or`, `not`, `plus`, `minus`, `mod`, `is`, `by`, `at`,
`with`, `added`, `size`, `of`, `turtle`, `move`, `make`, `goto`, `set`

Multi-word (matched longest-first):
- `is not equal to`
- `is equal to`
- `is greater than or equal to`
- `is less than or equal to`
- `is greater than`
- `is less than`
- `divided by`

### Symbols
`,` `(` `)` `[` `]` `>` `<` `>=` `<=` `=` `==` `!=`

### Structural
- `NEWLINE` — statement separator (optional in many places)
- `--` — line comment (to end of line)
- `EOF` — end of file

## Expression grammar

Precedence from lowest to highest:

```
expression    := concat
concat        := or ("," or)*
or            := and ("or" and)*
and           := unary_logic ("and" unary_logic)*
unary_logic   := "not" unary_logic | comparison
comparison    := additive (comp_op additive)?
   where comp_op ∈ { is, is not equal to, is greater than [or equal to],
                     is less than [or equal to], =, ==, !=, >, <, >=, <= }
additive      := multiplicative (("plus" | "+" | "minus" | "-") multiplicative)*
multiplicative:= unary (("times" | "*" | "divided" "by" | "/" | "mod") unary)*
unary         := "-" unary | postfix
postfix       := size_of_or_primary ("at" call_arg | "with" call_arg "added")*
size_of_or_primary
              := "size" "of" size_of_or_primary | primary
primary       := NUMBER | STRING | "true" | "false" | "nothing"
               | "turtle"                                -- turtle factory
               | IDENT (call_arg ("," call_arg)*)?     -- call if followed by expression
               | "ask" expression                       -- input
               | "[" (call_arg ("," call_arg)*)? "]"
               | "(" expression ")"
call_arg      := primary ("at" call_arg | "with" call_arg "added")*
```

The `call_arg` rule is a restricted form of expression used as a function
argument. It does not include binary operators — those belong to the
surrounding expression. Use parentheses to pass a complex expression:
`add (3 plus 4), 5`.

## Statement grammar

```
program       := (statement NEWLINE?)*

statement     := "let" IDENT "be" expression
               | "say" expression
               | "if" expression "then" block
                   ("else" "if" expression "then" block)*
                   ("else" block)?
                   "end"
               | "while" expression block "end"
               | "repeat" primary "times" block "end"
               | "for" "each" IDENT "in" expression block "end"
               | "to" IDENT IDENT* block "end"
               | "return" expression?
               | "move" IDENT direction additive        -- turtle movement
               | "make" IDENT make_action                -- turtle actions
               | "set" IDENT set_property "to" expression
               | expression                              -- bare expression statement

direction     := "forward" | "backward" | "left" | "right"
make_action   := "hide" | "show" | "close" "pen" | "open" "pen"
               | "erase" "all" | "restart" | "go" "home"
               | "draw" ("circle" | "dot") additive
               | "speed" additive
               | "go" "to" additive "and" additive      -- raw goto
               | "goto" additive ("right" | "left") "and"
                         additive ("up" | "down")        -- relative goto
set_property  := "pen" ("color" | "size") | IDENT        -- e.g. "pen color", "background"

block         := (statement NEWLINE?)*
```

## Built-in functions

| Name         | Arity | Description                          |
|--------------|-------|--------------------------------------|
| `ask`        | 1     | Read a line of text from the user    |
| `number`     | 1     | Convert a value to a number          |
| `text`       | 1     | Convert a value to text              |
| `uppercase`  | 1     | Convert text to UPPERCASE            |
| `lowercase`  | 1     | Convert text to lowercase            |
| `random`     | 2     | Random integer between two numbers   |

## Type rules

E is dynamically typed. Values have one of these types at runtime:
- **number** (int or float)
- **text** (string)
- **true/false** (bool)
- **nothing** (None)
- **list** (heterogeneous)

The `,` operator converts each operand to text and concatenates.
The `plus`/`minus`/`times`/`divided by`/`mod` operators require both
operands to be numbers (or convertible to numbers).
The comparison operators require both operands to be numbers, except
`is` / `is not equal to` which work on any values.
