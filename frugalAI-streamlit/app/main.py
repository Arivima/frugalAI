
import streamlit as st
import logging
from app.config import Context
from app.api_call import classify_claim

logger = logging.getLogger(__name__)



def dom():
    logger.info("App is starting")

    st.set_page_config(
        page_title="Climate Debunker", 
        page_icon="🌍"
    )

    st.title("Climate Disinformation Debunker")


    with st.form("claim_form"):
        # st.markdown("Enter claim related to climate change:")
        claim = st.text_area(
            label="Enter claim related to climate change:",
            placeholder="e.g., 'Climate change is a hoax.'"
        )
        submitted = st.form_submit_button("Check for disinformation")
        if submitted:
            logger.info(f"event : st.button")
            if not claim.strip():
                st.warning("Please enter a claim to classify.")
            else:
                with st.spinner("Analyzing..."):
                    result = classify_claim(claim.strip())

                if result:
                    if result.category == '0':
                        st.markdown(f"This claim is not related to climate or not considered to be disinformation")
                    else:
                        climate_dict = Context.CLIMATE_DICT

                        st.markdown(f"**This claim is considered climate disinformation.**")
                        st.markdown(f"**Category:** {result.category} ({climate_dict[result.category].split('-')[0]})")
                        st.markdown(f"**About this category :**")
                        st.markdown(f"{climate_dict[result.category].split('-')[1]}")
                        st.markdown(f"**Why it was categorized as such:**")
                        st.markdown(f"{result.explanation}")
                else:
                    logger.error("classification failed")
                    st.error("Unable to retrieve classification. Please try again later.")
            


if __name__ == "__main__":
    dom()
