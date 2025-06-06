# app/config.py
import os
import logging


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

API_URL = "http://127.0.0.1:8000/classify"

class Context:
    CLIMATE_DICT = {
        "0": "No relevant claim detected or claims that don't fit other categories",
        "1": "Climate change - This category gathers claims denying the occurrence of global warming and its effects - Global warming is not happening. Climate change is NOT leading to melting ice (such as glaciers, sea ice, and permafrost), increased extreme weather, or rising sea levels. Cold weather also shows that climate change is not happening",
        "2": "Human responsibility - This category gathers claims denying human responsibility in climate change - Greenhouse gases from humans are not the causing climate change.",
        "3": "Negative impacts - This category gathers claims minimizing or denying negative impacts of climate change - The impacts of climate change will not be bad and might even be beneficial.",
        "4": "Solutions for climate change - This category gathers claims against climate solutions - Climate solutions are harmful or unnecessary",
        "5": "Climate science - This category gathers claims questioning climate science validity - Climate science is uncertain, unsound, unreliable, or biased.",
        "6": "Climate scitentist/activits - This category gathers claims attacking climate scientists and activists - Climate scientists and proponents of climate action are alarmist, biased, wrong, hypocritical, corrupt, and/or politically motivated.",
        "7": "Fossil fuel - This category gathers claims promoting fossil fuel necessity - We need fossil fuels for economic growth, prosperity, and to maintain our standard of living.",
    }