import operator
from django.db.models import Q, F
from functools import reduce, cached_property
from querystring_parser import parser


class DataTablesServer(object):
    def __init__(self, request, columns, queryset):

        self.columns = columns
        self.queryset = queryset
        self.total_records = len(self.queryset)
        self.total_filtered_records = self.total_records

        # Parse the request into a multidemintional dictionary
        self.request_dict: dict = parser.parse(request.GET.urlencode())

        # Set pagination variables.
        # Use defaults for when the endpoint is used directly without get variables
        self.start = int(self.request_dict.get("start", "0"))
        self.length = int(self.request_dict.get("length", "10"))

    @cached_property
    def column_index_lookup_by_data(self):
        column_index_lookup_by_data = {}
        for i, v in self.request_dict["columns"].items():
            column_index_lookup_by_data[v.get("data", i)] = i
        return column_index_lookup_by_data

    def get_column_index_by_data(self, data: str) -> int:
        return self.column_index_lookup_by_data.get(data, None)

    def get_output_result(self) -> dict:
        data = self.get_db_data()
        return {
            "draw": self.request_dict.get("draw"),
            "recordsTotal": self.total_records,
            "recordsFiltered": self.total_filtered_records,
            "data": data,
        }

    def get_db_data(self) -> list[dict]:
        # Apply Filter
        self.filter_queryset()
        self.total_filtered_records = len(self.queryset)

        # Apply Order
        self.order_queryset()

        # Select only the allowed collumns
        self.select_queryset()

        # Apply Paginations
        self.paginate_queryset()

        return list(self.queryset)

    def filter_queryset(self) -> None:
        q_filter = self.get_filter()

        if q_filter:
            self.queryset = self.queryset.filter(q_filter)

    def get_filter(self):
        global_search_value = self.request_dict.get("search", {}).get("value", "")
        global_search_regex = (
            self.request_dict.get("search", {}).get("regex", False) == "true"
        )

        # if global_search_value == "":
        #    return

        global_lookup_type = "icontains" if not global_search_regex else "iregex"
        # Loop over designated columns and build query list
        global_filter_list = []
        column_filter_list = []
        for column in self.columns:
            # Get column id from request based on provided column name
            column_index = self.get_column_index_by_data(column)
            # Only search against fields provided in the request
            if column_index is None:
                continue

            # Verify that searchable is true for this field
            field_info = self.request_dict.get("columns").get(column_index)
            if field_info.get("searchable") == "false":
                continue

            # Build the global query
            if global_search_value:
                global_filter_list.append(
                    Q(**{f"{column}__{global_lookup_type}": global_search_value})
                )

            # Get column values
            column_search_value = field_info.get("search", {}).get("value", "")
            column_search_regex = (
                field_info.get("search", {}).get("regex", False) == "true"
            )
            column_lookup_type = "icontains" if not column_search_regex else "iregex"

            # Build the column query
            if column_search_value:
                column_filter_list.append(
                    Q(**{f"{column}__{column_lookup_type}": column_search_value})
                )

        q_filter = []
        # If q_list is empty return None
        if len(global_filter_list) != 0:
            global_filter = reduce(operator.or_, global_filter_list)
            q_filter.append(global_filter)

        if len(column_filter_list) != 0:
            column_filter = reduce(operator.and_, column_filter_list)
            q_filter.append(column_filter)

        # Build global OR search using reduce
        if len(q_filter) != 0:
            return reduce(operator.and_, q_filter)

    def order_queryset(self) -> None:
        order_value = self.request_dict["order"].values()

        order_list = []
        # Sample order_by: {0: {'column': '0','dir': 'asc'}, {2: {'column': '0','dir': 'asc'}
        for order_request in order_value:

            # Lookup the field by the provided column index. Skip if cannot be found.
            field_info = self.request_dict.get("columns").get(
                int(order_request.get("column")), None
            )
            if field_info is None:
                continue

            # If field is not orderable skip
            if field_info.get("orderable") == "false":
                continue

            # Appended hiphen is used for descending order
            order_list.append(
                f"{'-' if order_request.get('dir') == 'desc' else ''}{field_info['data']}"
            )
        if len(order_list) > 0:
            self.queryset = self.queryset.order_by(*order_list)

    def select_queryset(self):
        self.queryset = self.queryset.values(*self.columns)

    def paginate_queryset(self) -> None:
        if self.length == -1:
            return

        self.queryset = self.queryset[self.start : self.start + self.length]
