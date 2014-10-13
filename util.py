import sublime, sublime_plugin
from JiraWithLime.lime_connection import LimeConnection

class Util():
	@staticmethod
	def findVersionId(projectID, name): #10905
		versionId = -1
		connection = LimeConnection()
		response, data = connection.getAllVersionsOfProject(projectID)
		for v in data['unreleasedVersions']:
			if v['label'] == name:
				versionId = v['value']
				break
		for v in data['releasedVersions']:
			if v['label'] == name:
				versionId = v['value']
				break
		if versionId == -1:
			sublime.error_message("Could not find Version "+name)
			raise Exception("Could not find Version")
		return versionId

class SaveUsername(sublime_plugin.TextCommand):
	def run(self, edit):
		self.window = self.view.window()
		self.window.show_input_panel('Username', "", self.save_user, None, None)

	def save_user(self, user_input):
		self.username = user_input
		self.window.show_input_panel('Password', "", self.save_password, None, None)
		
	def save_password(self, user_input):
		self.password = user_input
		import base64
		enc_username = base64.b64encode(self.username.encode('utf-8')).decode('utf-8')		
		print("enc_username", enc_username)
		enc_password = base64.b64encode(self.password.encode('utf-8')).decode('utf-8')
		print("enc_password", enc_password)
		name = 'JiraWithLime.sublime-settings'
		settings = sublime.load_settings(name)
		settings.set('username', enc_username)
		settings.set('password', enc_password)
		sublime.save_settings(name)