import argparse
import sys

p = argparse.ArgumentParser(description="""Convert tokenized words into a file of tags indicating pronouns""")
p.add_argument("lang", help="what language to use (en/fr/ja)", type=str)
p.add_argument("--do_formal", help="Whether to distinguish formality", action='store_true')
p.add_argument("--do_plural", help="Whether to distinguish plural", action='store_true')
args = p.parse_args()

ja_map = {
  # "Standard" first person
  '私': (1, 'fml', 'sing'),
  'わたし': (1, 'fml', 'sing'),
  'わたくし': (1, 'fml', 'sing'),
  '僕': (1, 'infml', 'sing'),
  'ぼく': (1, 'infml', 'sing'),
  '俺': (1, 'infml', 'sing'),
  'おれ': (1, 'infml', 'sing'),
  '我々': (1, 'infml', 'plrl'), # (1, 'fml', 'sing')st person plural
  # Less standard first person
  'あたし': (1, 'infml', 'sing'),
  'あたくし': (1, 'infml', 'sing'),
  'わし': (1, 'infml', 'sing'),
  'わて': (1, 'infml', 'sing'),
  'わい': (1, 'infml', 'sing'),
  'うち': (1, 'infml', 'sing'),
  'おいら': (1, 'infml', 'sing'),
  'おい': (1, 'infml', 'sing'),
  '我輩': (1, 'fml', 'sing'),
  '吾輩': (1, 'fml', 'sing'),
  '我が輩': (1, 'fml', 'sing'),
  '吾が輩': (1, 'fml', 'sing'),
  # "Standard" second person
  'あなた': (2, 'fml', 'sing'),
  'あんた': (2, 'infml', 'sing'),
  'お前': (2, 'infml', 'sing'),
  '君': (2, 'infml', 'sing'),
  # Less standard second person
  '貴方': (2, 'fml', 'sing'),
  'アナタ': (2, 'infml', 'sing'),
  'おまえ': (2, 'infml', 'sing'),
  'きみ': (2, 'infml', 'sing'),
  'キミ': (2, 'infml', 'sing'),
  # "Standard" third person
  '彼': (3, 'fml', 'sing'), # can also mean "boyfriend"
  'かれ': (3, 'fml', 'sing'), # can also mean "boyfriend"
  '彼女': (3, 'fml', 'sing'), # can also mean "girlfriend"
  'かのじょ': (3, 'fml', 'sing'), # can also mean "girlfriend"
  'あいつ': (3, 'infml', 'sing'),
}

en_map = {
  'i': (1, None, 'sing'),
  'me': (1, None, 'sing'),
  'you': (2, None, None),
  'he': (3, None, 'sing'),
  'him': (3, None, 'sing'),
  'she': (3, None, 'sing'),
  'they': (3, None, 'plrl'),
  'them': (3, None, 'plrl'),
  'we': (1, None, 'plrl'),
  'us': (1, None, 'plrl'),
  'they': (3, None, 'plrl'),
  'them': (3, None, 'plrl'),
}


fr_map = {
  # I (subject)
  'je': (1, None, 'sing'),
  # Me (object)
  'moi': (1, None, 'sing'),
  # You (subject)
  'tu': (2, 'infml', 'sing'),
  # You (object)
  'toi': (2, 'infml', 'sing'),
  # He (subject)
  'il': (3, None, 'sing'),
  # Him (object)
  'lui': (3, None, 'sing'),
  # She/her (object and subject)
  'elle': (3, None, 'sing'),
  # this is a weird one. It can be translated as "one" in english (eg "one does not do this") but is also used a lot as an informal way of saying "we" (very relevant here)
  # I would say that it is informal. Also it refers to multiple or an indefinite amount of people but still conjugates as a singular (yes...)
  'on': (1, 'infml', 'sing'),
  # We/us
  'nous': (1, None, 'plrl'),
  # You: This is either (plural AND neither formal or informal) OR (singular AND formal).
  'vous': (2, None, None),
  # They (subject, masculine)
  'ils': (3, None, 'plrl'),
  # They (object, masculine)
  'eux': (3, None, 'plrl'),
  # They (subject/object, feminine)
  'elles': (3, None, 'plrl'),
}

tag_map = {
  'ja': lambda x: ja_map.get(x, (None, None, None)),
  'en': lambda x: en_map.get(x, (None, None, None)),
  'fr': lambda x: fr_map.get(x, (None, None, None))
}[args.lang]

def tag_word(w):
  person, formality, plurality = tag_map(w)
  if not person:
    return 'other'
  tag = str(person)
  if args.do_formal and formality:
    tag += f'_{formality}'
  if args.do_plural and plurality:
    tag += f'_{plurality}'
  return tag

for line in sys.stdin:
  words = line.strip().split(' ')
  print(' '.join([tag_word(w.lower()) for w in words]))
