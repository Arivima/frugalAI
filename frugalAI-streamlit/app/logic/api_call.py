
import requests
import logging
import streamlit as st
from pydantic import ValidationError
from typing import Optional
from app.logic.pydantic_models import (
    ClassifyRequest, 
    ClassifyResponse,
    FeedbackRequest
    )
from app.config import Context

logger = logging.getLogger(__name__)


@st.cache_data(show_spinner=False)
def classify_claim_cached(claim_text: str) -> Optional[ClassifyResponse]:
    def classify_claim(claim_text: str) -> Optional[ClassifyResponse] :
        try:
            payload = ClassifyRequest(user_claim=claim_text)
            logger.info(f"classify_claim | payload : {payload.model_dump()}")

            endpoint = Context.API_URL + 'classify'
            response = requests.post(endpoint, json=payload.model_dump())
            response.raise_for_status()
            data = response.json()

            validated_data = ClassifyResponse(**data)
            logger.info(f"classify_claim | response.model_name : {validated_data.model_name}")
            logger.info(f"classify_claim | response.user_claim : {validated_data.user_claim}")
            logger.info(f"classify_claim | response.category : {validated_data.category}")
            logger.info(f"classify_claim | response.explanation : {validated_data.explanation}")
            return validated_data
        
        except requests.exceptions.RequestException as e:
            st.error(f"API request failed: {e}")
            return None
        except ValidationError as e:
            st.error(f"Invalid format:\n{e}")
            return None
        except Exception as e:
            logger.error(f"error:\n{e}")
            st.error(f"error:\n{e}")
            return None
        
    return classify_claim(claim_text)



def send_feedback(claim: str, predicted_category : int, correct_category : int):
    try:
        payload = FeedbackRequest(
            user_claim=claim, 
            predicted_category=predicted_category,
            correct_category=correct_category
            )
        logger.info(f"send_feedback | payload : {payload.model_dump()}")

        endpoint = Context.API_URL + 'feedback'
        logger.info(endpoint)
        
        response = requests.post(endpoint, json=payload.model_dump())
        response.raise_for_status()
        logger.info(f"send_feedback | response : {response}")

    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed: {e}")
        st.error(f"API request failed: {e}")
        return None
    except ValidationError as e:
        logger.error(f"Invalid format:\n{e}")
        st.error(f"Invalid format:\n{e}")
        return None
    except Exception as e:
        logger.error(f"error:\n{e}")
        st.error(f"error:\n{e}")
        return None