# Scientific papers notes

Note that all of the following are my own take on the paper, and may represent a misunderstanding or misrepresentation - read with caution...


**Sensitivity and Generalization in Neural Networks: An Empirical Study**

- Date revised: 2018-02-23
- Date read: 2018-04-23
- Link: https://arxiv.org/abs/1802.08760
- Topics: deep learning, generalization

This paper acknowleges an odd property of deep learning models - they don't fit the expected pattern of more parameters leading to greater expressivity, but weaker generalization (more overfitting). The paper therefore argues for measuring _sensitivity to input_ as a better proxy metric to understand generalization, rather than simply counting parameters. To do this, they introduce two simple metrics for measuring sensitivity. Their analysis is restricted to piecewise linear networks (RELU or Hard Tanh/Sigmoid, etc.) The first metric is for linear segment gradient - a (Frobenius) norm of the Jacobian (which predicts the change in output for a small normally distributed input change). The second metric is for density of segment transitions (which is a measure of curvature of such a non-smooth function). Their results show that these metrics take the lowest value (least sensitive) in the training data space, then medium values in regions "close by" (e.g. interpolations between same-class MNIST digits), and the largest values for random points in the input domain. They then analyse how these metrics behave under experiment variations such as random labelling, data augmentation, choice of nonlinearity, and use of a full-batch optimizer. In particular, the gradient measure correlates with generalization gap. Overall, this shows that deep learning seems to train relatively low-gradient & smooth functions around the input domain, which helps it to generalize.

- Why might more parameters mean smoother & more linear functions in the data domain?
- Could similar analysis be perfomed with smooth nonlinearities such as tanh/elu?
- Could training with hard (value) discontinuities perform better?
  - Making it easier to "transition values" in regions outside the data space.
- Is this (low input sensitivity) the cause or the effect of good generalization?


**Massively Parallel A\* Search on a GPU**

- Date revised: 2015
- Date read: 2018-04-21
- Link: http://iiis.tsinghua.edu.cn/~compbio/papers/aaai_2015.pdf
- Topics: GPGPU, search, parallelism

Introduces a parallel search for implementation on GPU, minimizing data dependencies to exploit the massive data parallelism of GPUs. The core idea is to allocate many priority queues for nodes to explore (thousands), and let each GPU thread explore a new state from each queue. This means that the parallel search will typically explore many more states than the sequential search, however it is worth it to weaken the data dependency & parallelize. Also describes data structures for efficient parallel duplication detection (hash sets), based on _cuckoo hashing_ and _parallel hashing with replacement_ (where contention for a hash bucket is resolved by replacing the old with the new). The results show a large speedup compared to a single-thread CPU algorithm, particularly where the trivially parallel work of computing heuristic functions is expensive.

- Compare against an existing SIMD CPU A* search?
- Compare against a CPU implementation of the same scheme?
- Could block-level coordination be used to efficiently distribute good solutions amongst priority queues?
  - Or is a random assignment likely to be "good enough"?


**TrueSkill 2: An improved Bayesian skill rating system**

- Date revised: 2018-03-22
- Date read: 2018-04-20
- Link: https://www.microsoft.com/en-us/research/uploads/prod/2018/03/trueskill2.pdf
- Topics: bayesian, gaming, ranking, matchmaking

Extends TrueSkill with some very practical improvements, while seeking the keep the model as simple as possible. First, describes online & batch updates, showing the greatly improved stability & convergence speed of computing skill updates in a batch. Second, makes the model parameters trainable using _expectation propagation_ with point MAP estimates of the trainable parameters (using point estimates improves memory & compute usage during training), updating using Rprop. The third improvement is to the model itself, which they perform by an approach called _metric driven modelling_. They seek to keep the model as simple as possible, but add components to the model to deal with particular high-bias failures of the model (identified by measuring metrics that show some important structure the model is failing to capture). For example, to address the fact that players that intentionally self-organize into _squads_ might over-perform, they compare win rate stats for different squad sizes to those predicted by their model. Since there is a correlation that is not picked up by the model, they add an additional component into the model (in this case a simple additive player performance bonus based on squad size). In the same way, they describe _experience_ effects (another offset based on number of games played), _individual stats_ (additional stats that can be generated from the model, such as kill & death counts) & a _quit penalty_ for failing to complete a game. They pragmatically only add features that are needed to explain the data, which seems a very sensible approach!

- Could distributions be non-Gaussian?
  - E.g. Generation of performance from skill could be heavy-tailed
- Is there a way to search through possible structure in the data, rather than manually generating hypotheses?
  - Maybe this wouldn't efficiently find "interaction structure" (as a person needs to generate the hypothesis & query the data in an appropriate way)?
- Could a similar process of metric-driven modelling be appled to supervised deep learning models?
  - Does it require an interpretable model?
  - Could it be applied to choose inputs to a model?
- Would it be possible to better formalize the "no bad incentives" constraint (that they rightly place upon the skill model)?


**TrueSkill(TM): A Bayesian Skill Rating System**

- Date revised: 2007-01-01
- Date read: 2018-04-19
- Link: https://www.microsoft.com/en-us/research/wp-content/uploads/2007/01/NIPS2006_0688.pdf
- Topics: bayesian, gaming, ranking, matchmaking

