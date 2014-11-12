import sublime, sublime_plugin
from JiraWithLime.lime_connection import LimeConnection
from JiraWithLime.lime_issue import LimeIssue
from JiraWithLime.util import Util

class CreateTestCycleCommand(sublime_plugin.TextCommand):
	def run(self, edit, cycletype, issue_key=None):
		self.window = self.view.window()
		self.util = Util()
		settings = sublime.load_settings('JiraWithLime.sublime-settings')
		self.projectKey = settings.get('project', "")
		self.cycletype = cycletype
		if not issue_key:
			window = self.view.window()
			call = lambda v: window.run_command('create_test_cycle', {'cycletype': cycletype, 'issue_key': v})
			if cycletype == "story":
				window.show_input_panel('Key', self.projectKey + "-", call, None, None)
			else:
				window.show_input_panel('Lable', "", call, None, None)

		else:
			self.connection = LimeConnection()
			self.environment = ""
			self.version = ""
			self.versionId = ""
			self.key = issue_key
			if cycletype == "story":
				self.issue = self.connection.get(issue_key)
				self.version = self.issue.version
				self.versionId = self.issue.versionId
				self.projectId = self.issue.projectId
				print("projectID #### ", str(self.issue.projectId))
				self.window.show_input_panel('Sprint:', self.version, self.setSprint, None, None)	
			else:
				self.projectId = self.util.getProjectId(self.projectKey)
				self.window.show_input_panel('Sprint:', "Sprint-", self.setSprint, None, None)	
				
	def setSprint(self, uinput):
		if self.version != uinput:
			self.version = uinput
			self.versionId = self.util.findVersionId(self.projectId, uinput)
		self.window.show_input_panel('Umgebung:', "Develop", self.setEnvironment, None, None)	

	def setEnvironment(self, uinput):
		self.environment = uinput
		self.pushCycle()

	def pushCycle(self):
		testCycle = {
    		"clonedCycleId": "",
    		"name": self.key,
    		"build": self.version,
    		"environment": self.environment,
    		# "description": "Released Cycle1",
    		# "startDate": "17/Oct/13",
    		# "endDate": "17/Jan/14",
    		"projectId": self.projectId,
    		"versionId": self.versionId
		}

		response, data = self.connection.createTestCycle("", testCycle)
		cycleId = data['id']

		if self.cycletype == "story":
			testcaseLinks = self.issue.getAllTestLinks()
		else: 
			testcaseLinks = self.util.getAllIssueKeysFromSearch(["project", "issuetype", "labels"], [self.projectKey, "Test", self.key])

		issuesForCycle = {
		    "issues": testcaseLinks,
		    "versionId": self.versionId,
		    "cycleId": cycleId,
		    "projectId": self.projectId,
		    "method": "1"
		}

		response = self.connection.addTestsToTestCycle(issuesForCycle)
		sublime.message_dialog("Finish")