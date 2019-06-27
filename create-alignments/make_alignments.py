import sys
import os
import subprocess
import glob
import argparse

p = argparse.ArgumentParser(description="""Make alignments for wmt robustness task data""")
p.add_argument("lang", help="what language to use (fr or ja)", type=str)
p.add_argument("--aligner", help="what aligner to use (giza or fa)", type=str, default='giza')
p.add_argument("--mdir", help="top directory of Moses installation", type=str, default='/home/gneubig/usr/local/mosesdecoder')
p.add_argument("--fadir", help="top directory of FastAlign installation", type=str, default='/home/gneubig/usr/local/fast_align')
args = p.parse_args()

def run_cmd(cmd):
  print(f'running: {cmd}')
  os.system(cmd)
  
def run_background(cmd):
  print(f'running in background: {cmd}')
  return subprocess.Popen([cmd], shell=True, stdin=None, stdout=None, stderr=None, close_fds=True)

lang = sys.argv[1]

mtnt_types = ('trainclean', 'valid', 'test', 'test2019')
f_orig = ([f'wmt2019-system-data/mtnt/mtnt-{t}.{lang}-en.{lang}.tok' for t in mtnt_types]
         + [f'wmt2019-system-data/mtnt/mtnt-{t}.en-{lang}.{lang}.tok' for t in mtnt_types]
         + [f'wmt2019-system-data/extra/{lang}/trainclean.{lang}.tok'])
e_orig = [l.replace(f'{lang}.tok', 'en.tok') for l in f_orig]
f_ftrg = list(glob.glob(f'wmt2019-system-data/outputs/en-{lang}/*.{lang}.tok')) 
e_ftrg = [f'wmt2019-system-data/mtnt/mtnt-test2019.en-{lang}.en.tok' for f in f_ftrg]
e_etrg = list(glob.glob(f'wmt2019-system-data/outputs/{lang}-en/*.en.tok')) 
f_etrg = [f'wmt2019-system-data/mtnt/mtnt-test2019.{lang}-en.{lang}.tok' for f in e_etrg]

f_all = f_orig + f_ftrg + f_etrg
e_all = e_orig + e_ftrg + e_etrg

run_cmd(f'mkdir -p alignments/{lang}')
run_cmd('cat '+' '.join(f_all)+f' | sed "s/^$/__EMPTY__/g" > alignments/{lang}/all.{lang}')
run_cmd('cat '+' '.join(e_all)+f' | sed "s/^$/__EMPTY__/g" > alignments/{lang}/all.en')

if args.aligner == 'giza':
  run_cmd(f'{args.mdir}/scripts/training/train-model.perl -external-bin-dir {mdir}/tools -last-step 4 -root-dir alignments/{lang}/moses -corpus alignments/{lang}/all -f {lang} -e en -alignment grow-diag-final-and -cores 4 -parallel')
elif args.aligner == 'fa':
  run_cmd(f'mkdir -p alignments/{lang}/fa')
  with open(f'alignments/{lang}/all.{lang}', 'r') as ffile, open(f'alignments/{lang}/all.en', 'r') as efile, open(f'alignments/{lang}/fa/all.{lang}-en', 'w') as fefile:
    for fline, eline in zip(ffile, efile):
      fline = fline.strip()
      eline = eline.strip()
      print(f'{fline} ||| {eline}', file=fefile)
  p1 = run_background(f'{args.fadir}/build/fast_align -i alignments/{lang}/fa/all.{lang}-en -d -o -v > alignments/{lang}/fa/all.foralign.{lang}-en 2> alignments/{lang}/fa/all.foralign.log')
  p2 = run_background(f'{args.fadir}/build/fast_align -i alignments/{lang}/fa/all.{lang}-en -d -o -v -r > alignments/{lang}/fa/all.backalign.{lang}-en 2> alignments/{lang}/fa/all.backalign.log')
  p1.wait()
  p2.wait()
  run_cmd(f'{args.fadir}/build/atools -i alignments/{lang}/fa/all.foralign.{lang}-en -j alignments/{lang}/fa/all.backalign.{lang}-en -c grow-diag-final-and > alignments/{lang}/fa/all.align.{lang}-en')
else:
  raise ValueError(f'Illegal aligner {args.aligner}')

# TODO: figure out what GIZA++ outputs
alignfile = None if args.aligner == 'giza' else f'alignments/{lang}/fa/all.align.{lang}-en'
  
def assign_alignments(aligns, inf, outf, reverse=False):
  print(f'assign_alignments(aligns, {inf}, {outf})')
  if inf == outf:
    raise ValueError(f'Error {inf} == {outf}')
  with open(inf, 'r') as ins, open(outf, 'w') as outs:
    for line in ins:
      if not reverse:
        print(aligns.readline().strip(), file=outs)
      else:
        print(' '.join([f'{trg}-{src}' for (src,trg) in [v.split('-') for v in aligns.readline().strip().split(' ')]]), file=outs)

with open(alignfile, 'r') as alignstream:
  for f in f_orig:
    if f'en-{lang}' in f:
      assign_alignments(alignstream, f, f.replace(f'{lang}.tok', f'en-{lang}-{args.aligner}align'), reverse=True)
    else:
      assign_alignments(alignstream, f, f.replace(f'{lang}.tok', f'{lang}-en-{args.aligner}align'))
  for f in f_ftrg:
    assign_alignments(alignstream, f, f.replace(f'{lang}.tok', f'en-{lang}-{args.aligner}align'), reverse=True)
  for e in e_etrg:
    assign_alignments(alignstream, e, e.replace(f'en.tok', f'{lang}-en-{args.aligner}align'))
