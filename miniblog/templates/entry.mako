<%inherit file="layout.mako" />
<%def name="display_entry(entry)">
	<h1><a href="${view.request.route_url('view_entry', id_=entry.id)}">${entry.title}</a></h1>
	<span class="date">Posted on: ${entry.entry_time.strftime('%Y-%m-%d %H:%M:%S')}</span>
	<p>${entry.text|n}</p>
</%def>

<%block name="body">
	${display_entry(entry)}
    <div id="disqus_thread"></div>
    <script type="text/javascript">
        /* * * CONFIGURATION VARIABLES: EDIT BEFORE PASTING INTO YOUR WEBPAGE * * */
        var disqus_shortname = '${view.request.registry.settings["disqus_shortname"]}'; // required: replace example with your forum shortname

        /* * * DON'T EDIT BELOW THIS LINE * * */
        (function() {
            var dsq = document.createElement('script'); dsq.type = 'text/javascript'; dsq.async = true;
            dsq.src = '//' + disqus_shortname + '.disqus.com/embed.js';
            (document.getElementsByTagName('head')[0] || document.getElementsByTagName('body')[0]).appendChild(dsq);
        })();
    </script>
    <noscript>Please enable JavaScript to view the <a href="http://disqus.com/?ref_noscript">comments powered by Disqus.</a></noscript>
    <a href="http://disqus.com" class="dsq-brlink">comments powered by <span class="logo-disqus">Disqus</span></a>
</%block>
