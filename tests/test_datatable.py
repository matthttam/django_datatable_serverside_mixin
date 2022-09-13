import unittest
import operator
from parameterized import parameterized
from unittest.mock import MagicMock, patch, Mock
from .fixtures import *
from django.utils.http import urlencode
from django_datatable_serverside_mixin.datatable import DataTablesServer
from django.db.models import Q, F
from functools import reduce

# sample_data = "draw=1&columns%5B0%5D%5Bdata%5D=id&columns%5B0%5D%5Bname%5D=id&columns%5B0%5D%5Bsearchable%5D=true&columns%5B0%5D%5Borderable%5D=true&columns%5B0%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B0%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B1%5D%5Bdata%5D=person__internal_id&columns%5B1%5D%5Bname%5D=person__internal_id&columns%5B1%5D%5Bsearchable%5D=true&columns%5B1%5D%5Borderable%5D=true&columns%5B1%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B1%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B2%5D%5Bdata%5D=person_name&columns%5B2%5D%5Bname%5D=person_name&columns%5B2%5D%5Bsearchable%5D=true&columns%5B2%5D%5Borderable%5D=true&columns%5B2%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B2%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B3%5D%5Bdata%5D=person__first_name&columns%5B3%5D%5Bname%5D=person__first_name&columns%5B3%5D%5Bsearchable%5D=true&columns%5B3%5D%5Borderable%5D=true&columns%5B3%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B3%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B4%5D%5Bdata%5D=person__last_name&columns%5B4%5D%5Bname%5D=person__last_name&columns%5B4%5D%5Bsearchable%5D=true&columns%5B4%5D%5Borderable%5D=true&columns%5B4%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B4%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B5%5D%5Bdata%5D=person__type__name&columns%5B5%5D%5Bname%5D=person__type__name&columns%5B5%5D%5Bsearchable%5D=true&columns%5B5%5D%5Borderable%5D=true&columns%5B5%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B5%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B6%5D%5Bdata%5D=device_str&columns%5B6%5D%5Bname%5D=device_str&columns%5B6%5D%5Bsearchable%5D=true&columns%5B6%5D%5Borderable%5D=true&columns%5B6%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B6%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B7%5D%5Bdata%5D=device__asset_id&columns%5B7%5D%5Bname%5D=device__asset_id&columns%5B7%5D%5Bsearchable%5D=true&columns%5B7%5D%5Borderable%5D=true&columns%5B7%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B7%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B8%5D%5Bdata%5D=device__serial_number&columns%5B8%5D%5Bname%5D=device__serial_number&columns%5B8%5D%5Bsearchable%5D=true&columns%5B8%5D%5Borderable%5D=true&columns%5B8%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B8%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B9%5D%5Bdata%5D=device__device_model__name&columns%5B9%5D%5Bname%5D=device__device_model__name&columns%5B9%5D%5Bsearchable%5D=true&columns%5B9%5D%5Borderable%5D=true&columns%5B9%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B9%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B10%5D%5Bdata%5D=assignment_datetime&columns%5B10%5D%5Bname%5D=assignment_datetime&columns%5B10%5D%5Bsearchable%5D=true&columns%5B10%5D%5Borderable%5D=true&columns%5B10%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B10%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B11%5D%5Bdata%5D=return_datetime&columns%5B11%5D%5Bname%5D=return_datetime&columns%5B11%5D%5Bsearchable%5D=true&columns%5B11%5D%5Borderable%5D=true&columns%5B11%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B11%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B12%5D%5Bdata%5D=id&columns%5B12%5D%5Bname%5D=actions&columns%5B12%5D%5Bsearchable%5D=true&columns%5B12%5D%5Borderable%5D=false&columns%5B12%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B12%5D%5Bsearch%5D%5Bregex%5D=false&order%5B0%5D%5Bcolumn%5D=0&order%5B0%5D%5Bdir%5D=asc&start=0&length=10&search%5Bvalue%5D=&search%5Bregex%5D=false&_=1662747552725"


