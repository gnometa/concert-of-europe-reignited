"""
V2LocKit Main Window
====================

The main application window with:
- File tree sidebar
- Validation results panel
- CSV viewer
- Toolbar actions
"""

from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QTreeWidget, QTreeWidgetItem, QTextEdit, QTableWidget, QTableWidgetItem,
    QToolBar, QStatusBar, QFileDialog, QMessageBox, QProgressBar,
    QLabel, QPushButton, QHeaderView, QTabWidget
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QAction, QIcon, QColor

from v2lockit.core.validator import Validator, ValidationReport, Severity, IssueType
from v2lockit.core.fixer import Fixer, FixReport
from v2lockit.core.scanner import Scanner, MissingKeysReport


class ValidationWorker(QThread):
    """Background worker for validation."""
    finished = Signal(object)  # ValidationReport
    progress = Signal(str)
    
    def __init__(self, path: Path):
        super().__init__()
        self.path = path
    
    def run(self):
        try:
            validator = Validator()
            self.progress.emit("Validating files...")
            report = validator.validate_directory(self.path)
            self.finished.emit(report)
        except Exception as e:
            self.progress.emit(f"Error: {e}")
            self.finished.emit(None)


class FixWorker(QThread):
    """Background worker for fixing."""
    finished = Signal(object)  # FixReport
    progress = Signal(str)
    
    def __init__(self, path: Path, dry_run: bool = False):
        super().__init__()
        self.path = path
        self.dry_run = dry_run
    
    def run(self):
        try:
            fixer = Fixer(create_backup=True, dry_run=self.dry_run)
            self.progress.emit("Fixing files...")
            report = fixer.fix_directory(self.path)
            self.finished.emit(report)
        except Exception as e:
            self.progress.emit(f"Error: {e}")
            self.finished.emit(None)


