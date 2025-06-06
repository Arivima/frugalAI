
import streamlit as st
import logging
from app.config import Context
from app.api_call import classify_claim_cached

logger = logging.getLogger(__name__)

def dom():
    logger.info("App is starting")

    st.set_page_config(
        page_title="Climate Debunker", 
        page_icon="🌍"
    )

    st.title("Climate Disinformation Debunker")

    with st.form("claim_form"):

        st.markdown("Enter claim related to climate change:")

        claim = st.text_area(
            label="max 500 characters",
            placeholder="e.g., 'Climate change is a hoax.'"
        )

        submitted = st.form_submit_button("Check for disinformation")

        if submitted:
            results = None
            logger.info(f"event : st.button")
            if not claim.strip():
                st.warning("Please enter a claim to classify.")
            else:
                with st.spinner("Analyzing..."):
                    results = classify_claim_cached(claim.strip())   

            if results:
                if results.category == '0':
                    st.success(f"This claim is not related to climate or not considered to be disinformation")
                else:
                    climate_dict = Context.CLIMATE_DICT
                    st.warning(f"**This claim is considered to be climate disinformation.**")
                    st.markdown(f"**Category:** {results.category} ({climate_dict[results.category].split('-')[0]})")
                    st.markdown(f"**About this category :**")
                    st.markdown(f"{climate_dict[results.category].split('-')[1]}")
                    st.markdown(f"**Why it was categorized as such:**")
                    st.markdown(f"{results.explanation}")
            else:
                logger.error("classification failed")
                st.error("Unable to retrieve classification. Please try again later.")

    with st.expander("What do the categories mean?"):
        climate_dict = Context.CLIMATE_DICT
        for cat, desc in climate_dict.items():
            st.write(f"**{cat}**: {desc}")



if __name__ == "__main__":
    dom()
