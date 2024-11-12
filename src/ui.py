import os
import tempfile
from pathlib import Path

import streamlit as st

from src.gap_detector import GapDetector
from src.output_generator import OutputGenerator


def initialize_session_state():
    if "processing_complete" not in st.session_state:
        st.session_state["processing_complete"] = False
    if "summary_text" not in st.session_state:
        st.session_state["summary_text"] = ""
    if "detailed_summary" not in st.session_state:
        st.session_state["detailed_summary"] = ""
    if "gap_srt_content" not in st.session_state:
        st.session_state["gap_srt_content"] = ""


def display_header():
    st.title("🎧 Silence Detector")
    st.markdown(
        """
        Upload an SRT file to detect silences and gaps in the subtitles. Adjust the parameters as needed, and download the results.
        """
    )


def file_uploader():
    uploaded_file = st.file_uploader("Upload your SRT file", type=["srt"])
    return uploaded_file


def process_file(uploaded_file, min_gap_duration):
    if uploaded_file is not None:
        with st.spinner("Processing..."):
            try:
                srt_content = uploaded_file.getvalue().decode("utf-8")

                with tempfile.NamedTemporaryFile(
                    delete=False, suffix=".srt", mode="w", encoding="utf-8"
                ) as temp_srt_file:
                    temp_srt_file.write(srt_content)
                    temp_srt_file_path = temp_srt_file.name

                min_gap = float(min_gap_duration)
                gap_detector = GapDetector(min_gap_duration=min_gap)

                gaps, stats = gap_detector.detect_gaps(Path(temp_srt_file_path))

                output_generator = OutputGenerator()

                summary_text = output_generator.generate_detection_summary(stats)
                detailed_summary = output_generator.generate_detailed_summary(
                    gaps, stats
                )

                with tempfile.NamedTemporaryFile(
                    delete=False, suffix=".srt", mode="w", encoding="utf-8"
                ) as gap_srt_file:
                    gap_srt_file_path = gap_srt_file.name
                    output_generator.generate_gap_srt(gaps, Path(gap_srt_file_path))

                with open(
                    gap_srt_content := gap_srt_file_path, "r", encoding="utf-8"
                ) as f:
                    gap_srt_content = f.read()

                os.unlink(temp_srt_file_path)
                os.unlink(gap_srt_file_path)

                st.session_state["summary_text"] = summary_text
                st.session_state["detailed_summary"] = detailed_summary
                st.session_state["gap_srt_content"] = gap_srt_content
                st.session_state["processing_complete"] = True

                return True

            except Exception as e:
                st.error(f"An error occurred during processing: {str(e)}")
                return False
    else:
        st.error("Please upload an SRT file before processing.")
        return False


def display_results():
    if st.session_state.get("processing_complete"):
        st.success("Processing complete!")
        with st.expander("View Summary"):
            st.markdown(st.session_state["summary_text"])

        st.header("Download Results")
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="Download Detailed Summary",
                data=st.session_state["detailed_summary"],
                file_name="gap_detailed_summary.md",
                mime="text/markdown",
            )
        with col2:
            st.download_button(
                label="Download Gap SRT",
                data=st.session_state["gap_srt_content"],
                file_name="gaps.srt",
                mime="application/x-subrip",
            )


def add_custom_styles():
    st.markdown(
        """
        <style>
        .stButton > button {
            background-color: #4CAF50;
            color: white;
            padding: 0.75em 1.5em;
            font-size: 1em;
            border-radius: 8px;
            border: none;
        }
        .stButton > button:hover {
            background-color: #45a049;
            color: white;
        }
        .stDownloadButton > button {
            background-color: #2196F3;
            color: white;
            padding: 0.75em 1.5em;
            font-size: 1em;
            border-radius: 8px;
            border: none;
        }
        .stDownloadButton > button:hover {
            background-color: #0b7dda;
            color: white;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def run_app():
    st.set_page_config(
        page_title="Silence Detector",
        page_icon="🎧",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    initialize_session_state()
    add_custom_styles()
    display_header()

    with st.sidebar:
        st.header("Parameters")
        min_gap_duration = st.number_input(
            "Minimum Gap Duration (seconds)",
            min_value=0.1,
            max_value=10.0,
            value=1.0,
            step=0.1,
            help="Specify the minimum duration of gaps to detect.",
        )
        st.markdown("---")
        with st.expander("About"):
            st.markdown(
                """
                **Silence Detector** helps you find silent gaps in your subtitles.
                Upload your SRT file, set the minimum gap duration, and detect silences.
                """
            )

        with st.expander("Subtitle Resources"):
            st.markdown(
                """
            Here are some popular free subtitle providers:

            - **OpenSubtitles**: Offers a vast collection of subtitles in multiple languages for movies and TV series. [Visit OpenSubtitles](https://www.opensubtitles.org/)

            - **Subscene**: Provides user-contributed subtitles for a wide range of films and shows. [Visit Subscene](https://subscene.com/)

            - **YIFY Subtitles**: Specializes in movie subtitles across various languages. [Visit YIFY Subtitles](https://www.yifysubtitles.com/)

            - **Podnapisi**: Features over 2 million subtitles for movies and TV series in multiple languages. [Visit Podnapisi](https://www.podnapisi.net/)

            - **Addic7ed**: Focuses on TV show subtitles, offering timely releases often synchronized with new episodes. [Visit Addic7ed](https://www.addic7ed.com/)

            - **TVsubtitles**: Dedicated to TV series, providing subtitles for a broad spectrum of shows. [Visit TVsubtitles](https://www.tvsubtitles.net/)

            - **Moviesubtitles.org**: Specializes in movie subtitles with a straightforward interface for quick downloads. [Visit Moviesubtitles.org](https://www.moviesubtitles.org/)
            """
            )

    st.header("Upload SRT File")
    col1, col2 = st.columns([3, 1])
    with col1:
        uploaded_file = file_uploader()
    with col2:
        st.write("")
        st.write("")
        process_button = st.button("Detect Silences and Gaps")

    if process_button:
        success = process_file(uploaded_file, min_gap_duration)
        if success:
            display_results()
    elif st.session_state.get("processing_complete"):
        display_results()


if __name__ == "__main__":
    run_app()