class ScanWorker(QThread):
    """Background worker for scanning missing keys."""
    finished = Signal(object)  # MissingKeysReport
    progress = Signal(str)
    
    def __init__(self, mod_path: Path, localisation_path: Path):
        super().__init__()
        self.mod_path = mod_path
        self.localisation_path = localisation_path
    
    def run(self):
        try:
            # First, collect all existing keys from localisation
            self.progress.emit("Collecting existing keys...")
            validator = Validator()
            report = validator.validate_directory(self.localisation_path)
            existing_keys = set()
            for result in report.file_results:
                existing_keys.update(result.keys)
            
            # Scan for missing keys
            self.progress.emit("Scanning game files...")
            scanner = Scanner(self.mod_path)
            missing_report = scanner.find_missing(existing_keys)
            self.finished.emit(missing_report)
        except Exception as e:
            self.progress.emit(f"Error: {e}")
            self.finished.emit(None)


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        
        self.current_path: Optional[Path] = None
        self.mod_path: Optional[Path] = None  # Parent of localisation folder
        self.validation_report: Optional[ValidationReport] = None
        
        self.setWindowTitle("V2LocKit - Victoria 2 Localisation Toolkit")
        self.setMinimumSize(1200, 700)
        
        self._create_actions()
        self._create_toolbar()
        self._create_ui()
        self._create_statusbar()
    
    def _create_actions(self):
        """Create toolbar actions."""
        self.open_action = QAction("📁 Open Folder", self)
        self.open_action.setShortcut("Ctrl+O")
        self.open_action.triggered.connect(self._on_open_folder)
        
        self.validate_action = QAction("✅ Validate", self)
        self.validate_action.setShortcut("Ctrl+V")
        self.validate_action.triggered.connect(self._on_validate)
        self.validate_action.setEnabled(False)
        
        self.fix_action = QAction("🔧 Fix All", self)
        self.fix_action.setShortcut("Ctrl+F")
        self.fix_action.triggered.connect(self._on_fix)
        self.fix_action.setEnabled(False)
        
        self.preview_action = QAction("👁 Preview Fix", self)
        self.preview_action.triggered.connect(self._on_preview_fix)
        self.preview_action.setEnabled(False)
        
        self.export_action = QAction("📄 Export Report", self)
        self.export_action.triggered.connect(self._on_export_report)
        self.export_action.setEnabled(False)
        
        self.scan_action = QAction("🔎 Find Missing Keys", self)
        self.scan_action.setShortcut("Ctrl+M")
        self.scan_action.triggered.connect(self._on_scan_missing)
        self.scan_action.setEnabled(False)
    
    def _create_toolbar(self):
        """Create main toolbar."""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        toolbar.addAction(self.open_action)
        toolbar.addSeparator()
        toolbar.addAction(self.validate_action)
        toolbar.addAction(self.preview_action)
        toolbar.addAction(self.fix_action)
        toolbar.addSeparator()
        toolbar.addAction(self.scan_action)
        toolbar.addSeparator()
        toolbar.addAction(self.export_action)
    
    def _create_ui(self):
        """Create main UI layout."""
        central = QWidget()
        self.setCentralWidget(central)
        
        layout = QHBoxLayout(central)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Main splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)
        
        # Left panel: File tree
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        left_layout.addWidget(QLabel("📁 Files"))
        
        self.file_tree = QTreeWidget()
        self.file_tree.setHeaderLabels(["File", "Status"])
        self.file_tree.setColumnWidth(0, 200)
        self.file_tree.itemClicked.connect(self._on_file_selected)
        left_layout.addWidget(self.file_tree)
        
        splitter.addWidget(left_panel)
        
        # Right panel: Tabs for different views
        right_panel = QTabWidget()
        
        # Tab 1: Issues
        issues_widget = QWidget()
        issues_layout = QVBoxLayout(issues_widget)
        issues_layout.setContentsMargins(5, 5, 5, 5)
        
        issues_layout.addWidget(QLabel("🔍 Validation Issues"))
        
        self.issues_table = QTableWidget()
        self.issues_table.setColumnCount(5)
        self.issues_table.setHorizontalHeaderLabels(["Severity", "File", "Line", "Type", "Message"])
        self.issues_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self.issues_table.setAlternatingRowColors(True)
        issues_layout.addWidget(self.issues_table)
        
        right_panel.addTab(issues_widget, "Issues")
        
        # Tab 2: CSV Viewer
        viewer_widget = QWidget()
        viewer_layout = QVBoxLayout(viewer_widget)
        viewer_layout.setContentsMargins(5, 5, 5, 5)
        
        self.csv_label = QLabel("📄 Select a file to view")
        viewer_layout.addWidget(self.csv_label)
        
        self.csv_table = QTableWidget()
        self.csv_table.setAlternatingRowColors(True)
        viewer_layout.addWidget(self.csv_table)
        
        right_panel.addTab(viewer_widget, "CSV Viewer")
        
        # Tab 3: Report
        report_widget = QWidget()
        report_layout = QVBoxLayout(report_widget)
        report_layout.setContentsMargins(5, 5, 5, 5)
        
        self.report_text = QTextEdit()
        self.report_text.setReadOnly(True)
        self.report_text.setFontFamily("Consolas")
        report_layout.addWidget(self.report_text)
        
        right_panel.addTab(report_widget, "Report")
        
        # Tab 4: Missing Keys
        missing_widget = QWidget()
        missing_layout = QVBoxLayout(missing_widget)
        missing_layout.setContentsMargins(5, 5, 5, 5)
        
        missing_layout.addWidget(QLabel("🔎 Missing Localisation Keys"))
        
        self.missing_table = QTableWidget()
        self.missing_table.setColumnCount(3)
        self.missing_table.setHorizontalHeaderLabels(["Key", "Category", "Source"])
        self.missing_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.missing_table.setAlternatingRowColors(True)
        missing_layout.addWidget(self.missing_table)
        
        right_panel.addTab(missing_widget, "Missing Keys")
        
        splitter.addWidget(right_panel)
        splitter.setSizes([300, 900])
    
    def _create_statusbar(self):
        """Create status bar."""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(200)
        self.progress_bar.hide()
        self.statusbar.addPermanentWidget(self.progress_bar)
        
        self.statusbar.showMessage("Ready — Open a localisation folder to begin")
    
    def _on_open_folder(self):
        """Handle open folder action."""
        path = QFileDialog.getExistingDirectory(
            self,
            "Select Localisation Folder",
            str(Path.home())
        )
        
        if path:
            self.current_path = Path(path)
            # Set mod_path as parent of localisation folder
            self.mod_path = self.current_path.parent
            self._load_file_tree()
            self.validate_action.setEnabled(True)
            self.scan_action.setEnabled(True)
            self.statusbar.showMessage(f"Loaded: {self.current_path}")
    
    def _load_file_tree(self):
        """Load files into the tree view."""
        self.file_tree.clear()
        
        if not self.current_path:
            return
        
        csv_files = sorted(self.current_path.glob("*.csv"))
        
        for csv_file in csv_files:
            item = QTreeWidgetItem([csv_file.name, "—"])
            item.setData(0, Qt.ItemDataRole.UserRole, csv_file)
            self.file_tree.addTopLevelItem(item)
        
        self.statusbar.showMessage(f"Found {len(csv_files)} CSV files")
    
    def _on_file_selected(self, item: QTreeWidgetItem, column: int):
        """Handle file selection in tree."""
        file_path = item.data(0, Qt.ItemDataRole.UserRole)
        if file_path:
            self._load_csv_viewer(file_path)
    
    def _load_csv_viewer(self, file_path: Path):
        """Load a CSV file into the viewer."""
        self.csv_label.setText(f"📄 {file_path.name}")
        
        try:
            # Read file
            with open(file_path, 'rb') as f:
                content = f.read()
            
            # Decode
            try:
                text = content.decode('cp1252')
            except UnicodeDecodeError:
                text = content.decode('utf-8', errors='replace')
            
            lines = text.split('\n')
            
            # Clear and set up table
            self.csv_table.clear()
            self.csv_table.setRowCount(len(lines))
            
            max_cols = 0
            for line in lines:
                parts = line.rstrip('\r').split(';')
                max_cols = max(max_cols, len(parts))
            
            self.csv_table.setColumnCount(max_cols)
            
            # Headers
            headers = ["Key", "EN", "FR", "DE", "—", "ES"] + [f"Col{i}" for i in range(7, max_cols + 1)]
            self.csv_table.setHorizontalHeaderLabels(headers[:max_cols])
            
            # Populate
            for row, line in enumerate(lines):
                parts = line.rstrip('\r').split(';')
                for col, value in enumerate(parts):
                    item = QTableWidgetItem(value)
                    # Highlight issues
                    if col == 0 and value:  # Key column
                        item.setBackground(QColor(40, 40, 60))
                    self.csv_table.setItem(row, col, item)
            
            self.csv_table.resizeColumnsToContents()
            
        except Exception as e:
            self.csv_label.setText(f"Error loading file: {e}")
    
    def _on_validate(self):
        """Run validation."""
        if not self.current_path:
            return
        
        self.progress_bar.setRange(0, 0)
        self.progress_bar.show()
        self.validate_action.setEnabled(False)
        self.statusbar.showMessage("Validating...")
        
        self.worker = ValidationWorker(self.current_path)
        self.worker.finished.connect(self._on_validation_complete)
        self.worker.progress.connect(lambda msg: self.statusbar.showMessage(msg))
        self.worker.start()
    
    def _on_validation_complete(self, report: Optional[ValidationReport]):
        """Handle validation completion."""
        self.progress_bar.hide()
        self.validate_action.setEnabled(True)
        
        if report is None:
            self.statusbar.showMessage("Validation failed")
            return
        
        self.validation_report = report
        
        # Update file tree with status
        for i in range(self.file_tree.topLevelItemCount()):
            item = self.file_tree.topLevelItem(i)
            file_path = item.data(0, Qt.ItemDataRole.UserRole)
            
            # Find result for this file
            for result in report.file_results:
                if result.file_path == file_path:
                    if result.error_count > 0:
                        item.setText(1, f"❌ {result.error_count}")
                        item.setForeground(1, QColor(255, 100, 100))
                    elif result.warning_count > 0:
                        item.setText(1, f"⚠️ {result.warning_count}")
                        item.setForeground(1, QColor(255, 200, 100))
                    else:
                        item.setText(1, "✅")
                        item.setForeground(1, QColor(100, 255, 100))
                    break
        
        # Populate issues table
        self._populate_issues_table(report)
        
        # Generate report text
        validator = Validator()
        self.report_text.setPlainText(validator.generate_summary(report))
        
        # Enable actions
        self.fix_action.setEnabled(report.total_errors > 0 or report.total_warnings > 0)
        self.preview_action.setEnabled(True)
        self.export_action.setEnabled(True)
        
        self.statusbar.showMessage(
            f"Validation complete: {report.total_errors} errors, {report.total_warnings} warnings"
        )
    
    def _populate_issues_table(self, report: ValidationReport):
        """Populate the issues table with validation results."""
        self.issues_table.setRowCount(0)
        
        all_issues = []
        for result in report.file_results:
            all_issues.extend(result.issues)
        all_issues.extend(report.cross_file_issues)
        
        self.issues_table.setRowCount(len(all_issues))
        
        for row, issue in enumerate(all_issues):
            # Severity
            sev_item = QTableWidgetItem(issue.severity.value.upper())
            if issue.severity == Severity.ERROR:
                sev_item.setBackground(QColor(100, 30, 30))
            else:
                sev_item.setBackground(QColor(80, 60, 20))
            self.issues_table.setItem(row, 0, sev_item)
            
            # File
            self.issues_table.setItem(row, 1, QTableWidgetItem(issue.file_path.name))
            
            # Line
            line_text = str(issue.line_number) if issue.line_number else "—"
            self.issues_table.setItem(row, 2, QTableWidgetItem(line_text))
            
            # Type
            type_text = issue.issue_type.value.replace("_", " ").title()
            self.issues_table.setItem(row, 3, QTableWidgetItem(type_text))
            
            # Message
            self.issues_table.setItem(row, 4, QTableWidgetItem(issue.message))
        
        self.issues_table.resizeColumnsToContents()
    
    def _on_preview_fix(self):
        """Preview fixes without applying."""
        if not self.current_path:
            return
        
        self.progress_bar.setRange(0, 0)
        self.progress_bar.show()
        self.statusbar.showMessage("Previewing fixes...")
        
        self.worker = FixWorker(self.current_path, dry_run=True)
        self.worker.finished.connect(self._on_fix_preview_complete)
        self.worker.start()
    
    def _on_fix_preview_complete(self, report: Optional[FixReport]):
        """Handle fix preview completion."""
        self.progress_bar.hide()
        
        if report is None:
            self.statusbar.showMessage("Preview failed")
            return
        
        fixer = Fixer()
        self.report_text.setPlainText(fixer.generate_summary(report))
        
        self.statusbar.showMessage(f"Preview complete: {report.files_fixed} files would be fixed")
    
    def _on_fix(self):
        """Apply fixes to all files."""
        if not self.current_path:
            return
        
        # Confirm
        reply = QMessageBox.question(
            self,
            "Confirm Fix",
            "This will modify files (backups will be created).\n\nProceed?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        self.progress_bar.setRange(0, 0)
        self.progress_bar.show()
        self.fix_action.setEnabled(False)
        self.statusbar.showMessage("Fixing files...")
        
        self.worker = FixWorker(self.current_path, dry_run=False)
        self.worker.finished.connect(self._on_fix_complete)
        self.worker.start()
    
    def _on_fix_complete(self, report: Optional[FixReport]):
        """Handle fix completion."""
        self.progress_bar.hide()
        self.fix_action.setEnabled(True)
        
        if report is None:
            self.statusbar.showMessage("Fix failed")
            return
        
        fixer = Fixer()
        self.report_text.setPlainText(fixer.generate_summary(report))
        
        # Re-validate
        self.statusbar.showMessage(f"Fixed {report.files_fixed} files — Re-validating...")
        self._on_validate()
    
    def _on_export_report(self):
        """Export validation report to file."""
        if not self.validation_report:
            return
        
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Report",
            str(Path.home() / "v2lockit_report.md"),
            "Markdown (*.md);;Text (*.txt)"
        )
        
        if path:
            try:
                validator = Validator()
                report_text = validator.generate_summary(self.validation_report)
                Path(path).write_text(report_text, encoding='utf-8')
                self.statusbar.showMessage(f"Report exported to: {path}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", str(e))

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
