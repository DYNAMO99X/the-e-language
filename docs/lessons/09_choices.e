let age be ask "How old are you? "
let age_num be number age

if age_num is greater than or equal to 18 then
    say "You are an adult."
else
    say "You are a kid."
end

say ""

let score be ask "What was your test score? "
let score_num be number score

if score_num is greater than 90 then
    say "Grade: A"
else
    if score_num is greater than 80 then
        say "Grade: B"
    else
        if score_num is greater than 70 then
            say "Grade: C"
        else
            say "Grade: F"
        end
    end
end
