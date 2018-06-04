# Scientific papers notes

Note that all of the following are my own take on the paper, and may represent a misunderstanding or misrepresentation - read with caution...

**Deep Learning with Differential Privacy**

- Date revised: 2016-10-24
- Date read: 2018-05-31
- Link: https://arxiv.org/abs/1607.00133
- Topics: deep learning, privacy

This paper employs _differential privacy_ to train a deep learning model, applying noise to the gradients used in parameter updates, and introducing a _moments privacy accountant_ which keeps track of the privacy guarantee provided. Colloquially, the differential privacy guarantee offered seems to be "the inclusion of a single datapoint cannot make an observable change in the probability of a derived classification of more than `exp^{epsilon} * probability_without_point + delta`" (the privacy guarantee being specified by _epsilon_ & _delta_). In the case of a continuous observation (the deep learning parameters), this can be achieved by adding Gaussian noise to the data as it is aggregated, in this case into the gradient updates. The accountant keeps track of how effectively the noise is protecting privacy, and provides upper bounds for (epsilon, delta) as training progresses. The moments accountant bound is computed using log moments of privacy loss, and provides a better bound on (epsilon, delta) than the strong composition theorem. To roll this into a training algorithm, there are two pieces - one performs gradient clipping on individual sample parameter gradients, and adds noise. The second keeps track of the privacy "spent" during training using the moments accountant (this provides auxilliary output, perhaps to be used for early stopping, and is not fed back into parameter updates). The paper makes a few observations from experiments - one that differential privacy noise causes generalization rather than overfitting (unsurprisingly, as an overfitted model is almost certainly violating D.P.) Counter-intuitively, larger batches are bad for differential privacy - more epochs can be run with small batches than large ones. In both MNIST & CIFAR-10 experiments there is a cost to employing differential privacy - a reduction in accuracy of the classifier.

- The technique seems very simple (additive Gaussian noise), but the analysis is hard!
  - However tracking per-example gradients (needed for clipping) is slightly awkward.
- How would this apply in other contexts?
  - Would this be scalable to language modelling (e.g. would sparse updates cause a problem)?
  - Does this assume that the output after every batch is public (which would seem pessimistic)?
  - I presume for a model with only public outputs (not public parameters) this could be cheaper?
- As noise is added independently to each parameter gradient, could there be correlations between parameter gradients that leak privacy?


**Deep Models Under the GAN: Information Leakage from Collaborative Deep Learning**

- Date revised: 2017-09-14
- Date read: 2018-05-28
- Link: https://arxiv.org/abs/1702.07464
- Topics: deep learning, collaborative learning, privacy

This paper describes & demonstrates an attack on _collaborative deep learning_, an approach that is intended to improve privacy, but might actually make it worse. In collaborative deep learning, participants train local models & share subsets of their parameters with the server, which are distributed to other participants. Their attack describes an _active participant attacker_, who uses a GAN to generate a "fake class" that is as close as possible to the class being attacked. This encourages the victim to reveal more and more information about the target class as training progresses, which is used to improve the GAN, which ends up generating very good samples from the target class. Others have proposed using _differential privacy_ (DP) on the parameter syncs to improve privacy, but the authors can demonstrate that this attack works even when differential privacy is enabled (as it just depends on is the ability of the model to distinguish between the fake class & the actual one - if you increase DP to remove this effect, you have suppressed any collaborative learning).

- Does this always leak a per-user-per-class distribution, or (if the parameter server aggregates uploads) does it only leak per-class distribution?
- Is it only the one-shot nature of centralized (trusted server) learning that protects it against this attack?
  - It seems that in any case where you have a chance to inject data & to perform multiple iterations, you could train such a GAN.
- Can we find a way to separate out "facts" or "propositions" about our data distributions that are protected by privacy guarantees, but otherwise maximally benefit from large-data ML?
  - It would be easy (although limited) to do this for manual feature engineering or selective data sharing, but are there other techniques?
  - Or are most markets largely satisfied with a trusted-server model?


**Routing Networks: Adaptive Selection of Non-linear Functions for Multi-Task Learning**

- Date revised: 2017-12-31
- Date read: 2018-05-21
- Link: https://arxiv.org/abs/1711.01239
- Topics: deep learning, multi-task, reinforcement learning

This paper introduces a flexible architecture for _multi-task learning_ (_MTL_), where routing networks select a sequence of computation _blocks_ (neural networks) to execute, given a one-of-many task label. In the proposed & best implementation tested, the routing networks define a stochastic policy which makes a hard decision of a single network to forward-propagate. The gradient update is then a modified version of _REINFORCE_, called the _Weighted Policy Learner_ (_WPL_), which appears to be simply the REINFORCE gradient, but scaled by `1 - action_probability`  or `action_probability`, depending on whether the reward is greater or less than the historical average reward (respectively). This is a dampening effect on oscilations (which helps when training against a nonstationary objective, such as this one).

