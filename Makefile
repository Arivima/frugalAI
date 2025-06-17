.PHONY: streamlit api up

streamlit:
	$(MAKE) -C front streamlit-dev

api:
	$(MAKE) -C api fastapi-dev

