<%inherit file="layout.mako" />
<form method="POST">
	${form.title.label} ${form.title()} <div class="clr"></div>
	${form.text.label} ${form.text()} <div class="clr"></div>
	${form.category.label} ${form.category()} <div class="clr"></div>
	${form.submit()} <div class="clr"></div>
</form>
