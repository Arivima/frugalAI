import streamlit as st
import logging
from app.context import Context

logger = logging.getLogger(__name__)


def app():
    st.markdown("### What do the categories mean?")
    labels = Context.CATEGORY_LABEL.values()
    descriptions = Context.CATEGORY_DESCRIPTION.values()
    for i, (label, desc) in enumerate(zip(labels, descriptions)):
        st.markdown(f"- **{i} - {label}**: {desc}")


if __name__ == "__main__":
    app()