# TODO V1
# gestion du cache et du state
# tests ?

# TODO V2
# feedback loop

# TODO V3
# onglet dashboard comparaison modeles

import streamlit as st
import requests
import logging
from pydantic import BaseModel, ValidationError, Field
from typing import Optional, Annotated


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)


API_URL = "http://127.0.0.1:8000/classify"


class ClassifyRequest(BaseModel):
    user_claim: str = Field(..., strip_whitespace=True, min_length=1)

class ClassifyResponse(BaseModel):
    model_name: str
    user_claim: str
    claim_category: str


climate_dict = {
    "0": "No relevant claim detected or claims that don't fit other categories",
    "1": "Claims denying the occurrence of global warming and its effects - Global warming is not happening. Climate change is NOT leading to melting ice (such as glaciers, sea ice, and permafrost), increased extreme weather, or rising sea levels. Cold weather also shows that climate change is not happening",
    "2": "Claims denying human responsibility in climate change - Greenhouse gases from humans are not the causing climate change.",
    "3": "Claims minimizing or denying negative impacts of climate change - The impacts of climate change will not be bad and might even be beneficial.",
    "4": "Claims against climate solutions - Climate solutions are harmful or unnecessary",
    "5": "Claims questioning climate science validity - Climate science is uncertain, unsound, unreliable, or biased.",
    "6": "Claims attacking climate scientists and activists - Climate scientists and proponents of climate action are alarmist, biased, wrong, hypocritical, corrupt, and/or politically motivated.",
    "7": "Claims promoting fossil fuel necessity - We need fossil fuels for economic growth, prosperity, and to maintain our standard of living.",
}


def classify_claim(claim_text: str) -> Optional[ClassifyResponse] :
    try:
        payload = ClassifyRequest(user_claim=claim_text)
        logger.info(f"classify_claim | payload : {payload.model_dump()}")

        response = requests.post(API_URL, json=payload.model_dump())
        response.raise_for_status()

        data = response.json()
        logger.info(f"classify_claim | raw response JSON: {data}")

        validated_data = ClassifyResponse(**data)
        logger.info(f"classify_claim | validated response: {validated_data}")

        # mock_response = ClassifyResponse(
        #     model_name="Qwen 2.5 1.5B",
        #     user_claim=claim_text,
        #     claim_category='6',
        #     )
        # response = mock_response

        logger.info(f"response: {response.json}")

        logger.info(f"classify_claim | response.model_name : {validated_data.model_name}")
        logger.info(f"classify_claim | response.user_claim : {validated_data.user_claim}")
        logger.info(f"classify_claim | response.claim_category : {validated_data.claim_category}")
        return validated_data
    
    except requests.exceptions.RequestException as e:
        st.error(f"API request failed: {e}")
        return None
    except ValidationError as e:
        st.error(f"Invalid claim input:\n{e}")
        return None



def main():
    logger.info("App is starting")

    st.set_page_config(
        page_title="Climate Debunker", 
        page_icon="🌍"
    )

    st.title("Climate Disinformation Debunker")


    with st.form("claim_form"):
        st.markdown("Enter claim related to climate change:")
        claim = st.text_area(
            label="",
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
                    # if result.claim_category == '0':
                    #     st.markdown(f"This claim is not related to climate or not considered to be disinformation")
                    # else:
                        # st.markdown(f"**This claim is considered climate disinformation.**")
                        # st.markdown(f"**Category:** {result.claim_category}")
                    st.markdown(f"Response : {result.claim_category}")
                else:
                    logger.error("classification failed")
                    st.error("Unable to retrieve classification. Please try again later.")
            


if __name__ == "__main__":
    main()
