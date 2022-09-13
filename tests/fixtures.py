from unittest.mock import MagicMock, patch
from django.db.models import Model, QuerySet
from django.http.request import HttpRequest


def get_mock_model(options: dict = {}):
    return MagicMock(autospec=Model, create=True, **options)


def get_mock_queryset(options: dict = {}):
    return MagicMock(spec_set=QuerySet, **options)


def get_mock_request(options: dict = {}):
    return MagicMock(autospec=HttpRequest, create=True, **options)
