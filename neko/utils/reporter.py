import json
import csv
import os
from .logger import get_logger

class NekoReporter:
    def __init__(self, output_file, format='json'):
        self.output_file = output_file
        self.format = format.lower()
        self.logger = get_logger()

    def report(self, data):
        if not self.output_file:
            return

        try:
            if self.format == 'json':
                self._save_json(data)
            elif self.format == 'csv':
                self._save_csv(data)
            else:
                self.logger.error(f"Unsupported report format: {self.format}")
        except Exception as e:
            self.logger.error(f"Failed to save report: {e}")

    def _save_json(self, data):
        with open(self.output_file, 'w') as f:
            json.dump(data, f, indent=4)
        self.logger.success(f"Report saved to {self.output_file} (JSON)")

    def _save_csv(self, data):
        if not data:
            return
        
        # Handle list of dicts
        if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
            keys = data[0].keys()
            with open(self.output_file, 'w', newline='') as f:
                dict_writer = csv.DictWriter(f, fieldnames=keys)
                dict_writer.writeheader()
                dict_writer.writerows(data)
        # Handle single dict
        elif isinstance(data, dict):
             with open(self.output_file, 'w', newline='') as f:
                w = csv.DictWriter(f, data.keys())
                w.writeheader()
                w.writerow(data)
        else:
            self.logger.error("Data format not suitable for CSV")
            return
            
        self.logger.success(f"Report saved to {self.output_file} (CSV)")
