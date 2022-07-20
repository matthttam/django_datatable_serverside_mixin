# Django Serverside Datatable

This is a fork of Umesh Krishna's django-serverside-datable which was written for an older version of datatables. This updated version has been rewritten. Thanks to Umesh for the foundation to start from.

This is a  package that let you use views with DataTables.net server-side processing in your Django Project.

Supports datatable features such as Pagination, Search, filtering, etc...

## Install

```
pip install django-datatable-serverside-mixin
```


## How to use

Create a django View that inherits from  **ServerSideDatatableMixin**.
Example (backend):

```python
# views.py

from django_serverside_datatable_mixin.views import ServerSideDatatableMixin


class ItemListView(ServerSideDatatableMixin):
	queryset = models.Item.objects.all()
	columns = ['name', 'code', 'description']


# urls.py
# add the following line to urlpatterns

path('data/', views.ItemListView.as_view()), 

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
		<h1>Items</h1>
		<hr>
		<table id="items-table">
			<thead>
				<tr>
					<th>Name</th>
					<th>Code</th>
					<th>Description</th>
				</tr>
			</thead>
			<tbody></tbody>
		</table>

		<script src="https://code.jquery.com/jquery-3.3.1.min.js"></script>
		<script src="https://cdn.datatables.net/1.10.19/js/jquery.dataTables.min.js"></script>
		<script language="javascript">
			$(document).ready(function () {
				$('#items-table').dataTable({
					serverSide: true,
					sAjaxSource: "http://127.0.0.1:8000/data/",  // new url
                                        columns: [
                                            {name: "name", data: 0},
                                            {name: "code", data: 1},
                                            {name: "description", data: 2},
                                        ],
				});
			});
		</script>
	</body>
</html>
```
The dataTables `columns` option must be set in the dataTable initialization. Each column is `required` to have a name coresponding to the views `columns` array. Data can optionally be set to the same field values to add readable keys to the json responses.

For further customization of Datatable, you may refer the Datatable official documentation.

#
## To Do:
- Implement global REGEX filtering
- Implement per column filtering
- Implement per column regex filtering
- Write tests