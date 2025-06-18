import logging

logger = logging.getLogger(__name__)


def validate_required_fields(**kwargs):
    for name, val in kwargs.items():
        if name == "optional":
            for k, v in val.items():
                logger.info(f"Optional - {k:<20} : {v}")
        else:
            logger.info(f"Required - {name:<20} : {val}")
            if not val:
                raise ValueError(f"Missing {name}.")
