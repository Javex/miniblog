<%inherit file="layout.mako" />
<%block name="body">
<form method="post">
	${form.name.label} ${form.name()}
	${form.submit()}
</form>
</%block>