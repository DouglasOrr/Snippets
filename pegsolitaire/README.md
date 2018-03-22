# Brute force solver for "peg solitaire"

Solve [peg solitaire](https://en.wikipedia.org/wiki/Peg_solitaire) by performing a brute force search, and exploiting lots of symmetry.

The brute force search visits every possible game state from the starting position in a tree, in a bread-first search, except for a few symmetries:

 - reflection - the game has four reflective symmetries
   - `x=0`, `y=0`, `x=y`, `x=-y`
 - rotation - the game has two rotation symmetries, which can be combined with reflection
   - `0`, `pi/2`
 - time (most importantly) - if you transform a game by inverting every piece & reversing the order of moves, you have a valid game
   - therefore we can explore half a game tree, then invert it and hash-join against itself, to find possible endgames

Exploiting these symmetries brings down the number of states such that it can be explored in a few minutes on a modern laptop.

## Running

This project requires Docker - the following commands build the image & native numpy extension, then run tests, the demo program & start a network to explore interactively.

    ./scripts/build
    ./scripts/test
    ./scripts/run
    ./scripts/notebook
