-- Fibonacci sequence
to fibonacci n
    if n <= 1 then
        return n
    end
    return fibonacci (n minus 1) plus fibonacci (n minus 2)
end

say "First 10 Fibonacci numbers:"
repeat 10 times
    let i be repeat count
    say fibonacci i
end
