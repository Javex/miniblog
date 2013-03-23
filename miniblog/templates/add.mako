<%inherit file="layout.mako" />
<%namespace name="entry_file" file="entry.mako" />
% if preview:
<div>
    Preview of the entered text:
    <hr />
    ${entry_file.display_entry(preview)}
    <hr />
</div>
% endif
<form method="POST">
	${form.title.label} ${form.title(required=True)} <div class="clr"></div>
	${form.text.label} ${form.text(required=True)} <div class="clr"></div>
	${form.category.label} ${form.category()} <div class="clr"></div>
	<label>&nbsp;</label> ${form.submit()} ${form.preview()}<div class="clr"></div>
</form>
