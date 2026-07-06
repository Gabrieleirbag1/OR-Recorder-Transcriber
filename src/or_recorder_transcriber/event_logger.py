#2026-03-09 1009_ExcelData
#Abs Time Vector	    Relative Time	Events                        Dose      Type                    Label selected  Score   Corrected label
#23-Oct-2023 11:03:14   0               pr 0.05 @23-10-2023 11:03:14  0.05      médication/op events    PP              0.999   NoneP       

import csv
import os
import datetime
from or_recorder_transcriber.utils import DATA_DIR

class EventLoggerCSV:
    def __init__(self, output_dir=DATA_DIR):
        self.output_dir = output_dir
        self.file_path = None
        self.create_csv_file()

    def create_csv_file(self):
        # filename must have been this format YYYY-MM-DD HHMM_ExcelData.csv
        filename = datetime.datetime.now().strftime("%Y-%m-%d %H%M_ExcelData.csv")
        self.file_path = os.path.join(self.output_dir, filename)
        with open(self.file_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Abs Time Vector', 'Relative Time', 'Events', 'Dose', 'Event Type', 'Selected Label', 'Score', 'Corrected label'])

    def relative_time_counter(self):
        if not hasattr(self, 'start_time'):
            self.start_time = datetime.datetime.now()
            return 0
        else:
            current_time = datetime.datetime.now()
            relative_time = (current_time - self.start_time).total_seconds()
            relative_time = round(relative_time, 0)
            return relative_time
        
    def append_to_csv_file(self, event, dose, event_type, selected_label, score, corrected_label=None):
        abs_time_vector = datetime.datetime.now().strftime("%d-%b-%Y %H:%M:%S")
        relative_time = self.relative_time_counter()
        with open(self.file_path, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([abs_time_vector, relative_time, event, dose, event_type, selected_label, score, corrected_label])