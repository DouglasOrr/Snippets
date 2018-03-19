# Scientific papers notes

Note that all of the following are my own take on the paper, and may represent a misunderstanding or misrepresentation - read with caution...

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