# mock_queryset = get_mock_queryset({"all.return_value": self.sample_data})


class DataTablesServerTestCase(unittest.TestCase):
    def apply_global_filter(self, filter_value) -> dict:
        filtered_dataset = list()
        for d in self.dataset:
            filters = list()
            for column in self.columns:
                filters.append(filter_value in d[column].lower())
            if reduce(operator.or_, filters):
                filtered_dataset.append(d)

        return filtered_dataset

        # [d for d in self.dataset if  ]
        return filtered_dataset

    def setUp(self) -> None:
        self.maxDiff = None
        self.dataset = [
            {
                "id": "1",
                "data": "unsearchable",
                "first_name": "John",
                "last_name": "Smith",
                "internal_id": "1111",
            },
            {
                "id": "2",
                "data": "unsearchable also",
                "first_name": "Matt",
                "last_name": "Henry",
                "internal_id": "2222",
            },
            {
                "id": "3",
                "data": "unsearchable also2",
                "first_name": "Alice",
                "last_name": "Jones",
                "internal_id": "3333",
            },
        ]
        self.columns = self.dataset[0].keys()
        self.request_params = {
            "draw": "1",
            "columns[0][data]": "id",
            "columns[0][name]": "name_of_id",
            "columns[0][searchable]": "true",
            "columns[0][orderable]": "true",
            "columns[0][search][value]": "",
            "columns[0][search][regex]": "false",
            "columns[1][data]": "data",
            "columns[1][name]": "",
            "columns[1][searchable]": "true",
            "columns[1][orderable]": "true",
            "columns[1][search][value]": "",
            "columns[1][search][regex]": "false",
            "columns[2][data]": "first_name",
            "columns[2][name]": "first_name",
            "columns[2][searchable]": "true",
            "columns[2][orderable]": "true",
            "columns[2][search][value]": "",
            "columns[2][search][regex]": "false",
            "columns[3][data]": "last_name",
            "columns[3][name]": "last_name",
            "columns[3][searchable]": "true",
            "columns[3][orderable]": "true",
            "columns[3][search][value]": "",
            "columns[3][search][regex]": "false",
            "columns[4][data]": "internal_id",
            "columns[4][name]": "internal_id",
            "columns[4][searchable]": "true",
            "columns[4][orderable]": "true",
            "columns[4][search][value]": "",
            "columns[4][search][regex]": "false",
            "order[0][column]": 0,
            "order[0][dir]": "asc",
            "start": "0",
            "length": "10",
            "search[value]": "",
            "search[regex]": "false",
        }

    def test_get_output_result(self):
        mock_request = get_mock_request(
            {"GET.urlencode.return_value": urlencode(self.request_params)}
        )
        # Pretend the queryset started with a length of our dataset
        mock_queryset = get_mock_queryset({"__len__.return_value": len(self.dataset)})
        datatable = DataTablesServer(mock_request, self.columns, mock_queryset)
        datatable.get_db_data = Mock(**{"return_value": self.dataset})
        # Pretend the queryset was filtered to one result
        mock_queryset.__len__.return_value = 1

        # Run and assert
        result = datatable.get_output_result()
        self.assertEqual(
            result,
            {
                "draw": "1",
                "recordsTotal": 3,
                "recordsFiltered": 1,
                "data": self.dataset,
            },
        )

    def test_global_filter_with_no_value(self):
        """
        A blank value for the global search should not trigger a filter at all
        """
        filter_value = ""
        self.request_params["search[value]"] = filter_value
        mock_request = get_mock_request(
            {"GET.urlencode.return_value": urlencode(self.request_params)}
        )
        mock_queryset = get_mock_queryset({"__len__.return_value": len(self.dataset)})
        mock_filtered_queryset = get_mock_queryset()
        mock_queryset.filter.return_value = mock_filtered_queryset
        datatable = DataTablesServer(mock_request, self.columns, mock_queryset)

        datatable.filter_queryset()
        mock_queryset.filter.assert_not_called()
        self.assertNotEqual(
            mock_filtered_queryset,
            datatable.queryset,
            msg="Filtered queryset incorrectly assigned to self.queryset!",
        )

    def test_global_filter_with_value(self):
        filter_value = "2"
        self.request_params["search[value]"] = filter_value
        mock_request = get_mock_request(
            {"GET.urlencode.return_value": urlencode(self.request_params)}
        )
        mock_queryset = get_mock_queryset({"__len__.return_value": len(self.dataset)})
        mock_filtered_queryset = get_mock_queryset()
        mock_queryset.filter.return_value = mock_filtered_queryset
        datatable = DataTablesServer(mock_request, self.columns, mock_queryset)

        datatable.filter_queryset()

        correct_filter = (
            Q(id__icontains=filter_value)
            | Q(data__icontains=filter_value)
            | Q(first_name__icontains=filter_value)
            | Q(last_name__icontains=filter_value)
            | Q(internal_id__icontains=filter_value)
        )
        mock_queryset.filter.assert_called_once_with(correct_filter)
        self.assertCountEqual(
            mock_filtered_queryset,
            datatable.queryset,
            msg="Filtered queryset not assigned to self.queryset!",
        )

    def test_global_filter_searchable_false(self):
        """
        A column with searchable false should not be included in the global search
        """
        filter_value = "1111"
        self.request_params["search[value]"] = filter_value
        self.request_params["columns[4][searchable]"] = "false"
        mock_request = get_mock_request(
            {"GET.urlencode.return_value": urlencode(self.request_params)}
        )
        mock_queryset = get_mock_queryset({"__len__.return_value": len(self.dataset)})
        mock_filtered_queryset = get_mock_queryset()
        mock_queryset.filter.return_value = mock_filtered_queryset
        datatable = DataTablesServer(mock_request, self.columns, mock_queryset)

        datatable.filter_queryset()

        correct_filter = (
            Q(id__icontains=filter_value)
            | Q(data__icontains=filter_value)
            | Q(first_name__icontains=filter_value)
            | Q(last_name__icontains=filter_value)
        )
        mock_queryset.filter.assert_called_once_with(correct_filter)
        self.assertCountEqual(
            mock_filtered_queryset,
            datatable.queryset,
            msg="Filtered queryset not assigned to self.queryset!",
        )

    def test_global_filter_no_searchable_fields(self):
        """
        If all available fields are not searchable, global search shouldn't apply
        any filters at all
        """
        filter_value = "test"
        self.request_params["search[value]"] = filter_value
        self.request_params["columns[0][searchable]"] = "false"
        self.request_params["columns[1][searchable]"] = "false"
        self.request_params["columns[2][searchable]"] = "false"
        self.request_params["columns[3][searchable]"] = "false"
        self.request_params["columns[4][searchable]"] = "false"

        mock_request = get_mock_request(
            {"GET.urlencode.return_value": urlencode(self.request_params)}
        )
        mock_queryset = get_mock_queryset({"__len__.return_value": len(self.dataset)})
        mock_filtered_queryset = get_mock_queryset()
        mock_queryset.filter.return_value = mock_filtered_queryset
        datatable = DataTablesServer(mock_request, self.columns, mock_queryset)

        datatable.filter_queryset()
        mock_queryset.filter.assert_not_called()
        self.assertNotEqual(
            mock_filtered_queryset,
            datatable.queryset,
            msg="Filtered queryset incorrectly assigned to self.queryset!",
        )

    def test_order(self):
        self.request_params["order[0][column]"] = 0
        self.request_params["order[0][dir]"] = "asc"
        self.request_params["order[1][column]"] = 1
        self.request_params["order[1][dir]"] = "desc"
        mock_request = get_mock_request(
            {"GET.urlencode.return_value": urlencode(self.request_params)}
        )
        mock_queryset = get_mock_queryset({"__len__.return_value": len(self.dataset)})
        mock_ordered_queryset = get_mock_queryset()
        mock_queryset.order_by.return_value = mock_ordered_queryset
        datatable = DataTablesServer(mock_request, self.columns, mock_queryset)

        datatable.order_queryset()

        correct_order_list = ["id", "-data"]

        mock_queryset.order_by.assert_called_once_with(*correct_order_list)
        self.assertEqual(
            datatable.queryset,
            mock_ordered_queryset,
            msg="Ordered queryset not assigned to self.queryset!",
        )

    def test_order_orderable_false(self):
        self.request_params["order[0][column]"] = 0
        self.request_params["order[0][dir]"] = "asc"
        self.request_params["order[1][column]"] = 1
        self.request_params["order[1][dir]"] = "desc"
        self.request_params["columns[1][orderable]"] = "false"
        mock_request = get_mock_request(
            {"GET.urlencode.return_value": urlencode(self.request_params)}
        )
        mock_queryset = get_mock_queryset({"__len__.return_value": len(self.dataset)})
        mock_ordered_queryset = get_mock_queryset()
        mock_queryset.order_by.return_value = mock_ordered_queryset
        datatable = DataTablesServer(mock_request, self.columns, mock_queryset)

        datatable.order_queryset()

        correct_order_list = ["id"]

        mock_queryset.order_by.assert_called_once_with(*correct_order_list)
        self.assertEqual(
            datatable.queryset,
            mock_ordered_queryset,
            msg="Ordered queryset not assigned to self.queryset!",
        )

    def test_order_no_orderable_fields(self):
        self.request_params["order[0][column]"] = 0
        self.request_params["order[0][dir]"] = "asc"
        self.request_params["columns[0][orderable]"] = "false"
        self.request_params["order[1][column]"] = 1
        self.request_params["order[1][dir]"] = "desc"
        self.request_params["columns[1][orderable]"] = "false"
        mock_request = get_mock_request(
            {"GET.urlencode.return_value": urlencode(self.request_params)}
        )
        mock_queryset = get_mock_queryset({"__len__.return_value": len(self.dataset)})
        mock_ordered_queryset = get_mock_queryset()
        mock_queryset.order_by.return_value = mock_ordered_queryset
        datatable = DataTablesServer(mock_request, self.columns, mock_queryset)

        datatable.order_queryset()

        mock_queryset.order_by.assert_not_called()
        self.assertNotEqual(
            datatable.queryset,
            mock_ordered_queryset,
            msg="Ordered queryset incorrectly assigned to self.queryset!",
        )

    def test_paginate_all(self):
        self.request_params["start"] = "0"
        self.request_params["length"] = "-1"

        mock_request = get_mock_request(
            {"GET.urlencode.return_value": urlencode(self.request_params)}
        )
        mock_queryset = get_mock_queryset({"__len__.return_value": len(self.dataset)})
        mock_paginated_queryset = get_mock_queryset()
        mock_queryset.__getitem__.return_value = mock_paginated_queryset

        datatable = DataTablesServer(mock_request, self.columns, mock_queryset)
        datatable.paginate_queryset()
        mock_queryset.__getitem__.assert_not_called()
        self.assertNotEqual(
            datatable.queryset,
            mock_paginated_queryset,
            msg="Paginated queryset incorrectly assigned to self.queryset!",
        )

    @parameterized.expand([(0, 10), (0, 100), (0, 1), (1, 1), (500, 1000)])
    def test_paginate(self, start, length):
        self.request_params["start"] = start
        self.request_params["length"] = length
        mock_request = get_mock_request(
            {"GET.urlencode.return_value": urlencode(self.request_params)}
        )
        mock_queryset = get_mock_queryset({"__len__.return_value": len(self.dataset)})
        mock_paginated_queryset = get_mock_queryset()
        mock_queryset.__getitem__.return_value = mock_paginated_queryset

        datatable = DataTablesServer(mock_request, self.columns, mock_queryset)
        datatable.paginate_queryset()
        mock_queryset.__getitem__.assert_called_with(slice(start, length + start, None))
        self.assertEqual(
            datatable.queryset,
            mock_paginated_queryset,
            msg="Paginated queryset not assigned to self.queryset!",
        )

    def test_select_queryset(self):
        mock_request = get_mock_request(
            {"GET.urlencode.return_value": urlencode(self.request_params)}
        )
        mock_queryset = get_mock_queryset({"__len__.return_value": len(self.dataset)})
        mock_select_queryset = Mock()
        mock_queryset.values.return_value = mock_select_queryset

        datatable = DataTablesServer(mock_request, self.columns, mock_queryset)
        datatable.select_queryset()

        mock_queryset.values.assert_called_with(*datatable.columns)

    def test_get_column_index_by_data(self):
        mock_request = get_mock_request(
            {"GET.urlencode.return_value": urlencode(self.request_params)}
        )
        mock_queryset = get_mock_queryset({"__len__.return_value": len(self.dataset)})

        datatable = DataTablesServer(mock_request, self.columns, mock_queryset)
        self.assertEqual(datatable.get_column_index_by_data("id"), 0)
        self.assertEqual(datatable.get_column_index_by_data("data"), 1)
        self.assertIsNone(datatable.get_column_index_by_data("blah123"))

    @patch("django_datatable_serverside_mixin.datatable.parser")
    def test_init(self, mock_parser):
        mock_request = get_mock_request(
            {"GET.urlencode.return_value": urlencode(self.request_params)}
        )
        mock_queryset = get_mock_queryset({"__len__.return_value": len(self.dataset)})
        mock_parser.parse.return_value = {"test": "test"}
        datatable = DataTablesServer(mock_request, self.columns, mock_queryset)
        self.assertEqual(datatable.start, 0)
        self.assertEqual(datatable.length, 10)
        self.assertEqual(datatable.columns, self.columns)
        self.assertEqual(datatable.queryset, mock_queryset)
        self.assertEqual(datatable.total_records, len(mock_queryset))
        self.assertIsInstance(datatable.request_dict, dict)
        mock_parser.parse.assert_called_with(urlencode(self.request_params))
        self.assertEqual(datatable.request_dict, {"test": "test"})

    @patch(
        "django_datatable_serverside_mixin.datatable.DataTablesServer.paginate_queryset"
    )
    @patch(
        "django_datatable_serverside_mixin.datatable.DataTablesServer.select_queryset"
    )
    @patch(
        "django_datatable_serverside_mixin.datatable.DataTablesServer.order_queryset"
    )
    @patch(
        "django_datatable_serverside_mixin.datatable.DataTablesServer.filter_queryset"
    )
    def test_get_db_data(
        self,
        mock_filter_queryset_function,
        mock_order_queryset_function,
        mock_select_queryset_function,
        mock_paginate_queryset_function,
    ):
        """
        Tests get_db_data  by ensuring each function is called
        """
        # Set filter to ensure the queryset is updated
        self.request_params["search[value]"] = "2"
        mock_request = get_mock_request(
            {"GET.urlencode.return_value": urlencode(self.request_params)}
        )
        mock_queryset = get_mock_queryset({"__iter__.return_value": [1, 2, 3]})
        datatable = DataTablesServer(mock_request, self.columns, mock_queryset)
        result = datatable.get_db_data()
        mock_filter_queryset_function.assert_called_once()
        mock_order_queryset_function.assert_called_once()
        mock_select_queryset_function.assert_called_once()
        mock_paginate_queryset_function.assert_called_once()
        self.assertIsInstance(result, list)
        print(datatable.queryset)
