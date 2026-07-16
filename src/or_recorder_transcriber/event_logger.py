import csv
import os
import datetime
from or_recorder_transcriber.utils import DATA_DIR
from or_recorder_transcriber.graph import GraphGenerator

class EventLoggerCSV:
    """A class to log events to a CSV file with absolute and relative timestamps.
    
    :param output_dir str: The directory where the CSV file will be saved. Defaults to DATA_DIR."""
    def __init__(self, output_dir: str = DATA_DIR):
        """Initialize the EventLoggerCSV with the specified output directory.
        
        :param output_dir str: The directory where the CSV file will be saved. Defaults to DATA_DIR."""
        self.output_dir = output_dir

        self.file_path = None
        self.file_path = None
        self.create_csv_file()

    def create_csv_file(self):
        """Create a new CSV file with a timestamped filename and write the header row."""
        # filename must have been this format YYYY-MM-DD HHMM_ExcelData.csv
        self.filename = datetime.datetime.now().strftime("%Y-%m-%d %H%M_ExcelData.csv")
        self.file_path = os.path.join(self.output_dir, self.filename)
        with open(self.file_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Abs Time Vector', 'Relative Time', 'Events', 'Dose', 'Event Type', 'Selected Label', 'Score', 'Corrected label'])

    def relative_time_counter(self) -> float:
        """Calculate the relative time in seconds since the first event was logged.
        
        :return: The relative time in seconds since the first event was logged.
        :rtype: float"""
        if not hasattr(self, 'start_time'):
            self.start_time = datetime.datetime.now()
            return 0
        else:
            current_time = datetime.datetime.now()
            relative_time = (current_time - self.start_time).total_seconds()
            relative_time = round(relative_time, 0)
            return relative_time
        
    def append_to_csv_file(self, event: str, dose: float, event_type: str, selected_label: str, score: float, corrected_label: str = None):
        """Append a new row to the CSV file with the provided event information.

        :param event str: The event description.
        :param dose float: The dose associated with the event.
        :param event_type str: The type of event.
        :param selected_label str: The label selected for the event.
        :param score float: The confidence score for the selected label.
        :param corrected_label str: An optional corrected label for the event. Defaults to None."""
        abs_time_vector = datetime.datetime.now().strftime("%d-%b-%Y %H:%M:%S")
        relative_time = self.relative_time_counter()
        with open(self.file_path, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([abs_time_vector, relative_time, event, dose, event_type, selected_label, score, corrected_label])

    def generate_graphs(self):
        """Generate graphs for each unique Event Type in the CSV file."""
        graph_generator = GraphGenerator(self.file_path, self.filename)
        graph_generator.generate_graph()