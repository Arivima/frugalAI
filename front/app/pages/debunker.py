"""
Streamlit page for the Climate Disinformation Detector app.
Handles 
- claim input, 
- classification, 
- result display, and 
- user feedback.
"""

import logging

import streamlit as st
from app.context import Context
from app.logic.api_call import classify_claim_cached, send_feedback

logger = logging.getLogger(__name__)


class SessionState:
    """
    Utility class for managing and manipulating Streamlit session state variables
    """

    @staticmethod
    def init():
        """
        Initialize the session state with default values if they are not already set.
        Sets up keys for feedback status, dialog visibility, claim, and results.
        """
        defaults = {
            "feedback_status": None,  # None, 'correct', 'incorrect'
            "show_dialog": False,
            "current_claim": None,
            "current_results": None,
        }
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value

    @staticmethod
    def reset_feedback():
        """
        Reset only the feedback-related session state variables to default values.
        """
        st.session_state.feedback_status = None
        st.session_state.show_dialog = False

    @staticmethod
    def reset_state():
        """
        Reset all relevant session state variables to their default values.
        """
        st.session_state.feedback_status = None
        st.session_state.show_dialog = False
        st.session_state.current_claim = None
        st.session_state.current_results = None

    @staticmethod
    def reset_results():
        """
        Reset only the current_results session state variable.
        """
        st.session_state.current_results = None

    @staticmethod
    def debug():
        """
        For debugging : Print all session state variables and values to the app.
        """
        st.write("---")
        for k, v in st.session_state.items():
            st.write(k, "|", v)


def process_claim(claim):
    """
    Classifies the given claim and updates the session state with the results.
    """
    with st.spinner("Analyzing claim..."):
        results = classify_claim_cached(claim)

    if not results:
        st.error("Classification failed. Please try again.")
        logger.error("Classification API call failed")
        return

    st.session_state.current_claim = claim
    st.session_state.current_results = results


def display_results():
    """
    Display the classification results and explanation for the current claim.
    """
    claim = st.session_state.current_claim
    st.markdown(f"'*{claim}*'")

    results = st.session_state.current_results
    if results.category == "0":
        st.success("This claim is not considered climate disinformation")

        with st.container():
            st.markdown("**Why it was categorized as such:**")
            st.markdown(f"{results.explanation}")

    else:
        st.warning("**This claim is considered to be climate disinformation**")

        category_label = Context.CATEGORY_LABEL[results.category]
        category_description = Context.CATEGORY_DESCRIPTION[results.category]

        with st.container():
            st.markdown(f"**Category:** {results.category} - {category_label}")
            st.markdown(f"**About this category:** {category_description}")
            st.markdown("**Why it was categorized as such:**")
            st.markdown(f"{results.explanation}")


def handle_feedback_buttons():
    """
    Display feedback buttons for users to confirm or correct the classification.
    Updates session state based on user input and shows a thank you message.
    """
    if st.session_state.feedback_status is None:
        st.markdown("**Is this classification correct?**")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("👍 Correct", key="correct_btn", use_container_width=True):
                st.session_state.feedback_status = "correct"
                st.rerun()

        with col2:
            if st.button("👎 Incorrect", key="incorrect_btn", use_container_width=True):
                st.session_state.feedback_status = "incorrect"
                st.session_state.show_dialog = True
                st.rerun()
    else:
        message = (
            "Thank you for confirming!"
            if st.session_state.feedback_status == "correct"
            else "Thank you for your feedback!"
        )
        st.success(message)


@st.dialog("Share your Feedback")
def feedback_dialog():
    """
    Display a dialog for users to provide feedback by selecting the correct category for a claim.
    """
    st.write("What is the correct category for:")
    st.info(st.session_state.current_claim)

    selected_label = st.radio(
        "Select the correct category:",
        Context.CATEGORY_LABEL.values(),
        key="feedback_category",
    )
    selected_category = None
    for key, label in Context.CATEGORY_LABEL.items():
        if label == selected_label:
            selected_category = key
            break

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Submit Feedback", type="primary", use_container_width=True):
            send_feedback(
                claim=st.session_state.current_claim,
                predicted_category=st.session_state.current_results.category,
                assistant_explanation=st.session_state.current_results.explanation,
                correct_category=selected_category,
            )

            st.success("Thank you for your feedback!")
            st.session_state.show_dialog = False
            st.rerun()

    with col2:
        if st.button("Cancel", use_container_width=True):
            st.session_state.show_dialog = False
            st.rerun()


def app():
    """
    Main app function for the Climate Disinformation Detector.
    """
    SessionState.init()

    st.markdown("### Climate Disinformation Detector")
    st.markdown("Enter a climate-related claim to check for disinformation.")

    with st.form("claim_form", clear_on_submit=True):
        claim = st.text_area(
            "Enter your claim:",
            placeholder="e.g., 'Climate change is a natural cycle, not caused by humans'",
            max_chars=500,
            help="Maximum 500 characters",
            key="claim_input",
        )

        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button(
                "Analyze Claim", type="primary", use_container_width=True
            )
        with col2:
            reset = st.form_submit_button("Reset", use_container_width=True)

    if reset:
        SessionState.reset_state()
        st.rerun()

    if submitted:
        if not claim.strip():
            st.warning("Please enter a claim.")
        else:
            SessionState.reset_results()
            SessionState.reset_feedback()
            process_claim(claim.strip())

    if st.session_state.current_results:
        display_results()
        handle_feedback_buttons()

    if st.session_state.show_dialog and st.session_state.current_claim:
        feedback_dialog()

    # SessionState.debug()


if __name__ == "__main__":
    app()
