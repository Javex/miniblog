<%inherit file="layout.mako" />
<%def name="display_entry(entry)">
	<h1><a href="${request.route_url('view_entry', id_=entry.id)}">${entry.title}</a></h1>
	<span class="date">Posted on: ${entry.entry_time.strftime('%Y-%m-%d %H:%M:%S')}</span>
	<p>${entry.text|n}</p>
</%def>

<%block name="body">
	${display_entry(entry)}
</%block>
