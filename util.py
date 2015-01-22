import sublime, sublime_plugin
import json
from JiraWithLime.lime_connection import LimeConnection

class Util():
	@staticmethod
	def getProjectId(projectKey):
		connection = LimeConnection()
		response, data = connection.getProjectId(projectKey)
		return data["id"]

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

	@staticmethod
	def getEpicMap():
		name = 'JiraWithLime.sublime-settings'
		settings = sublime.load_settings(name)
		project = settings.get('project', '')

		conn = LimeConnection()
		r = conn.getEpics(project)
		epicMap = json.loads(r.text)["epicNames"]
		epicArray = []
		for epic in epicMap:
			epicArray.append(epic["name"])
		return epicMap, epicArray

	@staticmethod
	def getAllIssueKeysFromSearch(fields, values):
		searchString = ""
		for i in range(len(fields)):
			searchString+=fields[i]
			searchString+=" = "
			searchString+=values[i]
			if(i < len(fields)-1): searchString+=" and "

		searchJson = {
			'jql' : searchString,
			"startAt" : 0,
			"maxResults" : 100,
			"fields" : ["id","key","issuetype"]
		}

		connection = LimeConnection()
		response, data = connection.searchIssues(searchJson)
		testList = []
		for issue in data['issues']:
			# issue['fields']['key']
			print("issueField", issue['key'])
			testList.append(issue['key'])
		return testList

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

class insertEpics(sublime_plugin.TextCommand):
	def run(self, edit, epicName=None):
		if not epicName:
			self.epicMap, self.epicArray = Util.getEpicMap()
			window = self.view.window()
			window.show_quick_panel(self.epicArray, self.run_command)
		else:
			self.insert(edit, epicName)

	def run_command(self, value):
		self.view.run_command(
                    "insert_epics",
                    {
                        "epicName": self.epicArray[value]
                    }
                )

	def insert(self, edit, epicName):
		regionSet = self.view.sel()
		for region in regionSet:
			string = self.view.substr(region)
			self.view.insert(edit, region.begin(), epicName)
			# self.view.insert(edit, region.begin(), tagOpen)
			#self.view.insert(edit, region.end()+len(tagOpen), tagEnd)
		
