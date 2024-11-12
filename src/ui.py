import os
import tempfile
from pathlib import Path

import streamlit as st

# Import the necessary modules
from src.gap_detector import GapDetector
from src.output_generator import OutputGenerator


def run_app():
    # Set page configuration
    st.set_page_config(
        page_title="Silence Detector",
        page_icon="🎧",
        layout="centered",
        initial_sidebar_state="auto",
    )

    # App title
    st.title("🎧 Silence Detector")
    st.markdown(
        """
        Upload an SRT file to detect silences and gaps in the subtitles. Adjust the parameters as needed, and download the results.
        """
    )

    # File uploader
    uploaded_file = st.file_uploader("Upload your SRT file", type=["srt"])

    # Parameters input
    st.header("Parameters")
    min_gap_duration = st.number_input(
        "Minimum Gap Duration (seconds)",
        min_value=0.1,
        max_value=10.0,
        value=1.0,
        step=0.1,
        help="Specify the minimum duration of gaps to detect.",
    )

    # Process button
    process_button = st.button("Detect Silences and Gaps")

    if process_button:
        if uploaded_file is not None:
            # Actual processing
            with st.spinner("Processing..."):
                try:
                    # Read the uploaded file content
                    srt_content = uploaded_file.getvalue().decode(
                        "utf-8"
                    )  # assuming UTF-8 encoding

                    # Save the uploaded file to a temporary location
                    with tempfile.NamedTemporaryFile(
                        delete=False, suffix=".srt", mode="w", encoding="utf-8"
                    ) as temp_srt_file:
                        temp_srt_file.write(srt_content)
                        temp_srt_file_path = temp_srt_file.name

                    # Now process the file
                    min_gap = float(min_gap_duration)  # Ensure it's a float
                    gap_detector = GapDetector(min_gap_duration=min_gap)

                    gaps, stats = gap_detector.detect_gaps(Path(temp_srt_file_path))

                    # Generate outputs
                    output_generator = OutputGenerator()

                    # Generate summary
                    summary_text = output_generator.generate_summary(gaps, stats)

                    # Generate gap SRT and read its content
                    with tempfile.NamedTemporaryFile(
                        delete=False, suffix=".srt", mode="w", encoding="utf-8"
                    ) as gap_srt_file:
                        gap_srt_file_path = gap_srt_file.name
                        output_generator.generate_gap_srt(gaps, Path(gap_srt_file_path))

                    with open(gap_srt_file_path, "r", encoding="utf-8") as f:
                        gap_srt_content = f.read()

                    # Clean up temporary files
                    os.unlink(temp_srt_file_path)
                    os.unlink(gap_srt_file_path)

                    # Display summary
                    st.success("Processing complete!")
                    st.header("Summary")
                    st.text(summary_text)

                    # Download buttons
                    st.header("Download Results")
                    st.download_button(
                        label="Download Summary",
                        data=summary_text,
                        file_name="gap_summary.txt",
                        mime="text/plain",
                    )

                    st.download_button(
                        label="Download Gap SRT",
                        data=gap_srt_content,
                        file_name="gaps.srt",
                        mime="application/x-subrip",
                    )
                except Exception as e:
                    st.error(f"An error occurred during processing: {str(e)}")
        else:
            st.error("Please upload an SRT file before processing.")

    # Add some styling
    st.markdown(
        """
        <style>
        .st-button>button {
            background-color: #4CAF50;
            color: white;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
