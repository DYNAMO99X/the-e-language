let friends be [ "Alice" , "Bob" , "Charlie" ]
say "I have " , (size of friends) , " friends."

say friends at 0
say friends at 1
say friends at 2

let pets be [ "dog" , "cat" , "fish" ]
let pets be pets with "hamster" added
let pets be pets with "parrot" added

say "All my pets:"
let i be 0
repeat (size of pets) times
    say "  " , (pets at i)
    let i be i plus 1
end
