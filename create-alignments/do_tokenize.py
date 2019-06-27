import spacy
import re
import sys

space_re = re.compile(r'  +')

nlp = spacy.load(sys.argv[1], disable=["parser", "tagger", "ner"])
for line in sys.stdin:
  line = re.sub(space_re, ' ', line.strip())
  doc = nlp(line)
  doc = [tok.text for tok in doc if tok.text.strip() != '']
  print(' '.join(doc))
