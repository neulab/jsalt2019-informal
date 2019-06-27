import sys
import os
import argparse

### Analysis script for the WMT 2019 robustness shared task

p = argparse.ArgumentParser(description="""
  Perform analysis using compare-mt for the wmt robustness task data

  Run this script, and the results should be written so you can see them in compare/compare-{langpair}/index.html  
""")
p.add_argument("langpair", help="what language pair to use (e.g. fr-en)", type=str)
p.add_argument("--aligner", help="what aligner to use (giza or fa)", type=str, default='giza')
p.add_argument("--cmtdir", help="top directory of compare-mt", type=str, default='/home/gneubig/work/compare-mt')
p.add_argument("--jsaltdir", help="top directory of JSALT scripts", type=str, default='/home/gneubig/work/jsalt2019-informal')
args = p.parse_args()

# Get the language pair and component parts
langpair = args.langpair
src, trg = langpair.split('-')
jafr = src if src != 'en' else trg

sd = 'wmt2019-system-data'
# Get the data if it doesn't exist
if not os.path.isdir(sd):
  run_cmd('wget http://phontron.com/data/wmt2019-aligned-data.tar.gz')
  run_cmd('tar -xzf wmt2019-aligned-data.tar.gz')


def run_cmd(cmd):
  print(f'running: {cmd}')
  os.system(cmd)

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

# Find all the system files that we want to use
syss = systems[langpair]
sys_len = len(syss)
sys_str = ' '.join([x.upper() for x in syss])
out_toks = [f'{sd}/outputs/{langpair}/{s}.{trg}.tok' for s in syss]
out_tok_str = ' '.join(out_toks)
src_tok = f'{sd}/mtnt/mtnt-test2019.{langpair}.{src}.tok'
trg_tok = f'{sd}/mtnt/mtnt-test2019.{langpair}.{trg}.tok'
refout_str = (f'ref_XXX='+
             trg_tok.replace(f'.tok', f'.YYY')+
             ',out_XXX="'+
             ';'.join([f.replace(f'.tok',f'.YYY') for f in out_toks])+
             '"')
align_str = refout_str.replace('XXX', 'align_file').replace('out_align_file', 'out_align_files').replace(f'{trg}.YYY', f'{langpair}-{args.aligner}align')
emoji_str = refout_str.replace('XXX', 'labels').replace('YYY', f'emoji')
prn_str = refout_str.replace('XXX', 'labels').replace('YYY', f'prn')
all_toks = out_toks + [trg_tok] + [src_tok]
all_langs = [trg for _ in all_toks]
all_langs[-1] = src

# Do any necessary extra tagging on the target
# NOTE: If you want to add extra analysis, this would be a good place to add it by writing a tagging script and applying it here
for fin, lang in zip(all_toks, all_langs):
  fout = fin.replace('.tok', '.emoji')
  assert(fout != fin)
  if not os.path.isfile(fout):
    run_cmd(f'python {args.jsaltdir}/tagging-scripts/tag_emojis.py < {fin} > {fout}')
  fout = fin.replace('.tok', '.prn')
  assert(fout != fin)
  if not os.path.isfile(fout):
    run_cmd(f'python {args.jsaltdir}/tagging-scripts/tag_pronouns.py {lang} < {fin} > {fout}')


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
  +f'    title=trg_emoji,bucket_type=label,{emoji_str},label_set=emoji' 
  +f'    title=trg_pronouns,bucket_type=label,{prn_str},label_set=prn' 
  +f'  --compare_src_word_accuracies'
  +f'    title=src_general_freq,{align_str},bucket_type=freq,freq_count_file={sd}/extra/{jafr}/train.{src}.tok.cnt'
  +f'    title=src_mtnt_freq,{align_str},bucket_type=freq,freq_count_file={sd}/mtnt/mtnt-train.{langpair}.{src}.tok.cnt'
  +f'    title=src_case,{align_str},bucket_type=case'
  +f'    title=src_emoji,{align_str},bucket_type=label,src_labels='+src_tok.replace('.tok','.emoji')+',label_set=emoji' 
  +f'    title=src_pronouns,{align_str},bucket_type=label,src_labels='+src_tok.replace('.tok','.prn')+',label_set=1+2+3' 
  +f'  --compare_ngrams'
  +f'    compare_type=match,compare_directions=\"{dirs}\"'
  +f'  --compare_sentence_examples'
  +f'    score_type=sentbleu,compare_directions=\"{dirs}\"')
