import regex
import json
import sys


PATTERN = regex.compile(r'^(.+) ([^ ]+)\t(.*)$')
TOKENS = regex.compile(r'[\p{L}\']+|\p{P}')


with open('data/bsb.txt', errors='replace') as file_in, \
     open('data/bible.jsonl', 'w') as file_out:
    for line in file_in:
        m = PATTERN.match(line.replace('\ufffd', ' '))
        if not m:
            sys.stderr.write(f'Failed to match: {line}\n')
        file_out.write(json.dumps(dict(book=m.group(1), verse=m.group(2), text=TOKENS.findall(m.group(3)))))
        file_out.write('\n')
