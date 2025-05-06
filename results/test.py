d = {"0":[(), (36,45), (), ()],
     "1":[11]}

a = [
    [index, x]
    for index, dest_list in d.items()           # for each key and its list
    for dest in dest_list                       #   for each element in that list
    for x in (dest if isinstance(dest, tuple)    #     if it’s a tuple, iterate its contents…
               else [dest])                     #     otherwise treat it as a 1‑element list
    if x is not ()                              #     (optional) filter out any “empty” values
]

print(a)
# [['0', 36], ['0', 45], ['1', 11]]
