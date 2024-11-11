import logging
import os
import threading
import tkinter as tk
from datetime import datetime
from pathlib import Path
from queue import Queue

import customtkinter as ctk

from resources.styles.style_sheet import COLORS, FONTS, PADDING

from .gap_detector import GapDetector
from .output_generator import OutputGenerator


class GapDetectorUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.processing_queue = Queue()
        self.is_processing = False

        # Initialize variables
        self.min_gap_duration = ctk.StringVar(value="1.0")  # Changed to StringVar
        self.selected_files = []
        self.output_dir = Path("output")
        self.generate_gap_srt = ctk.BooleanVar(value=True)
        self.generate_summary = ctk.BooleanVar(value=True)

        # Configure the window
        self.title("Gap Detector")
        self.geometry("800x600")

        # Configure grid layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Set theme and appearance
        ctk.set_appearance_mode("system")  # Use system theme
        ctk.set_default_color_theme("blue")  # Use blue theme

        # Initialize UI components
        self._create_sidebar()
        self._create_main_area()

        logging.info("UI initialized successfully")

    def _create_sidebar(self) -> None:
        """Create the sidebar with controls"""
        # Create sidebar frame
        sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_rowconfigure(6, weight=1)  # Adjusted for new elements

        # Title
        title = ctk.CTkLabel(sidebar, text="Gap Detector", font=FONTS["HEADER"])
        title.grid(row=0, column=0, padx=PADDING["DEFAULT"], pady=(20, 10))

        # Min Gap Duration Frame
        gap_frame = ctk.CTkFrame(sidebar)
        gap_frame.grid(
            row=1, column=0, padx=PADDING["DEFAULT"], pady=(0, 10), sticky="ew"
        )

        gap_label = ctk.CTkLabel(
            gap_frame, text="Minimum Gap (seconds):", font=FONTS["NORMAL"]
        )
        gap_label.grid(row=0, column=0, padx=5, pady=5)

        self.gap_entry = ctk.CTkEntry(
            gap_frame,
            textvariable=self.min_gap_duration,
            width=80,
            font=FONTS["NORMAL"],
        )
        self.gap_entry.grid(row=1, column=0, padx=5, pady=5)

        # Browse button
        self.browse_btn = ctk.CTkButton(
            sidebar,
            text="Browse Files",
            command=self._browse_files,
            fg_color=COLORS["ACCENT"],
        )
        self.browse_btn.grid(row=2, column=0, padx=PADDING["DEFAULT"], pady=(0, 10))

        # Selected files label
        self.files_label = ctk.CTkLabel(
            sidebar, text="No files selected", font=FONTS["NORMAL"], wraplength=180
        )
        self.files_label.grid(row=3, column=0, padx=PADDING["DEFAULT"], pady=(0, 10))

        # Process button
        self.process_btn = ctk.CTkButton(
            sidebar,
            text="Process Files",
            command=self._process_files,
            state="disabled",
            fg_color=COLORS["PRIMARY"],
        )
        self.process_btn.grid(row=4, column=0, padx=PADDING["DEFAULT"], pady=(0, 10))

        # Settings section
        settings_frame = ctk.CTkFrame(sidebar)
        settings_frame.grid(
            row=5, column=0, padx=PADDING["DEFAULT"], pady=(0, 10), sticky="ew"
        )

        # Appearance mode
        appearance_label = ctk.CTkLabel(settings_frame, text="Appearance Mode:")
        appearance_label.grid(row=0, column=0, padx=5, pady=5)

        appearance_menu = ctk.CTkOptionMenu(
            settings_frame,
            values=["System", "Light", "Dark"],
            command=self._change_appearance_mode,
        )
        appearance_menu.grid(row=1, column=0, padx=5, pady=5)

        # Output options frame
        output_frame = ctk.CTkFrame(sidebar)
        output_frame.grid(
            row=6, column=0, padx=PADDING["DEFAULT"], pady=(0, 10), sticky="ew"
        )

        # Output directory button
        self.output_dir_btn = ctk.CTkButton(
            output_frame,
            text="Select Output Directory",
            command=self._select_output_dir,
            fg_color=COLORS["SECONDARY"],
        )
        self.output_dir_btn.grid(row=0, column=0, padx=5, pady=5)

        # Output options
        gap_srt_check = ctk.CTkCheckBox(
            output_frame,
            text="Generate Gap SRT",
            variable=self.generate_gap_srt,
        )
        gap_srt_check.grid(row=1, column=0, padx=5, pady=5)

        summary_check = ctk.CTkCheckBox(
            output_frame,
            text="Generate Summary",
            variable=self.generate_summary,
        )
        summary_check.grid(row=2, column=0, padx=5, pady=5)

    def _create_main_area(self) -> None:
        """Create the main area with output display"""
        # Create main frame
        main_frame = ctk.CTkFrame(self)
        main_frame.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=PADDING["DEFAULT"],
            pady=PADDING["DEFAULT"],
        )
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        # Create textbox for output
        self.output_text = ctk.CTkTextbox(main_frame, font=FONTS["NORMAL"], wrap="word")
        self.output_text.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # Make textbox read-only
        self.output_text.configure(state="disabled")

    def _validate_inputs(self) -> bool:
        """Validate all inputs before processing"""
        try:
            # Validate minimum gap duration
            min_gap = float(self.min_gap_duration.get())
            if min_gap <= 0:
                self._update_output(
                    "Error: Minimum gap duration must be greater than 0"
                )
                return False

            # Validate file selection
            if not self.selected_files:
                self._update_output("Error: No files selected")
                return False

            return True

        except ValueError:
            self._update_output("Error: Invalid minimum gap duration")
            return False

    def _browse_files(self) -> None:
        """Handle file browsing"""
        try:
            from tkinter import filedialog

            files = filedialog.askopenfilenames(
                title="Select SRT Files",
                filetypes=(("SRT files", "*.srt"), ("All files", "*.*")),
            )

            if files:  # files is a tuple of selected file paths
                self.selected_files = list(files)  # Convert tuple to list
                self.process_btn.configure(state="normal")  # Enable the process button
                self.files_label.configure(
                    text=f"Selected {len(files)} file{'s' if len(files) > 1 else ''}"
                )
                self._update_output(
                    f"Selected {len(files)} file{'s' if len(files) > 1 else ''}"
                )
                logging.info(f"Selected {len(files)} files")
            else:
                self.selected_files = []
                self.process_btn.configure(state="disabled")
                self.files_label.configure(text="No files selected")

        except Exception as e:
            self._update_output(f"Error selecting files: {str(e)}")
            logging.error(f"Error in file selection: {str(e)}", exc_info=True)

    def _process_files(self) -> None:
        """Handle file processing"""
        if not self._validate_inputs() or self.is_processing:
            return

        # Disable the process button and show processing state
        self.process_btn.configure(state="disabled")
        self.is_processing = True
        self._update_output("\nStarting processing...")

        # Start processing thread
        processing_thread = threading.Thread(
            target=self._process_files_thread, daemon=True
        )
        processing_thread.start()

        # Start checking for completion
        self.after(100, self._check_processing_complete)

    def _process_files_thread(self) -> None:
        """Handle file processing in a separate thread"""
        try:
            min_gap = float(self.min_gap_duration.get())

            # Create output directories
            gaps_dir = self.output_dir / "gaps"
            summaries_dir = self.output_dir / "summaries"
            gaps_dir.mkdir(parents=True, exist_ok=True)
            summaries_dir.mkdir(parents=True, exist_ok=True)

            # Initialize processors
            gap_detector = GapDetector(min_gap_duration=min_gap)
            output_generator = OutputGenerator()

            total_processed = 0
            total_failed = 0
            start_time = datetime.now()

            # Process each file
            for file_path in self.selected_files:
                try:
                    self.processing_queue.put(
                        ("status", f"\nProcessing {Path(file_path).name}...")
                    )
                    file_path = Path(file_path)

                    # Process file
                    gaps, stats = gap_detector.detect_gaps(file_path)

                    # Generate outputs
                    if self.generate_gap_srt.get():
                        gap_output_path = gaps_dir / f"{file_path.stem}_gaps.srt"
                        output_generator.generate_gap_srt(gaps, gap_output_path)
                        self.processing_queue.put(
                            ("status", f"Generated gap SRT: {gap_output_path.name}")
                        )

                    if self.generate_summary.get():
                        summary = output_generator.generate_summary(gaps, stats)
                        summary_path = summaries_dir / f"{file_path.stem}_summary.txt"
                        output_generator.save_summary(summary, summary_path)
                        self.processing_queue.put(
                            ("status", f"Generated summary: {summary_path.name}")
                        )

                    total_processed += 1

                except Exception as e:
                    total_failed += 1
                    self.processing_queue.put(
                        ("error", f"Error processing {file_path.name}: {str(e)}")
                    )

            # Calculate completion statistics
            elapsed_time = datetime.now() - start_time
            completion_message = (
                f"\nProcessing complete!"
                f"\nSuccessfully processed: {total_processed} files"
                f"\nFailed: {total_failed} files"
                f"\nElapsed time: {elapsed_time.total_seconds():.2f} seconds"
            )
            self.processing_queue.put(
                ("complete", (completion_message, total_processed))
            )

        except Exception as e:
            self.processing_queue.put(("error", f"Error during processing: {str(e)}"))
        finally:
            self.processing_queue.put(("done", None))

    def _check_processing_complete(self) -> None:
        """Check for processing updates and completion"""
        try:
            while True:
                msg_type, data = self.processing_queue.get_nowait()

                if msg_type == "status":
                    self._update_output(data)
                elif msg_type == "error":
                    self._update_output(data)
                elif msg_type == "complete":
                    message, total_processed = data
                    self._update_output(message)
                    if total_processed > 0:
                        self._add_open_output_button()
                elif msg_type == "done":
                    self.is_processing = False
                    self.process_btn.configure(state="normal")
                    return

                self.processing_queue.task_done()

        except tk.Empty:
            # No more updates, check again in 100ms
            self.after(100, self._check_processing_complete)

    def _add_open_output_button(self) -> None:
        """Add a button to open the output directory"""
        open_btn = ctk.CTkButton(
            self,
            text="Open Output Folder",
            command=lambda: (
                os.startfile(self.output_dir)
                if os.name == "nt"
                else os.system(f'xdg-open "{self.output_dir}"')
            ),
            fg_color=COLORS["SUCCESS"],
        )
        open_btn.grid(
            row=1, column=1, padx=PADDING["DEFAULT"], pady=(0, 10), sticky="e"
        )

    def _update_output(self, message: str) -> None:
        """Update the output text area"""
        self.output_text.configure(state="normal")
        self.output_text.insert("end", f"{message}\n")
        self.output_text.configure(state="disabled")
        self.output_text.see("end")

    def _change_appearance_mode(self, new_appearance_mode: str) -> None:
        """Change the appearance mode of the application"""
        ctk.set_appearance_mode(new_appearance_mode.lower())

    def _select_output_dir(self) -> None:
        """Handle output directory selection"""
        from tkinter import filedialog

        dir_path = filedialog.askdirectory(title="Select Output Directory")
        if dir_path:
            self.output_dir = Path(dir_path)
            self._update_output(f"Output directory set to: {self.output_dir}")

    def _update_process_button_state(self) -> None:
        """Update the state of the process button based on current selections"""
        if self.selected_files and len(self.selected_files) > 0:
            self.process_btn.configure(state="normal")
        else:
            self.process_btn.configure(state="disabled")

    def run(self) -> None:
        """Start the application"""
        self.mainloop()
