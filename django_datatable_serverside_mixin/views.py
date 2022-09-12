from django.views import View
from django.http import JsonResponse
from django.core.exceptions import ImproperlyConfigured
from django.db.models import QuerySet
from . import datatable


class ServerSideDatatableMixin(View):
    columns = None
    queryset = None
    model = None

    def get(self, request, *args, **kwargs):
        result = datatable.DataTablesServer(
            request, self.columns, self.get_queryset()
        ).get_output_result()
        return JsonResponse(result, safe=False)

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

        return queryset
