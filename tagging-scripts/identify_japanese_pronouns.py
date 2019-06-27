import sys
import re
from collections import defaultdict

# This is a script to identify pronouns in Japanese
# It requires data segmented by KyTea (http://www.phontron.com/kytea/)
#
# If you have raw Japanese text (with no spaces), use this script like:
#  cat japanese.txt | kytea | python identify_japanese_pronouns.py > japanese_with_pronouns.txt
#
# If you have tokenized Japanese text (with lots of spaces), use this script like:
#  cat segmented_japanese.txt | kytea -in tok | python identify_japanese_pronouns.py > japanese_with_pronouns.txt
#
# The result will be segmented, where each pronoun X will be surrounded by <<<X>>>_{1,2,3} indicating the
# person of the pronoun.
#
# This heavily references Wikipedia:
#  https://ja.wikipedia.org/wiki/日本語の一人称代名詞
#  https://ja.wikipedia.org/wiki/日本語の二人称代名詞

pronoun_map = {
  # "Standard" first person
  '私': 1,
  'わたし': 1,
  '僕': 1,
  'ぼく': 1,
  '俺': 1,
  'おれ': 1,
  '我々': 1, # 1st person plural
  # Less standard first person
  'わたくし': 1,
  'あたし': 1,
  'あたくし': 1,
  'わし': 1,
  'わて': 1,
  'わい': 1,
  'うち': 1,
  'おいら': 1,
  'おい': 1,
  '我輩': 1,
  '吾輩': 1,
  '我が輩': 1,
  '吾が輩': 1,
  # "Standard" second person
  'あなた': 2,
  'あんた': 2,
  'お前': 2,
  '君': 2,
  # Less standard second person
  '貴方': 2,
  'アナタ': 2,
  'おまえ': 2,
  'きみ': 2,
  'キミ': 2,
  # "Standard" third person
  '彼': 3, # can also mean "boyfriend"
  'かれ': 3, # can also mean "boyfriend"
  '彼女': 3, # can also mean "girlfriend"
  'かのじょ': 3, # can also mean "girlfriend"
  'あいつ': 3,
}

missed_pronoun = defaultdict(lambda: 0)

for line in sys.stdin:
  line = line.replace('\ ', '　') # remove space tokens
  words = line.strip().split(' ')
  out = []
  for w in words:
    t = w.split('/')
    if len(t) != 3:
      print(f'malformed tag {w}, skipping', file=sys.stderr)
      out.append(w)
    elif t[1] == '代名詞':
      if t[0] in pronoun_map:
        out.append(f'<<<{t[0]}>>>_{pronoun_map[t[0]]}')
      else:
        missed_pronoun[t[0]] += 1
        out.append(t[0])
    else:
      out.append(t[0])
  print(' '.join(out))

# # Print out missed pronouns to check to make sure none are missed 
# for k, v in sorted(missed_pronoun.items(), key=lambda x: -x[1]):
#   print(f'MISSED: {k}\t{v}', file=sys.stderr)
