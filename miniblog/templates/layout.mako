<% from pyramid.security import authenticated_userid, has_permission %>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<!--

	Design by Free CSS Templates
	http://www.freecsstemplates.org
	Released for free under a Creative Commons Attribution License

	Name       : Temporary Issue
	Version    : 1.0
	Released   : 20130222

-->
<html xmlns="http://www.w3.org/1999/xhtml">
	<head>
		<meta name="keywords" content="" />
		<meta name="description" content="" />
		<meta http-equiv="content-type" content="text/html; charset=utf-8" />
		<meta http-equiv="X-UA-Compatible" content="IE=Edge">
		<title>
		<%block name="title" /> ${view.request.registry.settings["title"]}
		</title>
		<link href="http://fonts.googleapis.com/css?family=Arvo" rel="stylesheet" type="text/css" />
		<link href="http://fonts.googleapis.com/css?family=Bitter" rel="stylesheet" type="text/css" />
		<link rel="stylesheet" type="text/css" href="/static/style.css" />
		<script src="https://login.persona.org/include.js"></script>
		<script src="${view.request.static_url('miniblog:static/jquery.js')}"></script>
		<script type="text/javascript">jQuery.noConflict();</script>
		<script type="text/javascript">
		jQuery(document).ready(function() {
		
		    jQuery("#login-wrap").hover(
		        function() {jQuery("#login-wrap a").fadeIn(500);}, //enter event
		        function() {jQuery("#login-wrap a").fadeOut(500);} //leave event
	        );
		
		
		
		    // Persona stuff
			jQuery("#signin").click(function() { navigator.id.request(); return false;});
	        jQuery("#signout").click(function() { navigator.id.logout(); return false;});
            
            var currentUser = ${'"%s"' % authenticated_userid(view.request) if authenticated_userid(view.request) else 'null'|n};
            
            navigator.id.watch({
                loggedInUser: currentUser,
                onlogin: function(assertion) {
                    jQuery.post("${view.request.route_url('login')}", 
                        {assertion: assertion},
                        function(res, status, xhr) { console.log("Logging in"); window.location.reload(); }
                    )
                    .fail(
                        function(xhr, status, err) { 
                            navigator.id.logout();
                            alert("Login failure: " + err);
                        }
                    );
                },
                
                onlogout: function() {
                    jQuery.post(
                        "${view.request.route_url('logout')}",
                        function(res, status, xhr) { console.log("Logging out..."); window.location.reload(); }
                    )
                    .fail(
                        function(xhr, status, err) { alert("Logout failure: " + err); }
                    );
                }
            });
		});

		</script>
	</head>
	<body>
		<div id="outer">
			<div id="header">
				<div id="logo">
					<h1>
						<a href="${view.request.route_url('home')}">${view.request.registry.settings["title"]}</a>
					</h1>
				</div>
				<div id="search">
					<form action="${view.request.route_url('search')}" method="get">
						<fieldset>
							<input class="text" name="search" size="40" maxlength="128" />
						</fieldset>
					</form>
				</div>
				<div id="nav">
					<ul>
						<li class="first">
							<a href="${view.request.route_url('home')}">Blog</a>
						</li>
						<li>
							<a href="${view.request.route_url('about')}">About</a>
						</li>
						<li>
						    <a href="${view.request.route_url('view_categories')}">Categories</a>
						</li>
						% if has_permission("edit", view.request.context, view.request):
						<li>
							<a href="${view.request.route_url('add_entry')}">Add Entry</a>
						</li>
						<li>
							<a href="${view.request.route_url('manage_categories')}">Manage Categories</a>
						</li>
						% endif
						<li id="login-wrap">
						     % if not authenticated_userid(view.request):
						        <a id="signin" href="">Login</a>
					        % else:
					            <a id="signout" href="">Logout</a>
				            % endif
						</li>
					</ul>
				</div>
			</div>
			<div id="main">
				<div id="content">
			    % if view.request.session.peek_flash():
				    <ul>
			        % for index, message in enumerate(view.request.session.pop_flash(), 1):
				        <li class="
				        % if index == 1:
						    first
						% elif index == len(view.categories):
						    last
						% endif
				        ">${message}</li>
			        % endfor
				    </ul>
			    % endif
					${self.body()}
					<br class="clear" />
				</div>
				<div id="sidebar_wrap">
				    <div id="sidebar2">
				        <h3>
						    Categories
					    </h3>
				    % if view.categories:
					    <ul>
					    % for index, category in enumerate(view.categories, 1):
						    <li class="
						    % if index == 1:
						    first
						    % elif index == len(view.categories):
						    last
						    % endif
						    ">
							    <a href="${view.request.route_url('view_category', id_=category.name)}">
								    ${category.name}
							    </a>
						    </li>
					    % endfor
					    </ul>
				    % else:
				        <p>No categories have been added yet.</p>
			        % endif
				    </div>
				    <div id="sidebar1">
					    <h3>
						    About
					    </h3>
					    <p>
						    This blog is about posting some interesting, mostly technical stuff.
					    </p>
				    </div>
				    <div id="sidebar12">
					    <h3>
						    Recent posts
					    </h3>
					    % if view.recent:
					    <ul>
					    % for index, entry in enumerate(view.recent, 1):
						    <li class="recent 
						    % if index == 1:
						    first
						    % elif index == len(view.recent):
						    last
						    % endif
						    ">
							    <a href="${request.route_url('view_entry', id_=entry.id)}" title="${entry.title}">
							    % if len(entry.title) > 31:
							        ${entry.title[:28] + "..."}
							    % else:
								    ${entry.title}
							    % endif
							    </a>
							    <span class="date">&nbsp;(${entry.pretty_date})</span>
						    </li>
					    % endfor
					    </ul>
					    % else:
					        No posts have been made yet.
					    % endif
					    
				    </div>
				</div>
				<br class="clear" />
			</div>
			<!--
			<div id="footer">
				<div id="footerContent">
					<h3>
						Suspendisse non commodo
					</h3>
					<p>
						Nisl iaculis arcu cubilia vitae. Suspendisse proin enim feugiat aenean aliquet proin quam. Risus 
						placerat nisl sapien donec velit ornare cursus. Massa rhoncus fringilla eu aliquam. Facilisis orci 
						tristique iaculis ridiculus tellus. Odio nibh mauris velit nullam. Placerat hendrerit montes ligula 
						aenean cras. Eget augue tempus ipsum feugiat. Curae pellentesque penatibus dis velit. Augue felis 
						nisl vel natoque duis mollis diam. Nullam sollicitudin massa curabitur. Lorem ipsum dolor sit amet
						nullam consequat etiam arcu cubilia cursus massa eu aliquam. Orci tristique velit nullam sed
						etiam tellus odio nibh mauris.
					</p>
				</div>
				<div id="footerSidebar2">
					<h3>
						Turpis mus elit
					</h3>
					<ul>
						<li class="first">
							<a href="#">Felis duis aliquam</a>
						</li>
						<li>
							<a href="#">Convallis sed auctor</a>
						</li>
						<li>
							<a href="#">Blandit sed tempus</a>
						</li>
						<li class="last">
							<a href="#">Duis et hendrerit</a>
						</li>
					</ul>
				</div>
				<div id="footerSidebar1">
					<h3>
						Etiam mollis
					</h3>
					<ul>
						<li class="first">
							<a href="#">Sed lacinia cubilia</a>
						</li>
						<li>
							<a href="#">Risus euismod fusce</a>
						</li>
						<li>
							<a href="#">Malesuada molestie</a>
						</li>
						<li class="last">
							<a href="#">Felis dolore nullam</a>
						</li>
					</ul>
				</div>
			</div>
			-->
		</div>
		<div id="copyright">
				&copy; ${view.request.registry.settings["title"]} | Design by <a href="http://www.freecsstemplates.org/">FCT</a> | Powered By <a href="https://github.com/Javex/miniblog">miniblog</a>
		</div>
	</body>
</html>
