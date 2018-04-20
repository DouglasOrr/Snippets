# Scientific papers notes

Note that all of the following are my own take on the paper, and may represent a misunderstanding or misrepresentation - read with caution...


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
