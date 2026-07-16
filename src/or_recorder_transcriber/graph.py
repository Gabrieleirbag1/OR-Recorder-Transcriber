import os
import re
import matplotlib.pyplot as plt
import pandas as pd
from or_recorder_transcriber.utils import FIGURES_DIR
from lite_logging.lite_logging import log

class GraphGenerator:
    def __init__(self, file_path: str = None):
        self.file_path = file_path

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
        """Load the CSV and prepare the necessary columns for graphs.
        
        :return: The loaded and processed DataFrame.
        :rtype: pd.DataFrame
        """
        df = pd.read_csv(self.file_path, encoding="utf-8")

        df["Relative Time"] = pd.to_numeric(df["Relative Time"], errors="coerce")
        df["Dose_num"] = pd.to_numeric(df["Dose"], errors="coerce")  # N/A -> NaN
        df["Event_clean"] = df["Events"].apply(self.clean_event_name)

        self.df = df
        return df

    def get_colors(self, n_events: int):
        """Return a color palette adapted to the number of events.
        
        :param n_events int: The number of unique events to plot.
        
        :return: A list of colors.
        :rtype: list
        """
        return plt.cm.tab10.colors if n_events <= 10 else plt.cm.tab20.colors

    def plot_event_curve(self, ax: plt.Axes, ev_data: pd.DataFrame, ev_name: str, color: str) -> bool:
        """
        Plot the curve of an event on the given axis.

        :param ax plt.Axes: The matplotlib axis to plot on.
        :param ev_data pd.DataFrame: The DataFrame containing data for the specific event.
        :param ev_name str: The name of the event.
        :param color str: The color to use for the plot.

        :return: True if the event was plotted as markers only (no dose), False otherwise
        :rtype: bool
        """
        if ev_data["Dose_num"].notna().any():
            # Curve with actual dose value
            ax.plot(
                ev_data["Relative Time"],
                ev_data["Dose_num"],
                marker="o",
                label=ev_name,
                color=color,
            )
            return False
        else:
            # No dose -> mark only occurrences (y=1), without connecting points
            ax.scatter(
                ev_data["Relative Time"],
                [1] * len(ev_data),
                marker="x",
                s=80,
                label=f"{ev_name} (occurrence)",
                color=color,
            )
            return True

    def build_figure_for_event_type(self, sub: pd.DataFrame, ev_type: str):
        """Build the complete matplotlib figure for a given Event Type.
        
        :param sub pd.DataFrame: The subset of the DataFrame corresponding to the specific Event Type.
        :param ev_type str: The Event Type being processed."""
        events = sub["Event_clean"].unique()

        fig, ax = plt.subplots(figsize=(10, 6))
        colors = self.get_colors(len(events))
        has_marker_only_events = False

        for i, ev in enumerate(sorted(events)):
            ev_data = sub[sub["Event_clean"] == ev].sort_values("Relative Time")
            color = colors[i % len(colors)]
            is_marker_only = self.plot_event_curve(ax, ev_data, ev, color)
            has_marker_only_events = has_marker_only_events or is_marker_only

        self.style_axes(ax, ev_type, has_marker_only_events)
        fig.tight_layout()
        return fig

    def style_axes(self, ax: plt.Axes, ev_type: str, has_marker_only_events: bool):
        """Apply labels, title, legend and grid on the axis.
        
        :param ax plt.Axes: The matplotlib axis to style.
        :param ev_type str: The Event Type being processed.
        :param has_marker_only_events bool: Whether any events were plotted as markers only (no dose).
        """
        ax.set_xlabel("Relative Time (s)")
        ylabel = "Dose"
        if has_marker_only_events:
            ylabel += " / occurrence (y=1 = no dose)"
        ax.set_ylabel(ylabel)
        ax.set_title(f"Event Type : {ev_type}")
        ax.legend(loc="best", fontsize=9)
        ax.grid(True, alpha=0.3)

    def save_figure(self, fig: plt.Figure, ev_type: str) -> str:
        """Save the figure in FIGURES_DIR and return the output path.
        
        :param fig plt.Figure: The matplotlib figure to save.
        :param ev_type str: The Event Type being processed.
        
        :return: The path where the figure was saved.
        :rtype: str
        """
        safe_name = re.sub(r"[^\w\-]", "_", str(ev_type))
        out_path = os.path.join(FIGURES_DIR, f"events_{safe_name}.png")
        fig.savefig(out_path, dpi=150)
        plt.close(fig)
        return out_path

    def generate_all(self):
        """Generate and save a graph for each Event Type present in the data."""
        if self.df is None:
            self.load_data()

        event_types = self.df["Event Type"].dropna().unique()

        for ev_type in event_types:
            sub = self.df[self.df["Event Type"] == ev_type].copy()
            fig = self.build_figure_for_event_type(sub, ev_type)
            out_path = self.save_figure(fig, ev_type)
            log(f"-> Graph saved: {out_path}")

    def generate_graph(self):
        """Main function to load data and generate graphs for each Event Type."""
        self.load_data()
        self.generate_all()

if __name__ == "__main__":
    graph = GraphGenerator("/home/frigiel/Documents/VSCODE/Stage LIAM 2026/OR-Recorder-Transcriber/output/data/test_csv.csv")
    graph.generate_graph()