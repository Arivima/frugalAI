"""
This module provides functions for interacting with the backend API,
- claim classification with caching
- feedback submission
"""

import logging
from typing import Optional

import requests
import streamlit as st
from app.context import Context
from pydantic import ValidationError

from shared.pydantic_models import ClassifyRequest, ClassifyResponse, FeedbackRequest

logger = logging.getLogger(__name__)


@st.cache_data(show_spinner=False)
def classify_claim_cached(claim_text: str) -> Optional[ClassifyResponse]:
    """
    Sends a claim to the backend API for classification and returns the result.
    Cached to avoid redundant API calls for the same input.

    Args:
        claim_text (str): The claim to classify.

    Returns:
        Optional[ClassifyResponse]: The classification result, or None if there is an error.
    """
    def classify_claim(claim_text: str) -> Optional[ClassifyResponse]:
        try:
            payload = ClassifyRequest(user_claim=claim_text)
            logger.info(
                "classify_claim | user_claim : %s",
                payload.model_dump()["user_claim"][:50],
            )

            endpoint = Context.API_URL + "classify"
            response = requests.post(endpoint, json=payload.model_dump(), timeout=30)
            response.raise_for_status()
            data = response.json()

            validated_data = ClassifyResponse(**data)
            logger.info(
                "classify_claim | response.model_name : %s", validated_data.model_name
            )
            logger.info(
                "classify_claim | response.user_claim : %s",
                validated_data.user_claim[:50],
            )
            logger.info(
                "classify_claim | response.category : %s", validated_data.category
            )
            logger.info(
                "classify_claim | response.explanation : %s", validated_data.explanation
            )
            return validated_data

        except requests.exceptions.RequestException as e:
            logger.error("API request failed: %s", e)
            st.error(f"API request failed: {e}")
            return None
        except ValidationError as e:
            logger.error("Invalid format:\n%s", e)
            st.error(f"Invalid format:\n{e}")
            return None
        except Exception as e:
            logger.error("Unexpected error:\n%s", e)
            st.error(f"Unexpected error:\n{e}")
            return None

    return classify_claim(claim_text)


def send_feedback(
    claim: str,
    predicted_category: int,
    assistant_explanation: str,
    correct_category: int,
):
    """
    Sends user feedback about a claim classification to the API.

    Args:
        claim (str): The original user claim.
        predicted_category (int): The category predicted by the assistant.
        assistant_explanation (str): The assistant's explanation for the prediction.
        correct_category (int): The correct category as provided by the user.

    Returns:
        None
    """
    try:
        payload = FeedbackRequest(
            user_claim=claim,
            predicted_category=predicted_category,
            assistant_explanation=assistant_explanation,
            correct_category=correct_category,
        )
        logger.info(
            "send_feedback | user_claim            : %s",
            payload.model_dump()["user_claim"][:50],
        )
        logger.info(
            "send_feedback | predicted_category    : %s",
            payload.model_dump()["predicted_category"],
        )
        logger.info(
            "send_feedback | assistant_explanation : %s",
            payload.model_dump()["assistant_explanation"][:50],
        )
        logger.info(
            "send_feedback | correct_category      : %s",
            payload.model_dump()["correct_category"],
        )

        endpoint = Context.API_URL + "feedback"
        logger.info(endpoint)

        response = requests.post(endpoint, json=payload.model_dump(), timeout=30)
        response.raise_for_status()
        logger.info("send_feedback | response : %s", response)

    except requests.exceptions.RequestException as e:
        logger.error("API request failed: %s", e)
        st.error(f"API request failed: {e}")
        return None
    except ValidationError as e:
        logger.error("Invalid format:\n%s", e)
        st.error(f"Invalid format:\n{e}")
        return None
    except Exception as e:
        logger.error("Unexpected error:\n%s", e)
        st.error(f"Unexpected error:\n{e}")
        return None
