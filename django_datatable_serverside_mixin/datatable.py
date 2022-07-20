import operator
from django.db.models import Q, F
from functools import reduce
from querystring_parser import parser


class DataTablesServer(object):
    def __init__(self, request, columns, qs):

        # Parse the request into a multidemintional dictionary
        # Serious thanks to https://github.com/bernii/querystring-parser
        self.request_dict: dict = parser.parse(request.GET.urlencode())
        # Get column names from request
        self.columns = columns

        self.column_index_lookup_by_name = {}
        for i, v in self.request_dict["columns"].items():
            self.column_index_lookup_by_name[v.get("name") or i] = i

        # Used for aliasing the data
        self.column_data_lookup_by_name = {}
        for i, v in self.request_dict["columns"].items():
            self.column_data_lookup_by_name[v.get("name") or i] = v.get("data")

        self.db_data = None
        self.qs = qs
        self.records_total = 0
        self.records_filtered = 0
        # Set pagination variables.
        # Use defaults for when the endpoint is used directly without get variables
        self.start = int(self.request_dict.get("start", "1"))
        self.length = int(self.request_dict.get("length", "10"))
        self.end = self.start + self.length

        # Execute queries based on request
        self.db_data = self.get_db_data()

    def get_output_result(self):
        output = {
            "draw": self.request_dict.get("draw"),
            "recordsTotal": self.records_total,
            "recordsFiltered": self.records_filtered,
            "data": list(self.db_data),
        }

        return output

    def get_db_data(self) -> list[dict]:

        # Set records_total before filtering
        self.records_total = len(self.qs)

        # Apply Filter
        # Retrieve the filter query
        filter_query = self.get_filter_query()
        if filter_query is not None:
            # breakpoint()
            self.qs = self.qs.filter(filter_query)

        # set records_filtered now that we have filtered
        self.records_filtered = len(self.qs)

        # Apply Order
        order_list = self.get_order_list()
        if order_list:
            self.qs = self.qs.order_by(*order_list)

        # Set aliases if the data field is not provided (e.g. 1,2,3 etc)
        # Populate select_columns to filter to only the columns provided
        # in the view itself or transpose those to the index
        select_columns = []
        for column in self.columns:
            data = self.column_data_lookup_by_name.get(column, column)
            select_columns.append(data)
            if data is not None and str(data) != column:
                self.qs = self.qs.annotate(**{str(data): F(column)})
        self.qs = self.qs.values(*select_columns)

        # perform pagination using splice
        return list(self.qs[self.start : self.end])

    def get_filter_query(self) -> Q:
        # TODO: Implement column search
        # TODO: Implement search[regex] = True
        # Global Search
        search_value = self.request_dict.get("search", {}).get("value", "")

        if not search_value:
            return None

        # Loop over designated columns and build query list
        q_list = []
        for column in self.columns:
            # Get column id from request based on provided column name
            column_index = self.column_index_lookup_by_name.get(column, None)

            # Only search against fields provided in the request
            if column_index is None:
                continue

            # Verify that searchable is true for this field
            field_info = self.request_dict.get("columns").get(column_index)
            if field_info.get("searchable") == "false":
                continue

            # Build a query for it and append to the q_list
            q_list.append(Q(**{f"{column}__icontains": search_value}))

        # If q_list is empty return None
        if len(q_list) == 0:
            return None

        # Build global OR search using reduce
        q = reduce(operator.or_, q_list)

        return q

    def get_order_list(self) -> list:
        order_list = []
        # Sample order_by: {0: {'column': '0','dir': 'asc'}, {2: {'column': '0','dir': 'asc'}
        for order_request in self.request_dict["order"].values():

            # Lookup the field by the provided column index. Skip if cannot be found.
            field_info = self.request_dict.get("columns").get(
                int(order_request.get("column")), None
            )
            if field_info is None:
                continue

            # If field is not orderable skip
            if field_info.get("orderable") == "false":
                continue

            # Add this order to list using - if dir is desc
            order_list.append(
                f"{'-' if order_request.get('dir') == 'desc' else ''}{field_info['name']}"
            )
        return order_list
