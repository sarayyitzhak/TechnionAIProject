import pandas as pd
import matplotlib.pyplot as plt


class ShowHyperParamsAnalysis:
    def __init__(self, config, y_axis_type):
        self.data_set_path = config["data_set_path"]
        self.y_axis_type = y_axis_type
        self.data = None
        self.result = []

    def pre_show_hyper_params_analysis(self):
        self.data = pd.read_csv(self.data_set_path)

    def show_hyper_params_analysis(self):
        min_samples_leaf_groups = self.data.groupby("min samples leaf")
        fig, axes = plt.subplots(2, 2)

        data_type = 'Train' if 'TRAIN' in self.y_axis_type else 'Validation'
        measure_type = 'MSE' if 'MSE' in self.y_axis_type else 'Accuracies'
        fig_title = f"{data_type} {measure_type} by hyper-params"

        data_type_column = 'train' if 'TRAIN' in self.y_axis_type else 'valid'
        measure_type_column = 'MSE' if 'MSE' in self.y_axis_type else 'acc'
        value_column = f"{data_type_column} {measure_type_column}"

        fig.suptitle(fig_title)
        for idx, min_samples_leaf in enumerate(min_samples_leaf_groups.groups.keys()):
            data_by_min_samples_leaf = min_samples_leaf_groups.get_group(min_samples_leaf)
            min_for_pruning_groups = data_by_min_samples_leaf.groupby("min for pruning")

            graph = axes[int(idx / 2), idx % 2]
            graph.set_title(f"min samples leaf = {min_samples_leaf}")
            graph.set_xlabel("max depth")
            graph.set_ylabel("accuracy")
            graph.grid()
            for min_for_pruning in min_for_pruning_groups.groups.keys():
                data_by_min_for_pruning = min_for_pruning_groups.get_group(min_for_pruning)
                graph.plot(data_by_min_for_pruning["max depth"], data_by_min_for_pruning[value_column], '.-', label=str(min_for_pruning))

        handles, labels = axes[0, 0].get_legend_handles_labels()
        fig.legend(handles, labels, title="min for pruning")
        fig.subplots_adjust(left=0.1, bottom=0.1, right=0.9, top=0.9, wspace=0.4, hspace=0.4)
        plt.show()
