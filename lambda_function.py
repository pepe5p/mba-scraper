"""This file's purpose is to expose real lambda handler from main module."""

from mba_scraper.lambda_function import lambda_handler

__all__ = [
    "lambda_handler",
]
