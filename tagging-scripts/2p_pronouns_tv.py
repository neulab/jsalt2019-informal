#!/usr/bin/env python3

import re, argparse, datetime, os
from collections import Counter, defaultdict

word_pattern = re.compile(r'\w+')

lexicons = {
	"english": {"neutral": {"you"}}, 
	"french": {"T": {"tu", "te", "toi"}, "V" : {"vous"}}
	}



def identify_2p_pronouns(tokenised_input, lexicon):
	counts = Counter(tokenised_input)

	pronouns_dict = defaultdict(dict)
	
	for k in lexicon:
		for pronoun in lexicon[k]:
			if counts[pronoun]:
				pronouns_dict[k][pronoun] = counts[pronoun]

	return(pronouns_dict)



def process_dataset(input_filepath, output_directory, source_lang, target_lang):
	os.makedirs(output_directory, exist_ok=True)
	with open(input_filepath, 'r') as infile:
		with open('{}/{}'.format(output_directory, os.path.split(input_filepath)[1]), 'w') as outfile:
			for line in infile:
				line = line.strip().lower()
				try:
					(example_id, source, target) = line.split('\t')
				except ValueError:
					print(line)
					continue
			
				tokenised_source = word_pattern.findall(source)

				if len(tokenised_source) > 200: 
					continue

				tokenised_target = word_pattern.findall(target)

				source_pronoun_dict = identify_2p_pronouns(tokenised_source, lexicons[source_lang.lower()])
				target_pronoun_dict = identify_2p_pronouns(tokenised_target, lexicons[target_lang.lower()])
				

				if source_pronoun_dict or target_pronoun_dict:

					line_out = '\t'.join([example_id, source, target]) + '\t'
					

					if source_pronoun_dict:
						source_pronouns = []
						for k in source_pronoun_dict:
							for (p,v) in source_pronoun_dict[k].items():
								source_pronouns.append('{}:{}'.format(p,(str(v))))
						source_pronouns = ' '.join(source_pronouns)
					else:
						source_pronouns = '0'


					if target_pronoun_dict:
						target_pronouns = []
						for k in target_pronoun_dict:
							for (p,v) in target_pronoun_dict[k].items():
								target_pronouns.append('{}:{}'.format(p,(str(v))))
						target_pronouns = ' '.join(target_pronouns)
					else:
						target_pronouns = '0'


					n_source = sum( (sum(source_pronoun_dict[k].values()) for k in source_pronoun_dict))
					n_target = sum( (sum(target_pronoun_dict[k].values()) for k in target_pronoun_dict))

					if n_source == n_target:
						most = '0'
					elif n_source > n_target:
						most = 'S'
					else:
						most = 'T'

			

					if source_lang == 'english':
						if 'T' in target_pronoun_dict and 'V' in target_pronoun_dict:
							T_V = 'Both'
						elif 'T' in target_pronoun_dict:
							T_V = 'T'
						elif 'V' in target_pronoun_dict:
							T_V = 'V'
						else:
							T_V = '0'
					else:
						if 'T' in source_pronoun_dict and 'V' in source_pronoun_dict:
							T_V = 'Both'
						elif 'T' in source_pronoun_dict:
							T_V = 'T'
						elif 'V' in source_pronoun_dict:
							T_V = 'V'
						else:
							T_V = '0'

					line_out += '\t'.join([source_pronouns, target_pronouns, most, T_V]) + '\n'

					outfile.write(line_out)

					# id, source, target, col for source pronouns, col for target pronouns, indicator for whether number of pronouns in target matches source, indicator for whether non-English lang uses T or V form (or both)



if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("-i", "--input_filepath", type=str, help="path to input file", default = '/Users/pippa/jsalt_workshop/datasets/MTNT/train/train.en-fr.tsv')
	parser.add_argument("-o", "--output_directory", type=str, help="directory where output file should be written", default = '/Users/pippa/jsalt_workshop/datasets/probing/2p_pronouns/MTNT/train/')
	parser.add_argument("-s", "--source_lang", type=str, help="name of source language", default = 'english')
	parser.add_argument("-t", "--target_lang", type=str, help="name of target language", default = 'french')

	print("starting at {}".format(datetime.datetime.now()))

	
	options = parser.parse_args()
	process_dataset(options.input_filepath, options.output_directory, options.source_lang, options.target_lang)
	print("finished at: {}".format(datetime.datetime.now()))


			