"""
Main entry point for the Climate Debunker Streamlit app.
Sets up logging and page configuration.
"""

import logging

import streamlit as st

from shared.config import setup_logging

setup_logging()

logger = logging.getLogger(__name__)


def root():
    logger.info("App is starting")

    st.set_page_config(
        page_title="Climate Debunker",
        page_icon="🌍",
        initial_sidebar_state="expanded",  # "collapsed"
    )


if __name__ == "__main__":
    root()