- I'm a little unfamiliar with MTL, but it sounds like a interesting area with lots of possibilities.
- Tasks seem to be small & each multi-task scenario seems to inhabit a relatively restricted domain.
  - Is it possible to do multi-task learning across all the different settings in the paper (MNIST, imagenet, CIFAR-100)?
- Shouldn't the baseline for multi-task learning systems be (well-regularized) single task learners?
  - Is the goal of MTL to reduce training time, help generalization, or both?
- No form of _fairness_ regularization was needed to encourage diversity (maybe because the routing decision is actually quite easy)?
  - In fact, the opposite was used, which seems counter-intuitive.


**Deep Learning Scaling is Predictable, Empirically**

- Date revised: 2017-12-01
- Date read: 2018-05-20
- Link: https://arxiv.org/abs/1712.00409
- Topics: deep learning, model capacity, generalization

This paper uses a broad run of experiments across multiple domains to estimate how model performance scales with dataset size. They run the same hyperparameter search experiment for selected model architectures & optimizers for machine translation, language modelling, image classification & speech recognition. They measure _generalization error_ and _minimum optimal model size_ when the training set is restricted over a broad range, producing _learning curves_ for both (a learning curve here is distinct from our usual _training curve_ which measures a single model evolving over a training run, instead measuring scaling of given metrics for various dataset sizes). Their results show a stable pattern - a power law distribution for generalization error & minimum optimal model size. However the power law exponent for generalization is considerably smaller than that predicted by current theory (which would predict an exponent of -0.5 or -1.0): their experiments show exponents of -0.07 (language modelling) to -0.35 (image classification). This means the curve is flatter - increasing dataset size does not aid performance as much as our theory (under numerous assumptions) predicts, particularly for language modelling. The power law exponent for minimum optimal model size is typically larger (0.5 to 0.7), so optimal model size scales sublinearly with dataset size. They suggest that there are three regions in the learning curve for a problem: first, a _small data region_, where the error metric is defined by random guesswork, second a _power-law region_ (with a problem/dataset-specific exponent) as the dataset grows, then an _irreducible error region_ at which point the problem is "solved" as best it can, and increases in dataset size cease to help the model. They also suggest that architecture & optimizer choice tends to affect the intercept, rather than the exponent of the power law region. For language modelling in particular, it could be very beneficial if we could improve the exponent.

- Could a wider array of architecture choices actually affect the exponent? (E.g. shallow vs deep)
- Does the small data region really exist - or is this just a bad region for deep learning in particular?
  - Why should scaling be poor (a flatter curve) here?
  - It "feels" like Bayesian nonparametric methods could be powerful here.
- Could you ever prove that you're operating in the irreducible error region?
  - (You find an upper bound on it whenever you successfully train a model.)
- Language modelling scales badly, which is somewhat understood in the ngram world (a sparsity problem) - is this the same thing?
- Could we compare scaling on a given dataset (different objectives) to scaling on a different objective (same dataset) - which affects the exponent more?


**The Lottery Ticket Hypothesis: Training Pruned Neural Network Architectures**

- Date revised: 2018-04-23
- Date read: 2018-05-17
- Link: https://arxiv.org/abs/1803.03635
- Topics: deep learning, optimization, model capacity

This paper tests a very interesting idea - (roughly) that large deep learning models perform better than small models because they have an increased probability of having initialized _lucky subsets_ of the parameters which can fit the data & objective structure well. They test this by training a large network, then pruning weights to reduce the size, then resetting the pruned weights to the original (untrained) values, and retraining. Retraining these sparser lucky subsets or _winning tickets_ can achieve a similar performance to the large network with a fraction (often under 5%) of the parameters. This is a very interesting finding, as it suggests that the scale of neural networks isn't acting to constrain the _capacity_ of the network (the amount of complexity it can fit in), but instead helping the optimizer to find a good solution. This means that for train-freeze-infer scenarios (where inference might dominate the cost of deep learning), training larger networks then pruning them down to size could work to maximize efficiency. It also highlights the interesting interplay between optimization & model capacity - I would often try to separate them in my mind, but results like this show that they are strongly intertwined (so the ability of the model to fit the data isn't really relevant without also considering the ability of the optimizer & model combined to find a solution to fit the data).

- Most results seemed to prune weights, not units (which could hurt SIMD compute) - are similar results achievable by pruning entire units?
- Does this work for RNNs (I can see no reason why not)?
- Could these findings be used to design smarter initialization procedures?
  - Here, it might interact with transfer learning, to give us much faster training for new problems.
- More research needed in different ways to prune trained networks? (One-shot & iterative schemes are good, but maybe we could do more.)
- Could pruning in regular intervals be used to speed up training?


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
