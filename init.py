import sublime, sublime_plugin
from JiraWithLime.update import Update
import os

def plugin_loaded():
	raw_version_url = 'https://raw.githubusercontent.com/redvox/JiraWithLime/master/'
	repo_url = 'https://github.com/redvox/JiraWithLime/archive/'
	print("Starting Up JiraWithLime "+os.getcwd())
	print(sublime.packages_path())
	path = sublime.packages_path()+'/JiraWithLime/'
	up = Update(path, raw_version_url, repo_url)
	try:
		outdated = up.checkForUpdate()
		if outdated:
			sublime.message_dialog("There is a new version of JiraWithLime. Please press OK and wait a moment while i update your files.")
			up.update()
			window = sublime.active_window()
			window.open_file(path+'/changelog.txt')
	except:
		print("There was a problem with your connection.")