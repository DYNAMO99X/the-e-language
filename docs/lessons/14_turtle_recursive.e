to draw_tree ada depth length
    if depth is 0 then
        return
    end
    set ada pen color to "brown"
    move ada forward length

    move ada left 30
    draw_tree ada, (depth minus 1), (length times 0.7)

    move ada right 60
    draw_tree ada, (depth minus 1), (length times 0.7)

    move ada left 30
    move ada backward length
end

let ada be turtle
move ada left 90
move ada backward 100
draw_tree ada, 8, 80

say "Tree complete."

to draw_spiral bob length angle
    if length is less than 5 then
        return
    end
    set bob pen color to "blue"
    move bob forward length
    move bob right angle
    draw_spiral bob, (length times 0.95), angle
end

let bob be turtle
move bob left 90
move bob backward 50
draw_spiral bob, 100, 91
say "Spiral complete."
