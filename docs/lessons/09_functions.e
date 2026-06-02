to greet name
    say "Hello, " , name , "!"
end

greet "Alice"
greet "Bob"
greet "Charlie"

say ""

to square n
    let result be n times n
    return result
end

let x be square 5
say "5 squared is " , x

let y be square (3 plus 2)
say "(3+2) squared is " , y
