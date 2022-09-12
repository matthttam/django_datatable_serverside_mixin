import unittest
from unittest.mock import MagicMock, patch, Mock
from .fixtures import *
from django.utils.http import urlencode
from django_datatable_serverside_mixin.datatable import DataTablesServer
from django.db.models import Q, F

# sample_data = "draw=1&columns%5B0%5D%5Bdata%5D=id&columns%5B0%5D%5Bname%5D=id&columns%5B0%5D%5Bsearchable%5D=true&columns%5B0%5D%5Borderable%5D=true&columns%5B0%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B0%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B1%5D%5Bdata%5D=person__internal_id&columns%5B1%5D%5Bname%5D=person__internal_id&columns%5B1%5D%5Bsearchable%5D=true&columns%5B1%5D%5Borderable%5D=true&columns%5B1%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B1%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B2%5D%5Bdata%5D=person_name&columns%5B2%5D%5Bname%5D=person_name&columns%5B2%5D%5Bsearchable%5D=true&columns%5B2%5D%5Borderable%5D=true&columns%5B2%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B2%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B3%5D%5Bdata%5D=person__first_name&columns%5B3%5D%5Bname%5D=person__first_name&columns%5B3%5D%5Bsearchable%5D=true&columns%5B3%5D%5Borderable%5D=true&columns%5B3%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B3%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B4%5D%5Bdata%5D=person__last_name&columns%5B4%5D%5Bname%5D=person__last_name&columns%5B4%5D%5Bsearchable%5D=true&columns%5B4%5D%5Borderable%5D=true&columns%5B4%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B4%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B5%5D%5Bdata%5D=person__type__name&columns%5B5%5D%5Bname%5D=person__type__name&columns%5B5%5D%5Bsearchable%5D=true&columns%5B5%5D%5Borderable%5D=true&columns%5B5%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B5%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B6%5D%5Bdata%5D=device_str&columns%5B6%5D%5Bname%5D=device_str&columns%5B6%5D%5Bsearchable%5D=true&columns%5B6%5D%5Borderable%5D=true&columns%5B6%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B6%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B7%5D%5Bdata%5D=device__asset_id&columns%5B7%5D%5Bname%5D=device__asset_id&columns%5B7%5D%5Bsearchable%5D=true&columns%5B7%5D%5Borderable%5D=true&columns%5B7%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B7%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B8%5D%5Bdata%5D=device__serial_number&columns%5B8%5D%5Bname%5D=device__serial_number&columns%5B8%5D%5Bsearchable%5D=true&columns%5B8%5D%5Borderable%5D=true&columns%5B8%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B8%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B9%5D%5Bdata%5D=device__device_model__name&columns%5B9%5D%5Bname%5D=device__device_model__name&columns%5B9%5D%5Bsearchable%5D=true&columns%5B9%5D%5Borderable%5D=true&columns%5B9%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B9%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B10%5D%5Bdata%5D=assignment_datetime&columns%5B10%5D%5Bname%5D=assignment_datetime&columns%5B10%5D%5Bsearchable%5D=true&columns%5B10%5D%5Borderable%5D=true&columns%5B10%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B10%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B11%5D%5Bdata%5D=return_datetime&columns%5B11%5D%5Bname%5D=return_datetime&columns%5B11%5D%5Bsearchable%5D=true&columns%5B11%5D%5Borderable%5D=true&columns%5B11%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B11%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B12%5D%5Bdata%5D=id&columns%5B12%5D%5Bname%5D=actions&columns%5B12%5D%5Bsearchable%5D=true&columns%5B12%5D%5Borderable%5D=false&columns%5B12%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B12%5D%5Bsearch%5D%5Bregex%5D=false&order%5B0%5D%5Bcolumn%5D=0&order%5B0%5D%5Bdir%5D=asc&start=0&length=10&search%5Bvalue%5D=&search%5Bregex%5D=false&_=1662747552725"


# mock_queryset = get_mock_queryset({"all.return_value": self.sample_data})


class DataTablesServerTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.columns = ["id", "data"]
        self.dataset = [{"id": "1", "data": "data"}, {"id": "2", "data": "data"}]
        self.request_params = {
            "draw": 1,
            "columns[0][data]": "id",
            "columns[0][name]": "id",
            "columns[0][searchable]": "true",
            "columns[0][ordered]": "true",
            "columns[0][search][value]": "",
            "columns[0][search][regex]": "false",
            "columns[1][data]": "data",
            "columns[1][name]": "data",
            "columns[1][searchable]": "true",
            "columns[1][ordered]": "true",
            "columns[1][search][value]": "",
            "columns[1][search][regex]": "false",
            "order[0][column]": 0,
            "order[0][dir]": "asc",
            "start": 0,
            "length": 10,
            "search[value]": "",
            "search[regex]": "false",
        }

    def test_get_output_result(self):
        mock_request = get_mock_request(
            {"GET.urlencode.return_value": urlencode(self.request_params)}
        )
        mock_queryset = get_mock_queryset({"__len__.return_value": len(self.dataset)})
        datatable = DataTablesServer(mock_request, self.columns, mock_queryset)

        datatable.get_db_data = Mock(**{"return_value": self.dataset})

        result = datatable.get_output_result()
        self.assertEqual(
            result,
            {
                "draw": "1",
                "recordsTotal": 2,
                "recordsFiltered": 2,
                "data": [{"id": "1", "data": "data"}, {"id": "2", "data": "data"}],
            },
        )
        # print(datatable.get_output_result())

    def test_global_filter_value(self):
        self.request_params["search[value]"] = "2"
        mock_request = get_mock_request(
            {"GET.urlencode.return_value": urlencode(self.request_params)}
        )
        mock_queryset = get_mock_queryset({"__len__.return_value": len(self.dataset)})
        filtered_dataset = [d for d in self.dataset if self.request_params["search[value]"].lower() in d['id'].lower() or self.request_params["search[value]"] in d['data']  ]
        mock_updated_queryset = get_mock_queryset({"__len__.return_value": len(self.dataset)})
        mock_queryset.filter.return_value = 
        datatable = DataTablesServer(mock_request, self.columns, mock_queryset)

        datatable.filter_queryset()

        correct_filter = Q(id__icontains="2") | Q(data__icontains="2")
        mock_queryset.filter.assert_called_once_with(correct_filter)
