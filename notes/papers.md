# Scientific papers notes

Note that all of the following are my own take on the paper, and may represent a misunderstanding or misrepresentation - read with caution...


**Investigating Human Priors for Playing Video Games**

- Date revised: 2018-02-15
- Date read: 2018-04-17
- Link: https://arxiv.org/abs/1802.10217
- Topics: deep learning, reinforcement learning

Uses human trials to evaluate the importance of different priors that people make use of when solving a new task (a video game), which allow them to learn games much more rapidly than current reinforcement learning algorithms. One of many simplifications made by RL is to start with zero knowledge (or a very weak spatial prior from a convolutional layer), and learn from scratch for each new task. Clearly this isn't how people approach a new task. By confounding the various priors that might help a person learn how to solve a new task, the paper tries to assign importance to different priors. They identify first visual similarity of similar objects, then affordances that indicate the semantics of an object, then the particular interactions between objects that you would expect.

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
