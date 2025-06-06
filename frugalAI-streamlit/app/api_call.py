
import requests
import logging
import streamlit as st
from pydantic import ValidationError
from typing import Optional
from app.models import ClassifyRequest, ClassifyResponse
from app.config import API_URL

logger = logging.getLogger(__name__)

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

        logger.info(f"response: {response.json}")

        logger.info(f"classify_claim | response.model_name : {validated_data.model_name}")
        logger.info(f"classify_claim | response.user_claim : {validated_data.user_claim}")
        logger.info(f"classify_claim | response.category : {validated_data.category}")
        logger.info(f"classify_claim | response.explanation : {validated_data.explanation}")
        return validated_data
    
    except requests.exceptions.RequestException as e:
        st.error(f"API request failed: {e}")
        return None
    except ValidationError as e:
        st.error(f"Invalid claim input:\n{e}")
        return None
