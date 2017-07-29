import click
import math
import string
import logging
from collections import defaultdict


def line_surprise(model, line, char_domain=string.printable):
    """Calculate the surprise of observing a line under the given
    character-from-prefix model.
    Ignores characters that aren't in char_domain.
    """
    surprise = 0
    for i, char in enumerate(line):
        if char in char_domain:
            surprise -= math.log(model.conditional_probability(line[:i], char),
                                 2)
    return surprise


class Model:
    """Base for models of lines of text (we trust them to be honest probability
    distributions over the domain of allowed characters).
    """
    def conditional_probability(self, prefix, char):
        raise NotImplementedError(
            "Submodels should implement 'conditional_probability'")


class InterpolationModel(Model):
    def __init__(self, *models_and_weights):
        norm = sum(weight for _, weight in models_and_weights)
        self.models_and_probs = [
            (model, weight / norm)
            for model, weight in models_and_weights
        ]

    def conditional_probability(self, prefix, char):
        return sum(prob * model.conditional_probability(prefix, char)
                   for model, prob in self.models_and_weights)


class NgramModel(Model):
    def __init__(self, order, alpha, char_domain=string.printable):
        self.order = order
        self.char_domain = char_domain
        initial_dict = {ch: alpha for ch in char_domain}
        self.contexts = defaultdict(lambda: initial_dict.copy())

    def get_contexts(self, prefix):
        for n in range(self.order - 1, 0, -1):
            yield prefix[-n:]
        yield ''

    def train(self, line):
        """Update the ngram model given this line.
        """
        for i, char in enumerate(line):
            if char in self.char_domain:
                for context in self.get_contexts(line[:i]):
                    self.contexts[context][char] += 1

    def conditional_probability(self, prefix, char):
        for context in self.get_contexts(prefix):
            if context in self.contexts:
                m = self.contexts[context]
                return m[char] / sum(m.values())


@click.command()
@click.argument('train_data', type=click.File('r'))
@click.argument('test_data', type=click.File('r'))
@click.option('-v', '--verbose', is_flag=True)
@click.option('-o', '--order', type=int, default=1)
@click.option('-a', '--alpha', type=float, default=0.01)
@click.option('-p', '--pretty', is_flag=True)
def run(train_data, test_data, verbose, order, alpha, pretty):
    """Script for calculating the Cross Entropy (expected surprise) of
    one file, given the data of another, using character modelling.
    """
    logging.basicConfig(
        format='%(levelname)s %(message)s',
        level=logging.DEBUG if verbose else logging.INFO
    )

    def preprocess(line):
        return line.rstrip('\n')

    # 1. Train
    ngram_model = NgramModel(order=order, alpha=alpha)
    for line in train_data:
        ngram_model.train(preprocess(line))

    # 2. Print debug info
    s = 0
    for ch in string.printable:
        p = ngram_model.conditional_probability("", ch)
        logging.debug("%r: %.3f" % (ch, p))
        s += p
    logging.debug("Total: %.2f" % s)

    # 3. Calculate surprise
    total_surprise = 0
    nlines = 0
    nchars = 0
    test_lines = list(map(preprocess, test_data))
    for line in test_lines:
        total_surprise += line_surprise(ngram_model, preprocess(line))
        nlines += 1
        nchars += len(line)
    logging.info("   Total surprise: %.3g" % total_surprise)
    logging.info("Surprise per line: %.3g" % (total_surprise / nlines))
    logging.info("Surprise per char: %.3g" % (total_surprise / nchars))

    if pretty:
        # print the text out with ASCII colour codes
        deadzone = 0.3
        average_surprise = total_surprise / nchars
        high_surprise = average_surprise * (1 + deadzone)
        low_surprise = average_surprise * (1 - deadzone)
        for line in test_lines:
            pretty_line = ''
            for i, char in enumerate(line):
                if char in ngram_model.char_domain:
                    surprise = -math.log(
                        ngram_model.conditional_probability(line[:i], char)
                    )
                    if surprise < low_surprise:
                        pretty_line += click.style(char, fg='green')
                    elif high_surprise < surprise:
                        pretty_line += click.style(char, fg='red')
                    else:
                        pretty_line += char
                else:
                    pretty_line += char
            print(pretty_line)
    else:
        print(surprise)

if __name__ == '__main__':
    run()
