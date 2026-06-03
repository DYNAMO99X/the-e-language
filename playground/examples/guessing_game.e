-- Number guessing game
let secret be random 1, 100
let guesses be 0
let won be false

say "I'm thinking of a number between 1 and 100."

while won is not true
    let guess be ask "Your guess? "
    let num be number guess
    let guesses be guesses plus 1

    if num is less than secret then
        say "Too low!"
    else if num is greater than secret then
        say "Too high!"
    else
        say "You got it in " , guesses , " guesses!"
        let won be true
    end
end
