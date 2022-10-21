import unittest
from unittest.mock import MagicMock, patch

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db.models import Model, QuerySet
from django.http import JsonResponse
from django.http.request import HttpRequest
from django.views import View
from django_datatable_serverside_mixin.datatable import DataTablesServer
from django_datatable_serverside_mixin.views import ServerSideDataTablesMixin

from .fixtures import *

sample_data = [{"id": "1", "data": "data"}, {"id": "2", "data": "data"}]
sample_return_value = {
    "draw": 1,
    "recordsTotal": 2,
    "recordsFiltered": 2,
    "data": sample_data,
}


class MisconfiguredView(ServerSideDataTablesMixin):
    """
    A Misconfigured ServerSideDatatableMixin View
    """


class QuerySetView(ServerSideDataTablesMixin):
    columns = ["id", "data"]
    queryset = get_mock_queryset({"all.return_value": sample_data})


class DataCallbackView(QuerySetView):
    def data_callback(self, data):
        for row in data:
            row["extra_field"] = f'some_url/{row["id"]}/'
        return data


class ModelView(ServerSideDataTablesMixin):
    columns = ["id", "data"]
    model = get_mock_model({"_default_manager.all.return_value": sample_data})


class ServerSideDatatableMixinTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        settings.configure()
        # Set up mocks
        cls.mock_request = get_mock_request()
        cls.mock_DataTablesServer = MagicMock(
            spec=DataTablesServer,
            **{"get_output_result.return_value": sample_return_value},
        )

    def test_inheritance(self):
        self.assertIsInstance(ServerSideDataTablesMixin(), View)

    def test_misconfiguration(self):
        view = MisconfiguredView()
        with self.assertRaises(ImproperlyConfigured) as e:
            view.get_queryset()

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

    @patch("django_datatable_serverside_mixin.views.datatable.DataTablesServer")
    def test_get(self, mock_DataTablesServer_class):
        mock_DataTablesServer_class.return_value = self.mock_DataTablesServer
        view = ModelView()
        response = view.get(self.mock_request)
        mock_DataTablesServer_class.assert_called_with(
            self.mock_request,
            view.columns,
            view.get_queryset(),
        )

        self.mock_DataTablesServer.get_output_result.assert_called()
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(
            response.content,
            b'{"draw": 1, "recordsTotal": 2, "recordsFiltered": 2, "data": [{"id": "1", "data": "data"}, {"id": "2", "data": "data"}]}',
        )

    @patch("django_datatable_serverside_mixin.views.datatable.DataTablesServer")
    def test_get_data_callback(self, mock_DataTablesServer_class):
        """
        Test that overwriting the data_callback funcation
        changes the data output and nothing else.
        """
        mock_DataTablesServer_class.return_value = self.mock_DataTablesServer
        view = DataCallbackView()
        response = view.get(self.mock_request)
        self.mock_DataTablesServer.get_output_result.assert_called()
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(
            response.content,
            b'{"draw": 1, "recordsTotal": 2, "recordsFiltered": 2, "data": [{"id": "1", "data": "data", "extra_field": "some_url/1/"}, {"id": "2", "data": "data", "extra_field": "some_url/2/"}]}',
        )

    def test_data_callback(self):
        """
        Test the default implementation of data_callback
        does not change the data
        """
        view = ModelView()
        test_value = [
            {"test": "some_data", "test2": 2},
            {"test": "some_data", "test2": 2},
        ]
        return_value = view.data_callback(test_value)
        self.assertEqual(return_value, test_value)

    def test_ServerSideDatatableMixin_deprecation_warning(self):

        from django_datatable_serverside_mixin.views import ServerSideDatatableMixin

        with self.assertWarns(expected_warning=DeprecationWarning):
            test = ServerSideDatatableMixin()


#
