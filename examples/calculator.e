-- calculator.e — interactive calculator using math and comparisons
-- Demonstrates: variables, math, comparisons, input, output

let first be number(ask "Enter first number: ")
let op be ask "Enter operator (plus, minus, times, divided by): "
let second be number(ask "Enter second number: ")

let result be 0
if op is "plus" then
    let result be first plus second
else if op is "minus" then
    let result be first minus second
else if op is "times" then
    let result be first times second
else if op is "divided by" then
    let result be first divided by second
else
    say "I don't know that operator: " , op
end

say first , " " , op , " " , second , " = " , result
