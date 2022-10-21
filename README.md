# Django Serverside DataTables

This is a fork of Umesh Krishna's django-serverside-datatable which was written for an older version of DataTables. This updated version has been rewritten. Thanks to Umesh for the foundation to start from.

This is  package that lets you easily extend views to work with DataTables.net server-side processing in your Django Project.

Supports DataTables features such as Pagination, Search, filtering, etc...

## Requirements
- Pythin version 3.10+ (may work on older versions but is untested)
- Django version 3.x or 4.x

## Install

```
pip install django-datatable-serverside-mixin
```


## How to use

Create a django View that inherits from  **ServerSideDatatableMixin**.
Example (backend):

```python
# views.py

from django_serverside_datatable_mixin.views import ServerSideDataTablesMixin


class PersonListView(ServerSideDatatableMixin):
	queryset = Person.objects.all()
	columns = ['person_name', 'person_code', 'person_description','person__building__name']
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
The dataTables `columns` option must be configured in the dataTable initialization. Each column is `required` to have a `data` attribute corresponding to the view's `columns` array. Name is optional as of version 2.0.0 and is no longer used.

The `data` attribute must correspond to a valid field provided by the view and must ultimately match an attribute on records in your queryset. Use annotations on your queryset if you prefer data values that don't look like "person__building__name."

This is generally compatible with DataTables features such as ColReorder and colvis.

For further customization of Datatable, you may refer the [Datatables.net official documentation](https://datatables.net/manual/).

### Data Callback
ServerSideDataTablesMixin provides a callback method named data_callback that can be overridden. Use this method to change the formatting or add/remove any pieces of data. This gives you full flexibility to render the data *after* everything has been sorted, filtered, paginated, etc...


```python
class PersonListView(ServerSideDataTablesMixin):
	def data_callback(self, data: list[dict]) -> list[dict]:
		for row in data:
			row["actions"] = render_to_string(
				"people/table_row_buttons.html",
				context={"person": row},
				request=self.request,
			)
			row["id"] = f"{<b>row['id']</b>"
		return super().data_callback(data)
```

In the example above the data for the ID column would render with <b> tags to make it bold. The table_row_buttons.html template would render buttons based on the person object. This text is added to the `row["actions"]` attribute and the javascript would look for a column definition for `data: "actions"`.

# Updates
## New in version 2.1.1:
- Fix deprecation issues where inheritance would not function as expected.
- Fixed readme typos.
## New in version 2.1.0:
- Renamed ServerSideDatatableMixin to ServerSideDataTablesMixin. A deprecation warning will trigger if the old class name is used.
- Added a data_callback method to ServerSideDataTablesMixin which can be used to manipulate the data just before rendering to JSON. Useful for adding HTML or modifying any data fields based on view context (like permissions).
## New in version 2.0.0:
- Fixed a bug where using a -1 for the pagination length would not work as expected (now provides all records)
- Implemented regex filtering
- Implemented column based filtering
- Wrote tests
- Refactored all code to streamline the process and speed up queries
