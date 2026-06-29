import logging

from app.core.request_context import request_id_context


class RequestIDFilter(logging.Filter):

    def filter(self, record):
        record.request_id = request_id_context.get()
        return True


def configure_logging():

    handler = logging.StreamHandler()

    handler.addFilter(
        RequestIDFilter()
    )

    formatter = logging.Formatter(
        "%(asctime)s | "
        "%(levelname)s | "
        "%(name)s | "
        "request_id=%(request_id)s | "
        "%(message)s"
    )

    handler.setFormatter(
        formatter
    )

    logging.basicConfig(
        level=logging.INFO,
        handlers=[handler],
        force=True,
    )