-- functions.e — defining and using functions
-- Demonstrates: function definitions, parameters, return values, recursion

-- A simple greeting function
to greet name
    say "Hello, " , name , "!"
end

-- A function that returns a value
to square x
    return x times x
end

-- A function with multiple parameters
to add a b
    return a plus b
end

-- A recursive function
to factorial n
    if n is less than 2 then
        return 1
    end
    return n times factorial(n minus 1)
end

-- Let's use them!
greet "Alice"
greet "Bob"

say "5 squared is " , square 5
say "3 plus 4 is " , add 3, 4
say "5! (factorial) is " , factorial 5