Extends the statistical mechanism behind ELO rating calculation to work in ranked team games (rather than winner-takes-all solo games). To do this, builds a Bayesian model for the unknown variables _skill_ & _performance_. Skill is a slowly-changing underlying characteristic of a player, which defines a distribution of possible performances. Player performance is a number which represents a single player's actual contribution towards success in a given game (and is drawn based on skill). Team performance is simply the sum of individual performances on that team. This is a very simple, very linear, model in which every prior, posterior & marginal is a Gaussian (the approximate learning scheme is called _Gaussian density filtering_, and inference can be run using very efficient message passing.) The learning scheme is adapted quite simply to allow skills to vary over time, which (unsurprisingly) corresponds to adding variance to the prior for skill. The model is simple, interpretable, and out-performs ELO in a variety of tests (it is somewhat like ELO with an extra layer of latent variables, which gives it more explanatory power as a model over the games it observes). It is very efficient to run, and was deployed for matchmaking in Xbox Live.

 - What is the biggest limiting assumption?
   - What if the 'combiner' operation for calculating team performance from player performance wasn't linear?
   - What if player performances weren't independently drawn?
 - Could inference be done nearly as efficiently if distributions weren't Gaussian, or operations weren't linear?
 - What would be the drawback of developing/deploying a more complex, less interpretable, model?


**Curiosity-driven Exploration by Self-supervised Prediction**

- Date revised: 2017-05-15
- Date read: 2018-04-17
- Link: https://arxiv.org/abs/1705.05363
- Topics: deep learning, reinforcement learning, exploration

Tackles the problem of encoraging _intentional exploration_ in a _sparse reward_ setting, where the natural structure of the problem requires non-random exploration (there is not enough signal in the reward to guide the algorithm to the optimal policy). Traditional RL approaches with epsilon-greedy exploration are random walks until they find some signal from the reward. So this paper introduces an intrinsic reward for _curiosity_. They want to reward exploration of different states which influence the actor (they are not interested in states that can have no effect on the action-state interaction). To do this, they introduce a feature space, which is used both to classify the action taken (when comparing adjacent features) and to predict a subsequent set of features given starting features & the action taken. The error from this prediction model is the intrinsic curiosity reward. Put simply, if the transition in an abstracted feature space is hard to predict, the agent should receive a reward. They show that adding this reward does indeed improve the time to solution for an A3C-trained agent, particularly with sparse rewards.

 - Could this be done separately from the "reward-seeking policy" with an "exploration policy"?
   - It seems slightly odd to train a network to maximize the intrinsic reward, rather than having some separate search for optimal exploration actions.
   - Could another type of search be used on top of the trained models for optimizing actions for curiosity?
   - Perhaps the next-features uncertainty could be modeled explicitly, rather than rewarded & then optimized along with the rest of the policy?
 - Is the balance of losses (next-features-prediction & action-classification) on the feature space sensitive? (As they seem somewhat adversarial.)


**Investigating Human Priors for Playing Video Games**

- Date revised: 2018-02-15
- Date read: 2018-04-17
- Link: https://arxiv.org/abs/1802.10217
- Topics: deep learning, reinforcement learning, priors

Uses human trials to evaluate the importance of different _priors_ that people make use of when solving a new task (a video game), which allow them to learn games much more rapidly than current reinforcement learning algorithms. One of many simplifications made by RL is to start with zero knowledge (or a very weak spatial prior from a convolutional layer), and learn from scratch for each new task. Clearly this isn't how people approach a new task. By confounding the various priors that might help a person learn how to solve a new task, the paper tries to assign importance to different priors. They identify a priority order: first visual similarity of similar objects, second affordances that indicate the semantics of an object, then the particular interactions between objects that you would expect.

 - It is great to see the problem of sample efficiency identified & worked on - what's next in this very important area?
 - What else is missing, as this seems to account for an order of magnitude (in terms of number experiences needed to solve the task) in their examples, yet RL is maybe still 1-2 orders of magnitude out?
   - Are there still priors that are being used?
   - Possibly more structural or "problem solving" priors?
     - Is there a fundamental difference between a prior & a learning algorithm, or are they part of the same thing?
 - Can we learn such priors (by sharing them between tasks), rather than either starting from scratch, or trying to encode the priors manually?


**On the Optimization of Deep Networks: Implicit Acceleration by Overparameterization**

- Date revised: 2018-02-19
- Date read: 2018-03-19
- Link: https://arxiv.org/abs/1802.06509
- Topics: deep learning, optimization

Adding depth to a linear network, which doesn't change the expressiveness of the network, would (by conventional wisdom) seem to make it harder to optimize. But this paper shows that it creates interesting training dynamics, with terms that appear momentum-like & adaptive-gradient-like. While the adaptive gradient & momentum terms are different from the hand-rolled heuristics of Adagrad & Adam, it is interesting that this class of behaviour emerges naturally from increasing depth. In other words, the dynamics of a deep linear network seem more "integration-like" (which is momentum), which might make it easier to optimize in some cases.

- Could this be simply applied to speed up training e.g. splitting linear layers in two (there need be no penalty at inference time)?
- How closely does this apply for deep nonlinear networks?
- Does this integration-like behaviour create instability in deeper networks?


**Expressive Power of Recurrent Neural Networks**

- Date revised: 2018-02-07
- Date read: 2018-03-19
- Link: https://arxiv.org/abs/1711.00811
- Topics: deep learning, linear algebra

Analyses the expressive power of what seems to be a "bilinear multiplicative recurrent network" (which they call a Tensor-Train (TT)-network). A random instance of a TT-network is exponentially hard to represent with a Candecomp/Parafac (CP)-network (which is a class of shallow network), and similar in power to a Hierarchical Tucker (HT)-network (which is a class of convolutional network).

- Could a bilinear RNN + nonlinearity work in practice, or would it suffer from vanishing gradients?
  - Could this be combined with a passthrough "cell", such as a GRU/LSTM/RHN?
- How well does this sort of decomposition model time-varying processes (as commonly deployed)?
