from collections import namedtuple
import operator
from django.db.models import Q
from functools import reduce

from django.http import QueryDict
import re
from querystring_parser import parser

order_dict = {"asc": "", "desc": "-"}


# class DataTablesRequest:
#    def __init__(self, response: QueryDict | dict):
#        self.columns = []
#        self.order = []
#        self.parse_get_request_dictionary(response)
#
#    def parse_get_request_dictionary(self, response: QueryDict | dict):
#        for key in response.keys():
#            if "[" not in key:
#                setattr(self, key, response[key])
#                continue
#            # if key == 'search[value]' or key == 'search[regex]':
#            #    continue
#            print(f"key: {key}")
#            current_key = re.search(r"^(.*?)(\[|$)", key).group(1)
#            print(f"current_key: {current_key}")
#            sub_keys = re.findall(r".*?\[(.*?)\]", key)
#
#            # If dealing with first index using a number, setup a list
#            if sub_keys[0].isnumeric():
#                index = sub_keys[0]
#                # If not initialized, make it an array
#                if getattr(self, current_key, None) is None:
#                    setattr(self, current_key, [])
#                current_list_attribute = getattr(self, current_key)
#
#                current_key_list = getattr(self, current_key)
#                index_exists = ( 0 <= index <= len(current_key_list) )
#                if index_exists:
#
#                    pass
#                else:
#
#                    pass
#
#            else:
#                print("dict")
#                continue
#
#
#        self.convert_to_dictionary(sub_keys, current_dict)
#
#    def convert_to_dictionary(self, sub_keys, current_dict):
#        # Get existing dict
#        temp = getattr(current_key_list, sub_key, {})
#        for sub_key in sub_keys[:-1]:
#            temp[sub_key] = {}
#            temp = temp[sub_key]
#        temp[sub_keys[-1]] = value


class DataTablesServer(object):
    def __init__(self, request, columns, qs):

        # Parse the request into a multidemintional dictionary
        # Serious thanks to https://github.com/bernii/querystring-parser
        self.request_dict: dict = parser.parse(request.GET.urlencode())
        # Get column names from request
        self.columns = columns

        # Used for formatting the output data and name to id lookups
        # self.column_lookup: list = [
        #    v.get("data") or i for i, v in self.request_dict["columns"].items()
        # ]
        self.column_lookup = {}
        for i, v in self.request_dict["columns"].items():
            self.column_lookup[v.get("data") or i] = i
        # breakpoint()
        self.db_data = None
        self.qs = qs
        self.records_total = 0
        self.records_filtered = 0
        # Set pagination variables.
        # Use defaults for when the endpoint is used directly without get variables
        self.start = int(self.request_dict.get("start", "1"))
        self.end = self.start + int(self.request_dict.get("length", "10"))

        # Execute queries based on request
        self.run_queries()

    def get_output_result(self):
        output = {
            "draw": self.request_dict.get("draw"),
            "recordsTotal": self.records_total,
            "recordsFiltered": self.records_filtered,
            "data": list(self.db_data),
        }

        # data_rows = []
        #
        # for row in self.db_data:
        #    data_row = []
        #    for column in self.columns:
        #        data_row.append(row[column])
        #    data_rows.append(data_row)
        # output["data"] = data_rows
        return output

    def run_queries(self):
        filter_query = self.get_filter_query()
        # the term you entered into the datatable search
        # _filter = self.filtering()
        # the document field you chose to sort
        # sorting = self.sorting()
        # custom filter

        # data = list(data[self.start : self.end].values(*self.columns))

        # Execute unfiltered query

        # Set records_total before filtering
        self.records_total = len(self.qs)
        if filter_query:
            self.qs = self.qs.filter(filter_query)
        # self.qs = self.qs.order_by("%s" % sorting).values(*self.columns)
        # length of filtered set
        self.records_filtered = len(self.qs)

        self.db_data = list(self.qs.values(*self.columns))

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
            column_index = self.column_lookup.get(column, None)

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

    def sorting(self):

        order = ""
        if (self.request_dict["iSortCol_0"] != "") and (
            int(self.request_dict["iSortingCols"]) > 0
        ):

            for i in range(int(self.request_dict["iSortingCols"])):
                # column number
                column_number = int(self.request_dict["iSortCol_" + str(i)])
                # sort direction
                sort_direction = self.request_dict["sSortDir_" + str(i)]

                order = (
                    ("" if order == "" else ",")
                    + order_dict[sort_direction]
                    + self.columns[column_number]
                )

        return order


#   def get_pagination_information(self, request_dict: dict):
#
#       pages = namedtuple("pages", ["start", "length", "end"])
#       # breakpoint()
#       pages.start = request_dict.get("start", 0)
#       pages.length = request_dict.get("length", 10)
#       pages.end
#
#
#       return pages
#
