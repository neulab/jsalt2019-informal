set -e
### Script for processing the WMT robustness datasets to generate alignments
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# Step 1. 
#   Install Moses and GIZA++ according to the directions in the step-by-step guides here:
#   http://www.statmt.org/moses/?n=Development.GetStarted
#   http://www.statmt.org/moses/?n=Moses.Baseline
#   And set the following variable to the place to install moses

MOSES_DIR=$HOME/usr/local/mosesdecoder

# Step 2.
#   Install spacy and download models
pip install spacy
python -m spacy download en_core_web_sm
python -m spacy download fr_core_news_sm

# Step 3.
#   Run the following commands. You should just be able to run this script

# Download the data
wget http://phontron.com/data/wmt2019-system-data.tar.gz
tar -xzf wmt2019-system-data.tar.gz

# Tokenize all the files
for l in en; do
  for f in wmt2019-system-data/mtnt/*.$l wmt2019-system-data/extra/*/*.$l wmt2019-system-data/outputs/*/*.$l; do
    echo "python do_tokenize.py en_core_web_sm < $f > $f.tok"
    python do_tokenize.py en_core_web_sm < $f > $f.tok &
  done
done
for l in fr; do
  for f in wmt2019-system-data/mtnt/*.$l wmt2019-system-data/extra/*/*.$l wmt2019-system-data/outputs/*/*.$l; do
    echo "python do_tokenize.py fr_core_news_sm < $f > $f.tok"
    python do_tokenize.py fr_core_news_sm < $f > $f.tok &
  done
done
wait
for l in ja; do
  for f in wmt2019-system-data/mtnt/*.$l wmt2019-system-data/extra/*/*.$l wmt2019-system-data/outputs/*/*.$l; do
    echo "cat $f | sed 's/ /　/g' | kytea -notags > $f.tok"
    cat $f | sed 's/ /　/g' | kytea -notags > $f.tok &
  done
done
wait

# Clean the big training corpora
for f in fr ja; do
  echo "$MOSES_DIR/scripts/training/clean-corpus-n.perl wmt2019-system-data/mtnt/mtnt-train.$f-en $f.tok en.tok wmt2019-system-data/mtnt/mtnt-trainclean.$f-en 1 70 &"
  $MOSES_DIR/scripts/training/clean-corpus-n.perl wmt2019-system-data/mtnt/mtnt-train.$f-en $f.tok en.tok wmt2019-system-data/mtnt/mtnt-trainclean.$f-en 1 70 &
  echo "$MOSES_DIR/scripts/training/clean-corpus-n.perl wmt2019-system-data/mtnt/mtnt-train.en-$f $f.tok en.tok wmt2019-system-data/mtnt/mtnt-trainclean.en-$f 1 70 &"
  $MOSES_DIR/scripts/training/clean-corpus-n.perl wmt2019-system-data/mtnt/mtnt-train.en-$f $f.tok en.tok wmt2019-system-data/mtnt/mtnt-trainclean.en-$f 1 70 &
  echo "$MOSES_DIR/scripts/training/clean-corpus-n.perl wmt2019-system-data/extra/$f/train $f.tok en.tok wmt2019-system-data/extra/$f/trainclean 1 70 &"
  $MOSES_DIR/scripts/training/clean-corpus-n.perl wmt2019-system-data/extra/$f/train $f.tok en.tok wmt2019-system-data/extra/$f/trainclean 1 70 &
done
wait

mkdir -p alignments
for f in fr ja; do
  python $DIR/make_alignments.py $f --aligner fa &> alignments/make-$f.log &
done
wait
for f in fr ja; do
  python $DIR/make_alignments.py $f --aligner giza &> alignments/make-$f.log &
done
wait
