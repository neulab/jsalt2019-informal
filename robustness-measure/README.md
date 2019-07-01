Example usage of the plotting script

For sentence BLEU or chrF (can be slow)

```bash
python plot_bleu_dist.py \
    --srcs wmt.valid.en wmt.test.en mtnt.test.en-fr.en \
    --refs wmt.valid.fr wmt.test.fr mtnt.test.en-fr.fr \
    --outs wmt.valid.out.fr wmt.test.out.fr mtnt.test.en-fr.out.fr \
    --dists wmt.valid.en.normed_nll wmt.test.en.normed_nll mtnt.test.en-fr.en.normed_nll \
    --score-type sentbleu
```

Or for arbitrary scores (eg. meteor) where you have precomputed scores:

```bash
python plot_bleu_dist.py \
    --srcs wmt.valid.en wmt.test.en mtnt.test.en-fr.en \
    --refs wmt.valid.fr wmt.test.fr mtnt.test.en-fr.fr \
    --outs wmt.valid.out.fr wmt.test.out.fr mtnt.test.en-fr.out.fr \
    --dists wmt.valid.en.normed_nll wmt.test.en.normed_nll mtnt.test.en-fr.en.normed_nll \
    --scores wmt.valid.fr.meteor wmt.test.fr.meteor mtnt.test.en-fr.fr.meteor
```
    
