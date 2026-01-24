"""Append scan handler methods to main_window.py"""

scan_handlers = '''
    def _on_scan_missing(self):
        """Scan for missing localisation keys."""
        if not self.current_path or not self.mod_path:
            return
        
        self.progress_bar.setRange(0, 0)
        self.progress_bar.show()
        self.scan_action.setEnabled(False)
        self.statusbar.showMessage("Scanning for missing keys...")
        
        self.worker = ScanWorker(self.mod_path, self.current_path)
        self.worker.finished.connect(self._on_scan_complete)
        self.worker.progress.connect(lambda msg: self.statusbar.showMessage(msg))
        self.worker.start()
    
    def _on_scan_complete(self, report):
        """Handle scan completion."""
        self.progress_bar.hide()
        self.scan_action.setEnabled(True)
        
        if report is None:
            self.statusbar.showMessage("Scan failed")
            return
        
        # Populate missing keys table
        self.missing_table.setRowCount(0)
        self.missing_table.setRowCount(report.total_missing)
        
        for row, missing in enumerate(report.missing_keys):
            self.missing_table.setItem(row, 0, QTableWidgetItem(missing.key))
            self.missing_table.setItem(row, 1, QTableWidgetItem(missing.category))
            self.missing_table.setItem(row, 2, QTableWidgetItem(missing.source_file.name))
        
        self.missing_table.resizeColumnsToContents()
        
        self.statusbar.showMessage(f"Scan complete: {report.total_missing} missing keys found")
'''

with open('src/v2lockit/ui/main_window.py', 'a', encoding='utf-8') as f:
    f.write(scan_handlers)

print("Scan handlers appended successfully!")
