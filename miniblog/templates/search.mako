<%inherit file="layout.mako" />

<%namespace name="entry_file" file="entry.mako" />
<%block name="body">
% if results:
	% for entry in results:
		${entry_file.display_entry(entry)}
	% endfor
% else:
	Nothing found... Sorry!
% endif
</%block>