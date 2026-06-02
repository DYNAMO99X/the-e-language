let inventory be [  ]
let won be false
let current_room be "start"
let moves be 0

to describe room
    if room is equal to "start" then
        say ""
        say "=== The Locked Room ==="
        say "You are in a small stone room. There's a wooden door to the north."
        say "On the floor, you see a small brass key."
    else
        if room is equal to "hallway" then
            say ""
            say "=== The Hallway ==="
            say "A long hallway stretches north. Torches flicker on the walls."
            say "There's a locked door to the south (back to the start room)."
        else
            if room is equal to "outside" then
                say ""
                say "=== Outside ==="
                say "You step out into the sunshine. Birds are singing."
                say "You are free!"
            end
        end
    end
end

to has_key items
    let i be 0
    let found be false
    repeat (size of items) times
        if (items at i) is equal to "key" then
            let found be true
        end
        let i be i plus 1
    end
    return found
end

while won is false
    describe current_room

    say ""
    say "Commands: look, take key, go north, go south, inventory, quit"
    let command be ask "> "

    if command is equal to "look" then
        describe current_room
    else
        if command is equal to "take key" then
            if current_room is equal to "start" then
                let inventory be inventory with "key" added
                say "You picked up the brass key."
            else
                say "There's no key here."
            end
        else
            if command is equal to "go north" then
                if current_room is equal to "start" then
                    if has_key inventory then
                        say "You unlock the door and step through."
                        let current_room be "hallway"
                    else
                        say "The door is locked. You need a key."
                    end
                else
                    if current_room is equal to "hallway" then
                        let current_room be "outside"
                        let won be true
                    end
                end
            else
                if command is equal to "go south" then
                    if current_room is equal to "hallway" then
                        let current_room be "start"
                    else
                        say "You can't go that way."
                    end
                else
                    if command is equal to "inventory" then
                        if (size of inventory) is 0 then
                            say "You are carrying nothing."
                        else
                            say "You are carrying:"
                            let i be 0
                            repeat (size of inventory) times
                                say "  * " , (inventory at i)
                                let i be i plus 1
                            end
                        end
                    else
                        if command is equal to "quit" then
                            say "Goodbye!"
                            let won be true
                        else
                            say "I don't understand '" , command , "'. Try: look, take key, go north, go south, inventory, quit"
                        end
                    end
                end
            end
        end
    end

    if command is not equal to "quit" then
        let moves be moves plus 1
    end
end

if current_room is equal to "outside" then
    say "You escaped in " , moves , " moves. Well done!"
end
