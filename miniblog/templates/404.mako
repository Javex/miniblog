<%inherit file="layout.mako" />

<%block name="title">404 - Page not found - </%block>

<%block name="body">
<h1>Error 404: Page does not exist</h1>
<p>The page you requested does not exist. The error message is: <i>"${msg}"</i></p>
</%block>
