import spacy
import re
import sys

# First install spacy and download models
# $ pip install spacy
# $ python -m spacy download en_core_web_sm
# $ python -m spacy download fr_core_news_sm

# Then run by doing the following for English or French respectively:
# $ python do_tokenize.py en < in.txt > out.txt
# $ python do_tokenize.py fr < in.txt > out.txt

space_re = re.compile(r'  +')

lang = sys.argv[1]
models = {
  'en': 'en_core_web_sm',
  'fr': 'fr_core_news_sm',
}

nlp = spacy.load(models[lang], disable=["parser", "tagger", "ner"])
for line in sys.stdin:
  line = re.sub(space_re, ' ', line.strip())
  doc = nlp(line)
  doc = [tok.text for tok in doc if tok.text.strip() != '']
  print(' '.join(doc))
