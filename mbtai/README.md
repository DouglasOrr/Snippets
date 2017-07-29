# MbtAI

Simple tank AI game, designed to let me have a little fun with Machine Learning, Reinforcement Learning, etc. (As well as making a game that is fun to play.)

MbtAI is a human and computer-playable action/strategy game where you maneuver a tank in a simple environment, collect ammunition, and destroy the other tank(s).


## Getting started

You'll need Docker & docker-compose...

    docker-compose build
    docker-compose up server
    # now look at http://localhost:5000


## Architecture

MbtAI consists of:

 - a server component, in Python, which implements the game rules,
 - a thin web client, in Javascript, implementing visuals and human control,
 - one or more AIs, in any language but preferably Python or C++.


## The game

A game of MBTAI has 2+ tanks, organized into 2+ teams. The goal of a team of tanks is to take out every other team - last team standing wins (maybe other objectives could be added in the future.

The tanks obey a simple movement model - colloqially, they can move forward quickly, traverse (rotate) slowly, traverse turret slowly, and reverse slowly.

The core of the game is designed to allow:

 - efficient accelerated play (e.g. between multiple AIs)
 - real-time play with the web client connected, and detailed logging (to collect training data)
