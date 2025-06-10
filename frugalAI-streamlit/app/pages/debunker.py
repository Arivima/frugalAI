import streamlit as st
import logging
from app.logic.api_call import classify_claim_cached, send_feedback
from app.config import Context


logger = logging.getLogger(__name__)


class SessionState:    
    @staticmethod
    def init():
        defaults = {
            'feedback_status': None,  # None, 'correct', 'incorrect'
            'show_dialog': False,
            'current_claim': None,
            'current_results': None,
        }
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value

    @staticmethod
    def reset_feedback():
        st.session_state.feedback_status = None
        st.session_state.show_dialog = False

    @staticmethod
    def reset_state():
        st.session_state.feedback_status = None
        st.session_state.show_dialog = False
        st.session_state.current_claim = None
        st.session_state.current_results = None

    @staticmethod
    def reset_results():
        st.session_state.current_results = None
        



def process_claim(claim):

    with st.spinner("Analyzing claim..."):
        results = classify_claim_cached(claim)
    
    if not results:
        st.error("Classification failed. Please try again.")
        logger.error("Classification API call failed")
        return
    
    st.session_state.current_claim = claim
    st.session_state.current_results = results
    

def display_results():
    claim = st.session_state.current_claim
    st.markdown(f"'*{claim}*'")

    results = st.session_state.current_results
    if results.category == '0':
        st.success("This claim is not considered climate disinformation")
        return
    
    st.warning("**This claim is considered to be climate disinformation**")
    
    category_label = Context.CATEGORY_LABEL[results.category]
    category_description = Context.CATEGORY_DESCRIPTION[results.category]
    
    with st.container():
        st.markdown(f"**Category:** {results.category} - {category_label}")
        st.markdown(f"**About this category:** {category_description}")
        st.markdown(f"**Why it was categorized as such:**")
        st.markdown(f"{results.explanation}")


def handle_feedback_buttons():
    if st.session_state.feedback_status is None:
        st.markdown("**Is this classification correct?**")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("👍 Correct", key="correct_btn", use_container_width=True):
                st.session_state.feedback_status = 'correct'
                # do we do something here ?
                st.rerun()
        
        with col2:
            if st.button("👎 Incorrect", key="incorrect_btn", use_container_width=True):
                st.session_state.feedback_status = 'incorrect'
                st.session_state.show_dialog = True
                st.rerun()
    else:
        message = ("Thank you for confirming!" if st.session_state.feedback_status == 'correct' 
                  else "Thank you for your feedback!")
        st.success(message)
    

@st.dialog("Share your Feedback")
def feedback_dialog():
    st.write("What is the correct category for:")
    st.info(st.session_state.current_claim)
    
    selected_label = st.radio(
        "Select the correct category:",
        Context.CATEGORY_LABEL.values(),
        key="feedback_category"
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
                predicted_category=st.session_state.results.category,
                correct_category=selected_category
                )
            logger.info(f"Feedback received, category: {selected_category} for claim: {st.session_state.current_claim[:50]}")
            st.success("Thank you for your feedback!")
            st.session_state.show_dialog = False
            st.rerun()

    with col2:
        if st.button("Cancel", use_container_width=True):
            st.session_state.show_dialog = False
            st.rerun()



def app():

    SessionState.init()
    
    st.markdown("### Climate Disinformation Detector")
    st.markdown("Enter a climate-related claim to check for disinformation.")

    with st.form("claim_form", clear_on_submit=True):
        claim = st.text_area(
            "Enter your claim:",
            placeholder="e.g., 'Climate change is a natural cycle, not caused by humans'",
            max_chars=500,
            help="Maximum 500 characters",
            key="claim_input"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("Analyze Claim", type='primary', use_container_width=True)
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


if __name__ == "__main__":
    app()
