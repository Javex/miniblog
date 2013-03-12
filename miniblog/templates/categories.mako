<%inherit file="layout.mako" />
<%block name="body">
<form method="post">
	${form.name.label} ${form.name()}
	${form.submit()}
</form>
<div>
    <ul>
    % for index, category in enumerate(categories, 1):
        <li class="category_list">
            <a class="delete" href="${view.request.route_url('delete_category', name_=category.name)}">
                <img src="${view.request.static_url('miniblog:static/images/Cross-32.png')}" class="cross"/>
            </a>
            ${category.name}
        </li>
    % endfor
    </ul>
</div>
</%block>
