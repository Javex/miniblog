<%inherit file="layout.mako" />
<%block name="body">
<% from miniblog.models import pretty_date %>
<ul>
% for index, (category, last_entry) in enumerate(categories, 1):
    <li class="
    % if index == 1:
    first
    % elif index == len(view.categories):
    last
    % endif
    ">
        <a href="${view.request.route_url('view_category', id_=category.name)}">${category.name}</a>
        <span class="date">(Last post: ${pretty_date(last_entry) if last_entry else 'No posts made yet'})</span>
    </li>
% endfor
</ul>

${categories.pager()}
</%block>
