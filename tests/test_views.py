from django.views import View
from unittest.mock import patch
import pytest
import unittest
from django_datatable_serverside_mixin.views import ServerSideDatatableMixin

# from django_datatable_serverside_mixin.datatable import DataTablesServer


class SimpleView(ServerSideDatatableMixin):
    """
    A Simple ServerSideDatatableMixin View
    """

    pass


class ServerSideDatatableMixinTestCase(unittest.TestCase):
    def test_inheritance(self):
        from django.views import View

        self.assertIsInstance(SimpleView(), View)

    # @patch.object("django_datatable_serverside_mixin.datatable.DataTablesServer")
    # def test_get_request(self, mockDataTablesServer):
    #    pass

    # self.mixin.get()
