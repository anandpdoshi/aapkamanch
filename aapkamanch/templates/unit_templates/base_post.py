# Copyright Aap Ka Manch
# License GNU General Public Licence

from __future__ import unicode_literals
import webnotes
from webnotes.utils import get_fullname

def get_unit_html(context):
	post = webnotes.doc("Post", webnotes.form_dict.name)
	if post.parent_post:
		raise webnotes.PermissionError
		
	context["unit_title"] += " by {}".format(get_fullname(post.owner))
	context["parent_post_html"] = get_parent_post_html(post, context)
	context["post_list_html"] = get_child_posts_html(post, context.get("view"))
	context["parent_post"] = post.name

def get_parent_post_html(post, context):
	profile = webnotes.bean("Profile", post.owner).doc
	for fieldname in ("first_name", "last_name", "user_image", "fb_hometown", "fb_location"):
		post.fields[fieldname] = profile.fields[fieldname]
	
	return webnotes.get_template("templates/includes/inline_post.html")\
		.render({"post": post.fields, "view": context.get("view"), "view_options": context.get("view_options")})

def get_child_posts_html(post, view):
	posts = webnotes.conn.sql("""select p.*, pr.user_image, pr.first_name, pr.last_name
		from tabPost p, tabProfile pr
		where p.parent_post=%s and pr.name = p.owner
		order by p.creation asc""", (post.name,), as_dict=True)
			
	return webnotes.get_template("templates/includes/post_list.html")\
		.render({
			"posts": posts,
			"parent_post": post.name,
			"view": view
		})