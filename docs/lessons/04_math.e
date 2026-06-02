say "Tip calculator!"
say ""

let bill be ask "How much was the bill? "
let bill_num be number bill

let tip be bill_num times 15 divided by 100
let total be bill_num plus tip

say "15% tip is " , tip
say "Total: " , total
say ""

let half be bill_num divided by 2
say "Split with one friend: " , half , " each"
