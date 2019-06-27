import sys
import os
import argparse

p = argparse.ArgumentParser(description="""Make alignments for wmt robustness task data""")
p.add_argument("langpair", help="what language pair to use (e.g. fr-en)", type=str)
p.add_argument("--aligner", help="what aligner to use (giza or fa)", type=str, default='giza')
p.add_argument("--cmtdir", help="top directory of compare-mt", type=str, default='/home/gneubig/work/compare-mt')
args = p.parse_args()

# Get the language pair and component parts
langpair = args.langpair
src, trg = langpair.split('-')
jafr = src if src != 'en' else trg

def run_cmd(cmd):
  print(f'running: {cmd}')
  os.system(cmd)

sd = 'wmt2019-system-data'
# Get the data if it doesn't exist
if not os.path.isdir(sd):
  run_cmd('wget http://phontron.com/data/wmt2019-aligned-data.tar.gz')
  run_cmd('tar -xzf wmt2019-aligned-data.tar.gz')

# Cache the counts from the corpora if they don't already exist
for l in (src, trg):
  for f in (f'{sd}/mtnt/mtnt-train.{langpair}.{l}.tok', f'{sd}/extra/{jafr}/train.{l}.tok'):
    if not os.path.isfile(f):
      raise ValueError(f'File {f} not found')
    if not os.path.isfile(f'{f}.cnt'):
      run_cmd(f'python {args.cmtdir}/scripts/count.py < {f} > {f}.cnt')

systems = {
  'fr-en': 'bdosu cuni nle'.split(),
  'en-fr': 'bdosu cuni nle'.split(),
  'ja-en': 'ntt nle'.split(),
  'en-ja': 'ntt nle'.split()
}

syss = systems[langpair]
sys_len = len(syss)
sys_str = ' '.join([x.upper() for x in syss])
out_toks = [f'{sd}/outputs/{langpair}/{s}.{trg}.tok' for s in syss]
out_tok_str = ' '.join(out_toks)
src_tok = f'{sd}/mtnt/mtnt-test2019.{langpair}.{src}.tok'
trg_tok = f'{sd}/mtnt/mtnt-test2019.{langpair}.{trg}.tok'
align_str = (f'ref_align_file='+
             trg_tok.replace(f'{trg}.tok', f'{langpair}-{args.aligner}align')+
             ',out_align_files="'+
             ';'.join([f.replace(f'{trg}.tok',f'{langpair}-{args.aligner}align') for f in out_toks])+
             '"')

dirs = []
for i in range(len(syss)-1):
  for j in range(i+1,len(syss)):
    dirs.append(f'{i}-{j}')
dirs = ';'.join(dirs)
run_cmd(
  f'compare-mt {trg_tok} {out_tok_str} --src_file {src_tok}'
  +f'  --sys_names {sys_str} --output_directory compare/compare-{langpair}'
  +f'  --compare_word_accuracies'
  +f'    title=trg_general_freq,bucket_type=freq,freq_count_file={sd}/extra/{jafr}/train.{trg}.tok.cnt'
  +f'    title=trg_mtnt_freq,bucket_type=freq,freq_count_file={sd}/mtnt/mtnt-train.{langpair}.{trg}.tok.cnt'
  +f'    title=trg_case,bucket_type=case'
  +f'  --compare_src_word_accuracies'
  +f'    title=src_general_freq,{align_str},bucket_type=freq,freq_count_file={sd}/extra/{jafr}/train.{src}.tok.cnt'
  +f'    title=src_mtnt_freq,{align_str},bucket_type=freq,freq_count_file={sd}/mtnt/mtnt-train.{langpair}.{src}.tok.cnt'
  +f'    title=src_case,{align_str},bucket_type=case'
  +f'  --compare_ngrams'
  +f'    compare_type=match,compare_directions=\"{dirs}\"'
  +f'  --compare_sentence_examples'
  +f'    score_type=sentbleu,compare_directions=\"{dirs}\"')
