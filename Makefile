.PHONY: streamlit api up

streamlit:
	$(MAKE) -C frugalAI-streamlit streamlit-dev

api:
	$(MAKE) -C frugalAI-api fastapi-dev

