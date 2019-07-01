from scipy.stats import pearsonr
import argparse
import os.path
from sacrebleu import sentence_bleu, sentence_chrf
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa


def loadtxt(filename):
    """Load text file"""
    txt = []
    with open(filename) as f:
        for line in f:
            txt.append(line.rstrip())
    return np.asarray(txt)


def rescale(x):
    return (x - x.min())/(x.max() - x.min())


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--refs", metavar="REFS", nargs="+",
                        help="Reference translations")
    parser.add_argument("--srcs", metavar="SRCS", nargs="+",
                        help="Source sentences")
    parser.add_argument("--outs", metavar="OUTS", nargs="+",
                        help="Model output")
    parser.add_argument("--dists", metavar="DISTS", nargs="+",
                        help="Distance of the source sentences")
    parser.add_argument("--scores", metavar="SCORES", nargs="*",
                        help="Precomputed scores (if this is not provided the "
                        "scores will be computed automatically using the "
                        "specified `--score-type` if available)")
    parser.add_argument("--score-type", type=str, help="Name of the scoring"
                        "function (eg. BLEU/chrF)")
    parser.add_argument("--img-prefix", type=str, default="./", help="Prefix "
                        "to the path to which the plots will be saved")
    parser.add_argument("--bs-resampling", type=str, default=None,
                        help="[N_samples]x[sample_size] for bootstrap "
                        "resampling within each bin")
    # Parse
    args = parser.parse_args()
    # Check number of files
    N = len(args.refs)
    if N != len(args.outs) or N != len(args.outs) or N != len(args.dists):
        raise ValueError("Specify the same number of input files of each type")
    if args.scores is not None and N != len(args.scores):
        raise ValueError("Specify the same number of input files of each type")

    return args


def sentbleu(y_hat, y):
    return sentence_bleu(y_hat, y, smooth_method="add-n", smooth_value=1.0)


def sentchrf(y_hat, y):
    return sentence_chrf(y_hat, y)*100


score_funcs = {"sentbleu": sentbleu, "chrf": sentchrf}


