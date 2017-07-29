# Entropy investigation

Measure the cross-entropy of various character models for the end of Sherlock Holmes' Adventures, given the beginning.

For example:

    python3 prepare.py
    python3 entropy.py data/sherlock_begin.txt data/sherlock_end.txt -p -o 4 | aha > data/out.html
