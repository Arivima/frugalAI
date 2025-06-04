# TODO V1
# logger
# api fonctionnelle
# gestion du cache et du state

# TODO V2
# feedback loop

# TODO V3
# onglet dashboard comparaison modeles

import streamlit as st
import requests
from pydantic import BaseModel, ValidationError, Field
from typing import Optional, Annotated


API_URL = "https://mock-api.example.com/classify"

class PayloadModel(BaseModel):
    """Payload should be a str, non empty, min length : 1, strips whitespace"""
    user_claim: Annotated[str, Field(strip_whitespace=True, min_length=1)]


class ResponseModel(BaseModel):
    """Response should have specific fields"""
    model_name: str
    model_description: str
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

def classify_claim(claim_text: str) -> Optional[ResponseModel] :
    """
    Send the user's claim to the API for classification.
    Return the response as JSON with a specific schema.
    """
    try:
        print("claim_text : ", claim_text)
        payload = PayloadModel(user_claim=claim_text)
        print("payload : ", payload.model_dump())

        #response = requests.post(API_URL, json=payload.model_dump())
        #response.raise_for_status()
        #return response.json()

        mock_response = ResponseModel(
            model_name="Qwen 2.5 1.5B",
            model_description="distilled from Phi3",
            user_claim=claim_text,
            claim_category='6',
            )
        response = mock_response
        print("response : ", response)
        return response
    
    except requests.exceptions.RequestException as e:
        st.error(f"API request failed: {e}")
        return None
    except ValidationError as e:
        st.error(f"Invalid claim input:\n{e}")
        return None



def main():
    """Classify single claims into climate disinformation categories"""
    
    st.set_page_config(
        page_title="Climate Disinformation Debunker", 
        page_icon="🌍"
    )

    st.title("Climate Disinformation Debunker")

    claim = st.text_area(
        label="Enter a climate-related claim below, we will assess if it is climate disonformation and which type", 
        placeholder="e.g., 'Climate change is a hoax.'"
    )

    if st.button("Check for disinformation"):
        if not claim.strip():
            st.warning("Please enter a claim to classify.")
        else:
            with st.spinner("Classifying..."):
                result = classify_claim(claim.strip())

            if result:
                st.markdown(f'_"{result.user_claim}"_')
                if result.claim_category is '0':
                    st.markdown(f"This claim is not related to climate or not considered to be disinformation")
                else:
                    st.markdown(f"**This claim is considered climate disinformation.**")
                    st.markdown(f"**Category:** {result.claim_category}")
                    st.markdown(f"{climate_dict[result.claim_category]}")
                st.markdown(f"**Classified by:** {result.model_name} ({result.model_description})")
            else:
                st.error("Unable to retrieve classification. Please try again later.")


if __name__ == "__main__":
    main()
