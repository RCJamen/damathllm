import time

d = {"0":[(), (36,45), (), ()],
     "1":[11]}


time.sleep(5)

a = [
    [i, x]
    for i, dest_list in d.items()       # for each key and its list
    for dest in dest_list               #   for each element in that list
    if dest                              #   skip empty tuples ()
    for x in (dest                       #   if it's a tuple, iterate its contents
               if isinstance(dest, tuple)
             else [dest])               #   otherwise treat it as a single‑item list
]

print(a)
# → [['0', 36], ['0', 45], ['1', 11]]
