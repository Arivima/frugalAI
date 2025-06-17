# app/config.py
import os


class Context:
    API_URL = "http://127.0.0.1:8000/"
    CATEGORY_LABEL = {
        "0": "Not disinformation",
        "1": "Challenges the existence of climate change",
        "2": "Challenges that climate change is caused by humans",
        "3": "Challenges that climate change has negative impacts",
        "4": "Challenges the solutions for climate change",
        "5": "Challenges climate science",
        "6": "Challenges climate scientists and/or activits",
        "7": "Promotes the need for fossil fuel",
        "8": "None of the above",
    }
    # CATEGORY_LABEL = {
    #     "0": "Unrelated to climate change",
    #     "1": "Climate change existence",
    #     "2": "Human responsibility",
    #     "3": "Negative impacts",
    #     "4": "Solutions for climate change",
    #     "5": "Climate science",
    #     "6": "Climate scitentist/activits",
    #     "7": "Fossil fuel",
    # }
    CATEGORY_DESCRIPTION = {
        "0": "No relevant claim detected or claims that don't fit other categories",
        "1": "This category gathers claims denying the occurrence of global warming and its effects - Global warming is not happening. Climate change is NOT leading to melting ice (such as glaciers, sea ice, and permafrost), increased extreme weather, or rising sea levels. Cold weather also shows that climate change is not happening",
        "2": "This category gathers claims denying human responsibility in climate change - Greenhouse gases from humans are not the causing climate change.",
        "3": "This category gathers claims minimizing or denying negative impacts of climate change - The impacts of climate change will not be bad and might even be beneficial.",
        "4": "This category gathers claims against climate solutions - Climate solutions are harmful or unnecessary",
        "5": "This category gathers claims questioning climate science validity - Climate science is uncertain, unsound, unreliable, or biased.",
        "6": "This category gathers claims attacking climate scientists and activists - Climate scientists and proponents of climate action are alarmist, biased, wrong, hypocritical, corrupt, and/or politically motivated.",
        "7": "This category gathers claims promoting fossil fuel necessity - We need fossil fuels for economic growth, prosperity, and to maintain our standard of living.",
    }