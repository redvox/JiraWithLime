import sublime, sublime_plugin
from JiraWithLime.update import Update


up = Update()
if up.checkForUpdate():
	sublime.message_dialog("There is a new version of JiraWithLime. Please wait a moment while i update your files.")
	up.update()
	sublime.message_dialog("Update Complete.")