import sys
import emoji

for line in sys.stdin:
  words = line.strip().split(' ')
  print(' '.join(['emoji' if any([c in emoji.UNICODE_EMOJI for c in w]) else 'other' for w in words]))

