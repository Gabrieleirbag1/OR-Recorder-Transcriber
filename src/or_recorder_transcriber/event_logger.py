import csv
import os
import datetime
from lite_logging.lite_logging import log
from PySide6.QtCore import Signal
from PySide6.QtCore import QObject
from or_recorder_transcriber.utils import DATA_DIR
from or_recorder_transcriber.graph import GraphGenerator

class EventLoggerCSV(QObject):
    """A class to log events to a CSV file with absolute and relative timestamps.
    
    :param output_dir str: The directory where the CSV file will be saved. Defaults to DATA_DIR."""

    file_content_update = Signal(object)
    def __init__(self, output_dir: str = DATA_DIR):
        """Initialize the EventLoggerCSV with the specified output directory.
        
        :param output_dir str: The directory where the CSV file will be saved. Defaults to DATA_DIR."""
        super().__init__()
        self.output_dir = output_dir

        self.file_content = {'Abs Time Vector': [], 'Relative Time': [], 'Events': [], 'Dose': [], 'Event Type': [], 'Selected Label': [], 'Score': [], 'Corrected Label': [], 'Medication Type': []}
        self.file_path = None
        self.create_csv_file()

    def create_csv_file(self):
        """Create a new CSV file with a timestamped filename and write the header row."""
        # filename must have been this format YYYY-MM-DD HHMM_ExcelData.csv
        self.filename = datetime.datetime.now().strftime("%Y-%m-%d %H%M_ExcelData.csv")
        self.file_path = os.path.join(self.output_dir, self.filename)
        with open(self.file_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Abs Time Vector', 'Relative Time', 'Events', 'Dose', 'Event Type', 'Selected Label', 'Score', 'Corrected Label', 'Medication Type'])

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
        
    def reset_session(self):
        """Reset the session by deleting the start time and creating a new CSV file."""
        self.generate_graphs()
        delattr(self, 'start_time')
        self.file_content = {'Abs Time Vector': [], 'Relative Time': [], 'Events': [], 'Dose': [], 'Event Type': [], 'Selected Label': [], 'Score': [], 'Corrected Label': [], 'Medication Type': []}
        self.create_csv_file()
        self.file_content_update.emit(None)
        
    def append_to_csv_file(self, event: str, dose: float, event_type: str, selected_label: str, score: float, corrected_label: str = None, medication_type: str | None = None, ):
        """Append a new row to the CSV file with the provided event information.

        :param event str: The event description.
        :param dose float: The dose associated with the event.
        :param event_type str: The Event Type ("Medication" / "Other"), already resolved by the caller from labels.json.
        :param selected_label str: The label selected for the event.
        :param score float: The confidence score for the selected label.
        :param corrected_label str: An optional Corrected Label for the event. Defaults to None.
        :param medication_type str | None: The type of medication, if applicable. Defaults to None. Should be perfusion or bolus.
        """
        abs_time_vector = datetime.datetime.now().strftime("%d-%b-%Y %H:%M:%S")
        relative_time = self.relative_time_counter()
        params = [abs_time_vector, relative_time, event, dose, event_type, selected_label, score, corrected_label, medication_type]
        with open(self.file_path, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([abs_time_vector, relative_time, event, dose, event_type, selected_label, score, corrected_label, medication_type])
            for i, (key, _) in enumerate(self.file_content.items()):
                self.file_content[key].append(params[i])
            self.file_content_update.emit(self.file_content)

    def update_data(self, new_value: str, column_name: str, row: int):
        """Update the table with the new value in the specified column.

        :param new_value str: The new value to set in the column.
        :param column_name str: The name of the column to update.
        :param row int: The row index of the cell being updated."""
        column_name = column_name if column_name != "Label" else "Corrected Label"
        if column_name in self.file_content:
            self.file_content[column_name][row] = new_value
            self.update_csv_file(new_value, column_name, row)
        else:
            log(f"Column {column_name} not found in file content.", level="WARNING")

    def update_csv_file(self, new_value: str, column_name: str, row: int):
        """Update a specific cell in the CSV file on disk.

        :param new_value str: The new value to write.
        :param column_name str: The column to update.
        :param row int: The row index (0-based, matching self.file_content lists).
        """
        with open(self.file_path, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            rows = list(reader)

        col_index = list(self.file_content.keys()).index(column_name)
        target_row = row + 1  # +1 to skip header row

        if target_row >= len(rows):
            log(
                f"Row {row} not found in CSV file (only {len(rows) - 1} data rows present). "
                f"Skipping update.",
                level="WARNING",
            )
            return

        # Pad the row if it's shorter than expected (defensive, shouldn't normally happen)
        if col_index >= len(rows[target_row]):
            rows[target_row].extend([None] * (col_index - len(rows[target_row]) + 1))

        rows[target_row][col_index] = new_value

        with open(self.file_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(rows)

    def delete_row(self, row: int):
        """Delete a specific row from the CSV file and update the internal file_content.

        :param row int: The row index (0-based, matching self.file_content lists) to delete."""
        with open(self.file_path, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            rows = list(reader)

        target_row = row + 1  # +1 to skip header row

        if target_row >= len(rows):
            log(
                f"Row {row} not found in CSV file (only {len(rows) - 1} data rows present). "
                f"Skipping deletion.",
                level="WARNING",
            )
            return

        del rows[target_row]

        with open(self.file_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(rows)

        # Update internal file_content
        for key in self.file_content:
            if row < len(self.file_content[key]):
                del self.file_content[key][row]

    def generate_graphs(self):
        """Generate one graph per distinct Event Type found in the CSV file."""
        graph_generator = GraphGenerator(self.file_path, self.filename)
        graph_generator.generate_graph()