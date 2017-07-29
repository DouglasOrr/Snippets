# Train a network to learn the XOR function

### Data & config ###

training_data = [([0, 0], 0),
                 ([0, 1], 1),
                 ([1, 0], 1),
                 ([1, 1], 0)]
learning_rate = 0.5
initial_scale = 0.1
nhidden = 3

import theano
import theano.tensor as T
import theano.tensor.nnet as nnet
import numpy.random as rng
from numpy import asarray

### Network ###

# Hand-tuned weights
# w0 = theano.shared(asarray([[1.0, 1.0],[-1.5, -1.5]]), 'w0')
# b0 = theano.shared(asarray([-1.5, 1.0]), 'b0')
# w1 = theano.shared(asarray([-1.5, -1.5]), 'w1')
# b1 = theano.shared(1.0, 'b1')

# Random weights
w0 = theano.shared(initial_scale * rng.randn(nhidden, 2), 'w0')
b0 = theano.shared(initial_scale * rng.randn(nhidden), 'b0')
w1 = theano.shared(initial_scale * rng.randn(nhidden), 'w1')
b1 = theano.shared(initial_scale * rng.randn(), 'b1')

# Net
x0 = T.fvector('x0')
yt = T.fvector('yt')
x1 = nnet.sigmoid(T.dot(w0, x0) + b0)
x2 = nnet.sigmoid(T.dot(w1, x1) + b1)
error = nnet.binary_crossentropy(x2, yt).mean()
grad_w0, grad_b0, grad_w1, grad_b1 = T.grad(error, [w0, b0, w1, b1])

predict = theano.function(inputs=[x0], outputs=x2)
train = theano.function(inputs=[x0, yt],
                        outputs=[x2, error],
                        updates=((w0, w0 - learning_rate * grad_w0), (b0, b0 - learning_rate * grad_b0),
                                 (w1, w1 - learning_rate * grad_w1), (b1, b1 - learning_rate * grad_b1)))

### Training loop ###

print("Predict:")
for (xd,yd) in training_data:
    print("\t%r -> %f" % (xd, predict(xd)))

print("Train:")
for __ in range(1000):
    for (xd,yd) in training_data:
        yp, ep = train(xd, [yd])
        print("\t%r -> %f (pred %f, err %f)" % (xd, yd, yp, ep))

print("Predict:")
for (xd,yd) in training_data:
    print("\t%r -> %f" % (xd, predict(xd)))
