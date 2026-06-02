-- fibonacci.e — generate a list of fibonacci numbers
-- Demonstrates: lists, for-each loop, function recursion, return values, index

-- Build a list of the first N fibonacci numbers
to fiblist count
    let result be []
    let a be 0
    let b be 1
    repeat count times
        let result be result with a added
        let next be a plus b
        let a be b
        let b be next
    end
    return result
end

-- A recursive fibonacci (single value)
to fib n
    if n is less than 2 then
        return n
    end
    return fib(n minus 1) plus fib(n minus 2)
end

-- Print the first 10 fib numbers using the list
let fibs be fiblist 10
say "First 10 fibonacci numbers:"
for each num in fibs
    say num
end

-- Also show fib(10)
say "fib(10) = " , fib 10

-- Show the size of the list
say "Generated " , size of fibs , " numbers"
