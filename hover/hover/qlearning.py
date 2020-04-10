import numpy as np
import torch as T

import hover as H


class Model(T.nn.Module):
    def __init__(self, hidden_size, output_size):
        super().__init__()
        self.in_features = T.nn.Linear(H.State.DATA_SIZE, hidden_size)
        d = .2 * (self.in_features.in_features) ** -.5
        T.nn.init.uniform_(self.in_features.weight, -d, d)
        self.predict = T.nn.Linear(hidden_size, output_size)

    def forward(self, x):
        h = T.relu(self.in_features(x))
        return self.predict(h)


class Agent:
    ACTIONS = [(False, False), (False, True), (True, False), (True, True)]

    def __init__(self):
        # Fixed state (settings)
        self.discount = .95
        self.alive_reward = .5 * (1-self.discount)
        self.greed = .9
        self.qsteps = 5
        self.max_buffer = 10000
        self.update_sample = 100

        # Transient state
        self.model = Model(100, len(self.ACTIONS))
        self.opt = T.optim.Adam(self.model.parameters())
        self.random = np.random.RandomState()
        self.buffer = []
        self.pre_buffer = []

    def _update(self, log):
        if self.update_sample <= len(self.buffer):
            self.opt.zero_grad()
            indices = self.random.randint(0, len(self.buffer), self.update_sample)
            states = T.FloatTensor([self.buffer[idx][0] for idx in indices])
            actions = T.LongTensor([self.buffer[idx][1] for idx in indices])
            rewards = T.FloatTensor([self.buffer[idx][2] for idx in indices])

            y = self.model(states)[T.arange(self.update_sample), actions]
            loss = (1 - self.discount) * ((y - rewards) ** 2).mean()
            log.append('loss', loss=float(loss))
            loss.backward()
            self.opt.step()

    def _act(self, state, greedy):
        if greedy or self.random.rand() < self.greed:
            return int(T.argmax(self.model(T.FloatTensor(state.data))))
        else:
            return self.random.randint(len(self.ACTIONS))

    def _add_memory(self, state, action, reward, log):
        if self.qsteps == len(self.pre_buffer):
            sar = self.pre_buffer.pop(0)
            sar[2] += (self.discount ** self.qsteps) * float(T.max(self.model(T.FloatTensor(state.data))))
            self.buffer.append(sar)
        self.pre_buffer.append([state.data, action, 0])
        for n in range(len(self.pre_buffer)):
            self.pre_buffer[-1 - n][2] += reward * (self.discount ** n)
        self._update(log)

    def _flush_and_trim_buffer(self):
        self.buffer += self.pre_buffer
        self.pre_buffer = []
        self.buffer = self.buffer[-self.max_buffer:]

    def _get_reward(self, state):
        if state.outcome == state.Outcome.Success:
            return 1
        if state.outcome == state.Outcome.Continue:
            return self.alive_reward
        return 0

    def train(self, log):
        """Train the agent on a single game."""
        runner = H.Runner(None, [1])
        state = runner.state()
        while True:
            action = self._act(state, greedy=False)
            runner.step(self.ACTIONS[action])
            new_state = runner.state()
            self._add_memory(state, action, self._get_reward(new_state), log)
            if new_state.outcome != new_state.Outcome.Continue:
                self._flush_and_trim_buffer()
                log.append('outcome', outcome=str(new_state.outcome), elapsed=new_state.elapsed)
                return
            state = new_state

    def __call__(self, state):
        """Evaluation policy - greedy as anything."""
        return self.ACTIONS[self._act(state, greedy=True)]
