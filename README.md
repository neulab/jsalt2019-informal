# jsalt2019-informal

## Baselines

Paul's scripts to get baselines: https://github.com/pmichel31415/jsalt-baseline. Feel free to modify in any way.

You can find trained model on the AWS cluster under `/export/fs01/pmichel1/models`, and preprocessed data for `en-{fr,ja,zh}` under `/export/fs01/pmichel1/corpora`

## Various scripts

The following are various scripts you might use:

* `create-alignments`: A pipeline to create alignments for the WMT2019 robustness task data and outputs
* `tagging-scripts`: Scripts that can be used for tagging for further downstream analysis
* `compare-mt`: Scripts to run [compare-mt](https://github.com/neulab/compare-mt) to generate reports
