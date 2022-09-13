import unittest
from unittest.mock import MagicMock, patch

from django.core.exceptions import ImproperlyConfigured
from django.db.models import Model, QuerySet
from django.http import JsonResponse
from django.http.request import HttpRequest
from django_datatable_serverside_mixin.datatable import DataTablesServer
from django_datatable_serverside_mixin.views import ServerSideDatatableMixin
from django.conf import settings

from .fixtures import *

sample_data = [{"id": "1", "data": "data"}, {"id": "2", "data": "data"}]


class MisconfiguredView(ServerSideDatatableMixin):
    """
    A Misconfigured ServerSideDatatableMixin View
    """


class QuerySetView(ServerSideDatatableMixin):
    columns = ["id", "data"]
    queryset = get_mock_queryset({"all.return_value": sample_data})


class ModelView(ServerSideDatatableMixin):
    columns = ["id", "data"]
    model = get_mock_model({"_default_manager.all.return_value": sample_data})


class ServerSideDatatableMixinTestCase(unittest.TestCase):
    def test_inheritance(self):
        from django.views import View

        self.assertIsInstance(ServerSideDatatableMixin(), View)

    def test_misconfiguration(self):
        view = MisconfiguredView()
        with self.assertRaises(ImproperlyConfigured) as e:
            test = view.get_queryset()

    def test_queryset(self):
        view = QuerySetView()
        test = view.get_queryset()
        self.assertIsInstance(view.queryset, QuerySet)
        view.queryset.all.assert_called()
        self.assertEqual(test, sample_data)

    def test_model(self):
        view = ModelView()
        test = view.get_queryset()
        view.model._default_manager.all.assert_called()
        self.assertEqual(test, sample_data)

    def test_get(self):
        settings.configure()
        # Set up mocks
        mock_request = get_mock_request()
        mock_DataTablesServer = MagicMock(
            spec=DataTablesServer, **{"get_output_result.return_value": sample_data}
        )

        # Patch DataTablesServer within the views module
        with patch(
            "django_datatable_serverside_mixin.views.datatable.DataTablesServer",
            return_value=mock_DataTablesServer,
        ) as mock_DataTablesServer_class:
            view = ModelView()
            response = view.get(mock_request)
            mock_DataTablesServer_class.assert_called_with(
                mock_request, view.columns, view.get_queryset()
            )
            mock_DataTablesServer.get_output_result.assert_called()
            self.assertIsInstance(response, JsonResponse)
            self.assertEqual(
                response.content,
                b'[{"id": "1", "data": "data"}, {"id": "2", "data": "data"}]',
            )
