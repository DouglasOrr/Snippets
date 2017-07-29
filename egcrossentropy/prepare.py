import os
import subprocess

os.makedirs('data')

subprocess.check_call(
    "wget http://www.gutenberg.org/cache/epub/1661/pg1661.txt"
    " -O data/sherlock.txt",
    shell=True)

with open('data/sherlock.txt') as src:
    # Skip to "Adventure I."
    while not next(src).startswith("ADVENTURE I"):
        pass

    # Read until "XII."
    with open('data/sherlock_begin.txt', 'w') as dest:
        while True:
            line = next(src)
            if line.startswith("XII."):
                break
            dest.write(line)

    # Read until "End of the Project Gutenberg EBook"
    with open('data/sherlock_end.txt', 'w') as dest:
        while True:
            line = next(src)
            if line.startswith("End of the Project Gutenberg EBook"):
                break
            dest.write(line)
