# Django Serverside Datatable

This is a fork of Umesh Krishna's django-serverside-datable which was written for an older version of datatables. This updated version has been rewritten. Thanks to Umesh for the foundation to start from.

This is  package that lets you easily extend views to work with DataTables.net server-side processing in your Django Project.

Supports datatable features such as Pagination, Search, filtering, etc...

## Requirements
- Pythin version 3.10+ (may work on older versions but is untested)
- Django version 3.x or 4.x

## Install

```
pip install django-datatable-serverside-mixin
```


## How to use

Create a django View that inherits from  **ServerSideDatatableMixin**.

- `queryset` is required or you can override `get_queryset()`. When specifying a queryset be sure you include all related models as needed.
For example, if you request related_thing__otherm_model__value you would .select_related("related_thing","related_thing__other_model"). Failing to retrieve the fields you need will result in an error especially when searching!
- `columns` is required and is an array of strings specifying the fields that will be retrieved from the queryset. The view will only return fields listed in this columns array thus preventing anyone from fetching anything they want from your models.

Example (backend):

```python
# views.py

from django_serverside_datatable_mixin.views import ServerSideDatatableMixin


class PersonListView(ServerSideDatatableMixin):
	# Be sure to use select_related to fetch fields of related models
	queryset = Person.objects.all().select_related("building")
	columns = ['name', 'code', 'description','building__name']
```
```python
# urls.py
# add the following element to your urlpatterns array

path('data/', views.PersonListView.as_view()), 

```

Example (frontend):

```html
<!DOCTYPE html>
<html>
	<head>
		<meta charset="utf-8">
		<link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.12.1/css/jquery.dataTables.min.css"/>
 
	<script type="text/javascript" src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
	<script type="text/javascript" src="https://cdn.datatables.net/1.12.1/js/jquery.dataTables.min.js"></script>
	</head>
	<body>
		<h1>People</h1>
		<hr>
		<table id="people-table">
			<thead>
				<tr>
					<th>Name</th>
					<th>Code</th>
					<th>Description</th>
					<th>Building Name</th>
				</tr>
			</thead>
			<tbody></tbody>
		</table>

		<script src="https://code.jquery.com/jquery-3.3.1.min.js"></script>
		<script src="https://cdn.datatables.net/1.10.19/js/jquery.dataTables.min.js"></script>
		<script language="javascript">
			$(document).ready(function () {
				$('#people-table').dataTable({
					serverSide: true,
					sAjaxSource: "http://127.0.0.1:8000/data/",  // new url
                                        columns: [
                                            {name: "name", data: "name"},
                                            {name: "code", data: "code"},
                                            {name: "description", data: "description"},
                                            {name: "building", data: "building__name"},
                                        ],
				});
			});
		</script>
	</body>
</html>
```
The dataTables `columns` option must be configured in the dataTable initialization. Each column is `required` to have a `data` attribute coresponding to the view's `columns` array. Name is optional as of version 2.0.0 and is no longer used.

The `data` attribute must corespond to a valid field provided by the view and must ultimately match an attribute on records in your queryset. Use annotations on your queryset if you prefer data values that don't look like "person__building__name."

This is generally compatible with datatable features such as ColReorder and colvis.

For further customization of Datatable, you may refer the [Datatables.net official documentation](https://datatables.net/manual/).

# Updates
## New in version 2.0.0:
- Fixed a bug where using a -1 for the pagination length would not work as expected (now provides all records)
- Implemented regex filtering
- Implemented column based filtering
- Wrote tests
- Refactored all code to streamline the process and speed up queries
