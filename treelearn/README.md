# TreeLearn

TreeLearn is a simple learning algorithm which combines Stochastic Gradient Descent (SGD) with Evolutionary Algorithms (EA).
It is designed to train deep learning systems, forming an alternative to hyperparameter optimizers.

## Goals

**Continuous training**

I'm trying to solve a problem, and am going to keep training even if I...
 - update the code
 - change initialization strategy
 - change network architecture
 - leave my computer(s) alone for 3 months

**Reproducability**

Since my training run will certainly be highly unique - I would like to have some guarantee
that I could reproduce the best models without spending so much time.

**Optimality**

I don't want to throw away any information that might help find an optimum, even if our heuristics
aren't great now, maybe one day they'll be better.

## System design

At its most basic, the system must have:
 - the _problem_
   - _initializer_ (creates randomly initialized, or mutated models)
   - _stepper_ (attempts to improve a model, based on some training data - runs an epoch)
   - _evaluator_ (evaluates a trained model on a validation set)
 - the _optimizer_
   - _database_ (a cache of results from the evaluator)
   - _archive_ (a cache of trained models)
   - _proposer_ (the core of the system)
   - _interface_ (to control the proposer)