def percentiles_plot(x, y, n_bins, percent_increment=10, bs_resampling=None):
    # All percentiles in increments of 10 by default
    percents = list(range(0, 101, percent_increment))
    if not 50 % percent_increment == 0:
        percents = sorted(list(set(percents) + {50}))
    # cut the x axis into n_bins bins
    N = len(x)
    # Threshold for the bins (uniformly partintioning the x axis)
    bin_thesholds = np.linspace(0, x.max(), n_bins+1)
    # Assign each point to a bin
    bin_assignments = np.digitize(x, bin_thesholds)
    # Bins as a list of indices mapping each bin to the indices it contains
    idxs = np.arange(N)
    bins = [idxs[bin_assignments == bin_idx]
            for bin_idx in range(n_bins) if (bin_assignments == bin_idx).any()]
    # Size of bins and their widths
    bin_sizes = np.asarray([len(bin_) for bin_ in bins])
    # y values of each bin
    binned_y = [y[bin_] for bin_ in bins]
    # Do BS resampling if needed
    if bs_resampling is not None:
        n, k = bs_resampling
        for i, bin_y in enumerate(binned_y):
            if k > len(bin_y):
                binned_y[i] = [bin_y.mean() for _ in range(n)]
            else:
                binned_y[i] = [np.random.choice(bin_y, size=k).mean()
                               for _ in range(n)]
    # Avg x value of each bin
    avg_x = np.stack([x[bin_].mean() for bin_ in bins])
    # Compute percentiles
    all_percentiles = np.asarray([
        [np.percentile(bleu, percent) for percent in percents]
        for bleu in binned_y
    ])
    # Find the best position to print the label of each percentile
    # (by min-maxing the distance between each consecutive percentile)
    best_pos = np.argmax([np.min(percentiles[1:] - percentiles[:-1]).mean()
                          for percentiles in all_percentiles])
    # Map percent value to percentiles
    all_percentiles = {percent: all_percentiles[:, i]
                       for i, percent in enumerate(percents)}
    for percent in percents[-len(percents)//2:]:
        plt.fill_between(
            avg_x,
            all_percentiles[percent],
            all_percentiles[100-percent],
            color="blue",
            alpha=0.2,
            edgecolor="black",
        )
        # Annotate the percent
        lower = all_percentiles[percent-10][best_pos]
        upper = all_percentiles[percent][best_pos]
        plt.text(avg_x[best_pos], (upper + lower)/2, f"{percent}%",
                 horizontalalignment='center', verticalalignment='center',
                 fontsize="x-small")
        lower = all_percentiles[100-percent][best_pos]
        upper = all_percentiles[100-percent+10][best_pos]
        plt.text(avg_x[best_pos], (upper + lower)/2, f"{percent}%",
                 horizontalalignment='center', verticalalignment='center',
                 fontsize="x-small")
    # plot median as well
    plt.plot(avg_x, all_percentiles[50], color="blue")
    # Plot a reversed histogram of the distribution of bin sizes
    # (*9 is there for scale)
    bin_distrib = bin_sizes/bin_sizes.max()*9
    # Position and width of the bars
    bin_centers = [
        (bin_thesholds[bin_idx+1] + bin_thesholds[bin_idx])/2
        for bin_idx in range(n_bins) if (bin_assignments == bin_idx).any()
    ]
    bar_width = bin_thesholds[1] - bin_thesholds[0]
    # Vertical position
    bar_y = int(min(min(v) for v in all_percentiles.values())/10) * 10
    # plot it
    plt.bar(bin_centers, -bin_distrib, bottom=bar_y, width=bar_width,
            color="gray", alpha=0.6, label="Bin sizes", linewidth=0)
    plt.legend()


def main():
    args = get_args()
    # Load files
    refs = [loadtxt(filename) for filename in args.refs]
    outs = [loadtxt(filename) for filename in args.outs]
    srcs = [loadtxt(filename) for filename in args.srcs]
    dists = np.concatenate([np.loadtxt(filename) for filename in args.dists])
    # Load or compute scores
    if args.scores is not None:
        scores = np.concatenate([np.loadtxt(filename)
                                 for filename in args.scores])
    else:
        if args.score_type not in score_funcs:
            raise ValueError(
                f"On-the-fly {args.score_type} computation is not supported, "
                "please precompute the scores yourself and provide them with "
                "`--scores [FILES]`"
            )
        # Compute scores on the fly for those that are supported
        score_func = score_funcs[args.score_type]
        scores = [
            np.asarray([score_func(y_hat, y) for y_hat, y in zip(out, ref)])
            for out, ref in zip(outs, refs)
        ]
        # Save precomputed scores
        for score, ref_file in zip(scores, args.refs):
            if os.path.isfile(f"{ref_file}.{args.score_type}"):
                print(
                    f"WARNING: {ref_file}.{args.score_type} already exists, "
                    "not overwriting"
                )
            np.savetxt(f"{ref_file}.{args.score_type}", score)
        scores = np.concatenate(scores)
    # Parse BS resampling example
    if args.bs_resampling is not None:
        n_samples, sample_size = args.bs_resampling.split("x")
        args.bs_resampling = (int(n_samples), int(sample_size))
    plt.figure(figsize=(7, 8))
    # Pearson correclation as titles
    corr_, p_val = pearsonr(scores, dists)
    plt.suptitle(
        f"{args.score_type} vs NLL\n"
        f"Pearson r: {corr_:.3f} ($p\\approx{p_val:.3f}$))"
    )
    # Scatter plot of the test samples (by datasets)
    plt.subplot("211")
    # Colors for plotting
    color_spectrum = np.linspace(0.1, 0.9, len(refs))
    colors = np.concatenate([
        np.full(len(refs[i]), v)
        for i, v in enumerate(color_spectrum)
    ])
    plt.scatter(dists, scores, s=0.5, c=colors,
                marker="+", alpha=0.9, cmap="jet")
    # Make a good legend
    cmap = plt.get_cmap("jet")
    legend_elements = [
        matplotlib.lines.Line2D([0], [0], marker='+', markersize=10,
                                color=cmap(color_spectrum[i]), linewidth=0)
        for i in range(len(srcs))
    ]
    plt.legend(legend_elements, args.srcs)
    plt.xlabel("NLL")
    plt.ylabel(args.score_type)
    # Binned percentiles
    plt.subplot("212")
    # Plot binned percentages
    percentiles_plot(dists, scores, 20, percent_increment=10,
                     bs_resampling=args.bs_resampling)
    # Axes labels
    plt.xlabel("NLL")
    plt.ylabel(args.score_type)
    # Save figure
    score_name = (args.score_type).replace(" ", "_")
    plt.savefig(f"{score_name}_vs_nll.png", bbox_inches="tight", dpi=300)
    # Print extremal elements
    srcs = [sent for dataset in srcs for sent in dataset]
    # We take the max/min of the sum/difference of the rescaled scores and
    # distances
    sum_ = rescale(dists) + rescale(scores)
    sum_order = sum_.argsort()
    diff_ = rescale(dists) - rescale(scores)
    diff_order = diff_.argsort()
    n_examples = 5
    # Lower left
    print("==== Lowest BLEU, lowest distance ====")
    for i in sum_order[:n_examples]:
        print(srcs[i])
    # Upper left
    print("==== Highest BLEU, lowest distance ====")
    for i in diff_order[:n_examples]:
        print(srcs[i])
    # Lower right
    print("==== Lowest BLEU, highest distance ====")
    for i in diff_order[-n_examples:]:
        print(srcs[i])
    # Upper right
    print("==== Highest BLEU, highest distance ====")
    for i in sum_order[-n_examples:]:
        print(srcs[i])


if __name__ == "__main__":
    main()
