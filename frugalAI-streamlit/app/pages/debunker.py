import streamlit as st
import logging
from app.logic.api_call import classify_claim_cached
from app.config import Context

logger = logging.getLogger(__name__)


def app():
    st.markdown("### Detect climate disinformation")
    
    with st.form("claim_form"):

        st.markdown("Enter claim related to climate change:")

        claim = st.text_area(
            label="max 500 characters",
            placeholder="e.g., 'Climate change is a hoax.'",
            max_chars=500
        )

        submitted = st.form_submit_button("Check for disinformation")

        if submitted:
            results = None
            logger.info(f"event : st.button form submitted")
            if not claim.strip():
                st.warning("Please enter a claim to classify.")
            else:
                with st.spinner("Analyzing..."):
                    results = classify_claim_cached(claim.strip())   

                if results:
                    if results.category == '0':
                        st.success(f"This claim is not related to climate or not considered to be disinformation")
                    else:
                        category_label = Context.CATEGORY_LABEL[results.category]
                        category_description = Context.CATEGORY_DESCRIPTION[results.category]
                        st.warning(f"**This claim is considered to be climate disinformation.**")
                        st.markdown(f"**Category:** {results.category} ({category_label})")
                        st.markdown(f"**About this category :**")
                        st.markdown(f"{category_description}")
                        st.markdown(f"**Why it was categorized as such:**")
                        st.markdown(f"{results.explanation}")
                else:
                    logger.error("classification failed")
                    st.error("Unable to retrieve classification. Please try again.")


if __name__ == "__main__":
    app()