# Copyright Aap Ka Manch
# License GNU General Public Licence

from __future__ import unicode_literals

import webnotes, json

no_cache = True

def get_context():
	unit = webnotes.request.path[1:]
	try:
		if not unit or unit.lower().split(".")[0]=="index":
			unit = "India"
		
		return {"content": get_unit_html(unit)}
	except webnotes.DoesNotExistError:
		return {"content": '<div class="alert alert-warning">The page you are looking for does not exist.</div>'}
	
def get_unit_html(unit):
	def _get_unit_html(unit):
		unit = webnotes.doc("Unit", unit)

		context = {
			"name": unit.name,
			"parent": unit.parent_unit,
			"parent_title": webnotes.conn.get_value("Unit", unit.parent_unit, "unit_title"),
			"children": webnotes.conn.sql("""select name, unit_title 
				from tabUnit where 
					ifnull(`public`,0) = 1 
					and parent_unit=%s""", (unit.name), as_dict=1),
			"post_list_html": get_post_list_html(unit.name)
		}
	
		return webnotes.get_template("templates/includes/unit.html").render(context)

	return _get_unit_html(unit)
	#return webnotes.cache().get_value("unit_html:" + unit, lambda:_get_unit_html(unit))

@webnotes.whitelist(allow_guest=True)
def get_post_list_html(unit, limit_start=0, limit_length=20):
	if webnotes.local.form_dict.cmd=="get_post_list_html":
		if not get_access(unit).get("read"):
			raise webnotes.PermissionError
	
	posts = webnotes.conn.sql("""select 
		p.creation, p.content, pr.fb_username, pr.first_name, pr.last_name 
		from tabPost p, tabProfile pr
		where p.unit=%s and pr.name = p.owner order by p.creation desc limit %s, %s""", 
			(unit, limit_start, limit_length), as_dict=True)
			
	return webnotes.get_template("templates/includes/post_list.html").render({"posts": posts, 
		"limit_start":limit_start})
