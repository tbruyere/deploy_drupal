from fabric.api import *
import fabric.api
import time

env.user = 'aegir'
env.shell = '/bin/bash -c'
env.key_filename = '/path/to/aegir/key'

def getSiteUri(platform, branch, uri):
  sitename = platform + '.' + branch + '.' + uri
  return sitename

def getSiteAlias(platform, branch):
  sitealias = '@site_' + platform + '_' + branch
  return sitealias

def getPlatformAlias(platform, branch):
  return '@platform_' + platform + '_' + branch

# Creation de la plateform sur le serveur aegir
def build_platform(platform, branch, root):
	print "===> Building the platform..."
	platformalias = getPlatformAlias(platform, branch)
	run("drush --root='%s' provision-save '%s' --context_type='platform'" % (root,platformalias))
	run("drush @hostmaster hosting-import '%s'" % platformalias)
	run("drush @hostmaster hosting-dispatch")

# Install a site on a platform, and kick off an import of the site
def install_migrate_site(platform, branch, uri, root, webserver, dbserver, profile):
	platformalias = getPlatformAlias(platform, branch)
	sitealias = getSiteAlias(platform, branch)
	siteuri = getSiteUri(platform, branch, uri)  
	source = root + '/sites/' + siteuri
	print source
	if not fabric.contrib.files.exists(source):
		print "==> INSTALL SITE FIRST TIME"
		save_alias(sitealias,platformalias,siteuri, webserver, dbserver, profile)
		install_site(sitealias,platformalias)
	else :		
		print "==> UPDATE SITE"
		migrate_site(sitealias,platformalias)
		
def migrate_site(sitealias, platformalias):
	print "===> Migrating the site to the new platform"
	run("drush %s provision-migrate '%s'" % (sitealias,platformalias))
		
def install_site(sitealias, platformalias):
	print "===> Install site on the new platform..."
	run("drush %s provision-install" % (sitealias))
	run("drush @hostmaster hosting-task %s verify" % (platformalias))
	time.sleep(5)
	run("drush @hostmaster hosting-dispatch")
		
# Save the Drush alias to reflect the new platform
def save_alias(sitealias, platformalias, siteuri, webserver, dbserver, profile):
	print "===> Updating the Drush alias for this site"	
	run("drush provision-save %s --context_type=site --uri=%s --platform=%s --server=@server_%s --db_server=@server_%s --profile=%s --client_name=admin" % (sitealias, siteuri, platformalias, webserver, dbserver, profile))
		
