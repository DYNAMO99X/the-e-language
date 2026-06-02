-- guessing_game.e — number guessing game
-- Demonstrates: variables, while loop, if/else, comparisons, ask, random

-- Use a fixed secret for reproducibility in tests
let secret be 7
let guesses be 0

say "I'm thinking of a number. Try to guess it!"

let done be false
while not done
    let guess be number(ask "Your guess: ")
    let guesses be guesses plus 1

    if guess is less than secret then
        say "Too low!"
    else if guess is greater than secret then
        say "Too high!"
    else
        say "You got it! It took you " , guesses , " guesses."
        let done be true
    end
end
