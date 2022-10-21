from django.views import View
from django.http import JsonResponse
from django.core.exceptions import ImproperlyConfigured
from django.db.models import QuerySet
from . import datatable
from warnings import warn
from deprecated import deprecated


class ServerSideDataTablesMixin(View):
    columns = None
    queryset = None
    model = None

    def get(self, request, *args, **kwargs):
        DataTablesServer = datatable.DataTablesServer(
            request,
            self.columns,
            self.get_queryset(),
        )
        result = DataTablesServer.get_output_result()
        result["data"] = self.data_callback(result["data"])

        return JsonResponse(result, safe=False)

    def data_callback(self, data: list[dict]) -> list[dict]:
        """
        Called on data attribute of result of DataTablesServer get_output_result method.
        Can be used to manipulate the final data rows.
        Useful for adding additional fields or adding formatting
        to the already filtered and sorted data.
        """
        return data

    def get_queryset(self):
        """
        Returns the `QuerySet`.

        If model and queryset are both missing it raises and exception.
        """
        if self.queryset is not None and isinstance(self.queryset, QuerySet):
            return self.queryset.all()

        if self.model is not None:
            return self.model._default_manager.all()

        raise ImproperlyConfigured(
            "%(cls)s is missing a QuerySet. Define "
            "%(cls)s.model, %(cls)s.queryset, or override "
            "%(cls)s.get_queryset()." % {"cls": self.__class__.__name__}
        )


class ServerSideDatatableMixin(ServerSideDataTablesMixin):
    def __init_subclass__(cls, **kwargs):
        """This throws a deprecation warning on subclassing."""
        warn(
            f"{cls.__name__} inherits from ServerSideDatatableMixin which has been deprecated. Please use ServerSideDataTablesMixin instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init_subclass__(**kwargs)

    def __init__(self, *args, **kwargs):
        """This throws a deprecation warning on initialization."""
        warn(
            f"{self.__class__.__name__} has been deprecated. Please use ServerSideDataTablesMixin instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(*args, **kwargs)
