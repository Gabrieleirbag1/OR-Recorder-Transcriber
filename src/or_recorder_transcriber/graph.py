import os
import re
import matplotlib.pyplot as plt
import pandas as pd
from or_recorder_transcriber.utils import FIGURES_DIR
from litelogging.litelogging import log

class GraphGenerator():
    def __init__(self, file_path: str = None, filename: str = None):
        """Initialize the GraphGenerator.

        :param file_path str: Path to the CSV file containing the session data.
        :param filename str: Base filename (without extension) used to name the output figures.
        """
        self.file_path = file_path
        self.filename = filename.split(".")[0]

        self.df = None

    def clean_event_name(self, raw_event: str) -> str:
        """Remove a possible number (dose) at the end of text, e.g: 'propofol 0.05' -> 'propofol'.
        
        :param raw_event str: The raw event string from the CSV.
        
        :return: The cleaned event name.
        :rtype: str
        """
        if pd.isna(raw_event):
            return "N/A"
        return re.sub(r"\s+[\d.]+\s*$", "", str(raw_event)).strip()

    def load_data(self) -> pd.DataFrame:
        """Load the CSV and prepare the necessary columns for graphs. The "Event Type" column is
        read as-is from the CSV: it was already resolved from labels.json when the row was logged,
        so it does not need to be recomputed here.
        
        :return: The loaded and processed DataFrame.
        :rtype: pd.DataFrame
        """
        df = pd.read_csv(self.file_path, encoding="utf-8")

        df["Relative Time"] = pd.to_numeric(df["Relative Time"], errors="coerce")
        df["Dose_clean"] = df["Dose"].astype(str).str.extract(r"([\d.]+)")
        df["Dose"] = pd.to_numeric(df["Dose_clean"], errors="coerce")  # N/A -> NaN
        df["Event_clean"] = df["Events"].apply(self.clean_event_name)
        df["Label"] = df["Corrected Label"].fillna(df["Selected Label"])

        self.df = df
        return df

    def get_colors(self, n_events: int):
        """Return a color palette adapted to the number of events.
        
        :param n_events int: The number of unique events to plot.
        
        :return: A list of colors.
        :rtype: list
        """
        return plt.cm.tab10.colors if n_events <= 10 else plt.cm.tab20.colors

    def plot_event_curve(self, ax: plt.Axes, ev_data: pd.DataFrame, label_name: str, color: str, event_type: str, linestyle: str = "-"):
        """Plot the curve of a single label on the given axis.

        :param ax plt.Axes: The matplotlib axis to plot on.
        :param ev_data pd.DataFrame: The DataFrame containing data for the specific label.
        :param label_name str: The selected or corrected label for the event (may include the medication type for legend clarity).
        :param color str: The color to use for the plot.
        :param event_type str: The Event Type ("Medication" or "Other") controlling the plot style (dose curve vs. occurrence markers).
        :param linestyle str: The line style to use, e.g. "-" for Perfusion, "--" for Bolus. Ignored for non-Medication events.
        """
        if event_type == "Medication":
            ax.step(
                ev_data["Relative Time"],
                ev_data["Dose"],
                marker="o",
                where="post",
                label=label_name,
                color=color,
                linestyle=linestyle,
            )
        else:
            ax.scatter(
                ev_data["Relative Time"],
                [1] * len(ev_data),
                marker="x",
                s=80,
                label=label_name,
                color=color,
            )

    def build_figure_for_event_type(self, sub: pd.DataFrame, event_type: str) -> plt.Figure:
        """Build a standalone matplotlib figure for a single Event Type.

        For "Medication" events, each label gets one color, and is split into
        separate curves per Medication Type (Perfusion/Bolus) using different
        line styles, all sharing the same color and the same axes.

        :param sub pd.DataFrame: The subset of the DataFrame corresponding to the specific Event Type.
        :param event_type str: The Event Type being processed.

        :return: The matplotlib figure built for this Event Type.
        :rtype: plt.Figure
        """
        fig, ax = plt.subplots(figsize=(8, 6))
        labels = sub["Label"].dropna().unique()
        colors = self.get_colors(len(labels))
        linestyles = {"Perfusion": "-", "Bolus": "--"}

        for i, lab in enumerate(sorted(labels, key=str)):
            label_data = sub[sub["Label"] == lab]
            color = colors[i % len(colors)]

            if event_type == "Medication" and "Medication Type" in label_data.columns:
                med_types = label_data["Medication Type"].dropna().unique()
                if len(med_types) == 0:
                    # No medication type info at all for this label: single solid curve
                    ev_data = label_data.sort_values("Relative Time")
                    self.plot_event_curve(ax, ev_data, str(lab), color, event_type)
                else:
                    for med_type in sorted(med_types, key=str):
                        ev_data = label_data[label_data["Medication Type"] == med_type].sort_values("Relative Time")
                        linestyle = linestyles.get(med_type, "-")
                        self.plot_event_curve(ax, ev_data, f"{lab} ({med_type})", color, event_type, linestyle=linestyle)

                    # Rows for this label with no medication type at all (e.g. NaN)
                    no_type_data = label_data[label_data["Medication Type"].isna()].sort_values("Relative Time")
                    if not no_type_data.empty:
                        self.plot_event_curve(ax, no_type_data, str(lab), color, event_type, linestyle=":")
            else:
                ev_data = label_data.sort_values("Relative Time")
                self.plot_event_curve(ax, ev_data, str(lab), color, event_type)

        self.style_axes(ax, f"Event Type : {event_type}", event_type)
        return fig

    def style_axes(self, ax: plt.Axes, title: str, event_type: str):
        """Apply labels, title, legend and grid on the axis.
        
        :param ax plt.Axes: The matplotlib axis to style.
        :param title str: The title to display for the axis.
        :param event_type str: The Event Type being processed.
        """
        ax.set_xlabel("Relative Time (s)")
        ylabel = "Dose" if event_type == "Medication" else "Occurrence"
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        handles, labels = ax.get_legend_handles_labels()
        if handles:
            ax.legend(
                loc="upper left",
                bbox_to_anchor=(1.02, 1),
                borderaxespad=0,
                fontsize=8,
                ncol=1 if len(handles) <= 20 else 2,  # split into 2 columns if there are a lot of entries
            )
        ax.grid(True, alpha=0.3)

    def save_figure(self, fig: plt.Figure, event_type: str) -> str:
        """Save the figure in FIGURES_DIR and return the output path.
        
        :param fig plt.Figure: The matplotlib figure to save.
        :param event_type str: The Event Type being processed.
        
        :return: The path where the figure was saved.
        :rtype: str
        """
        safe_event_type = re.sub(r"[^\w\-]", "_", str(event_type))
        out_path = os.path.join(FIGURES_DIR, f"{self.filename}_{safe_event_type}.png")
        fig.savefig(out_path, dpi=150, bbox_inches="tight")
        plt.close(fig)
        return out_path

    def generate_all(self):
        """Generate and save one graph per distinct Event Type present in the data."""
        if self.df is None:
            self.load_data()

        event_types = self.df["Event Type"].dropna().unique()

        for event_type in event_types:
            sub = self.df[self.df["Event Type"] == event_type].copy()
            fig = self.build_figure_for_event_type(sub, event_type)
            out_path = self.save_figure(fig, event_type)
            log(f"-> Graph saved: {out_path}")

    def generate_graph(self):
        """Main function to load data and generate graphs for each Event Type."""
        self.load_data()
        self.generate_all()

if __name__ == "__main__":
    graph = GraphGenerator(
        "/home/frigiel/Documents/VSCODE/Stage LIAM 2026/OR-Recorder-Transcriber/output/data/test_csv.csv",
        filename="test_csv.csv",
    )
    graph.generate_graph()