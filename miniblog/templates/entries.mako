<%inherit file="layout.mako" />
<%namespace name="entry_file" file="entry.mako" />

<%block name="body">
% for entry in entries:
	${entry_file.display_entry(entry)}
% endfor

${entries.pager()}
</%block>
