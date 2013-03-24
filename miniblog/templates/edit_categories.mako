<%inherit file="layout.mako" />
<%block name="body">
<form method="post">
    <legend>Add a category</legend>
	${form.name.label} ${form.name()}
	${form.submit()}
</form>
<br />

% if categories:
<div>
    <h3>Currently available categories:</h3>
    <ul>
    % for index, category in enumerate(categories, 1):
        <li class="category_list
        % if index == 1:
		    first
		% elif index == len(view.categories):
		    last
		% endif
        ">
            <a class="clickable-icon" href="${view.request.route_url('delete_category', name_=category.name)}">
                <img src="${view.request.static_url('miniblog:static/images/Cross-32.png')}" class="header-icon"/>
            </a>
            ${category.name}
        </li>
    % endfor
    </ul>
</div>
% endif
</%block>
