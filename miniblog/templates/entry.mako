<%inherit file="layout.mako" />
<%def name="display_entry(entry)">
	<h1><a href="${request.route_url('view_entry', id_=entry.id)}">${entry.title}</a></h1>
	<p>${entry.text|n}</p>
</%def>

<%block name="body">
	${display_entry(entry)}
</%block>