# Balance

A very basic _Machine Learning & Clojure_ coding Dojo starter kit, for implementing & training 'ball balancing' AI controllers.


## Setup

### Eclipse

To get started with Eclipse, we recommend the [CounterClockwise](https://code.google.com/p/counterclockwise/)
plugin for working with Clojure.

 - Help > Install New Software > Work with: `http://updatesite.ccw-ide.org/stable/` (0.23.0 at time of writing)
   - click through & accept license, restart as prompted
 - File > Import > Existing Projects into Workspace > Select root directory: > Browse > Select "Balance" > Finish
 - Open `src/balance/control.clj` & press `Ctrl+Alt+S` (or Clojure > Load file in REPL)

### Emacs

To get started with Emacs (24), we recommend [nrepl](https://github.com/clojure/tools.nrepl)

 - `M-x package-list-packages`
   - find `nrepl` (0.2.0 at time of writing)
   - type `i` to mark for installation, `x` to install
 - `C-c M-j` when viewing a file to start up

### Command line

Install [Leiningen](https://github.com/technomancy/leiningen#installation), and execute `lein run`. To run the tests, execute `lein midje`.


## Writing a controller

The objective is to write a controller for a simple physical system where a stick is to be balanced upright, in a position of unstable [equilibrium](http://en.wikipedia.org/wiki/Mechanical_equilibrium). Controllers can be attached to the system either in a live visual simulation window, or without visual output, as follows:

    (def my-controller (constantly 0))                      ;; isn't going to win any prizes!
    (balance.view/start! balance.core/task-1 my-controller) ;; real-time, visual simulation
    (balance.view/stop!)
    (->> (balance.core/simulate balance.core/task-1 my-controller)
         (take 100)
         (map :dynamic-state))                              ;; 100 steps of offline simulation

Controllers may fit into one of three rough categories: _ideal_, _adaptive_ or _general_, briefly described as follows.

### Ideal

_Ideal_ controllers are permitted to know (almost) anything about the control task being solved, including starting state, maximum controller torque and the physical characteristics of the system (moment of inertia, center of mass and damping factor). From this it should be possible to do a very good job of controlling the system, in order to optimize or trade off objectives such as minimum control input or duration, or minimum energy input. The controller may use some combination of mathematical modelling for exact or approximate solutions to the objective, and heuristics.

### Adaptive

_Adaptive_ controllers are permitted to know the general form of control function (or type of the physical system), but exactly the same starting conditions and procedure should be applicable to solve a variety of tasks (often involving an initial learning phase). In other words, there should be no knowledge of the actual parameters of the dynamic system being controlled. Any applicable learning algorithm may be used on a single controller or a population of multiple controllers during the training phase, before a single controller is selected for evaluation. For example, an adaptive system may be generated from an ideal controller by removing knowledge of the actual parameters, and instead learning the controller parameters using an appropriate learning algorithm.

### General

_General_ controllers should be able to solve a broader family of control tasks, so must assume little about the problem being solved (although they are of course permitted to have knowledge of the objective/goal). The same controller could in principle be applied to a control problem with significantly different dynamics, and find a solution. In practise it is likely that the implementation must make some assumptions, such as the dimensionality of the control output, and the number and type of objectives (e.g. in this example, a 1-dimensional input/error with provided time derivative, and 1-dimensional output). Like _adaptive_ controllers, _general_ controllers usually require a training phase, which is used to adapt to the dynamics of the system being controlled.
