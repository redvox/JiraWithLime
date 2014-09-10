import sublime, sublime_plugin
from JiraWithLime.lime_connection import LimeConnection
from JiraWithLime.lime_issue import LimeIssue
from JiraWithLime.util import Util

class CreateTestCycleCommand(sublime_plugin.TextCommand):
	def run(self, edit, issue_key=None):
		self.window = self.view.window()
		if not issue_key:
			self.window.run_command('prompt_issue_key',
								{'callback': 'create_test_cycle'})
		else:
			self.connection = LimeConnection()
			self.issue = self.connection.get(issue_key)
			self.key = self.issue.key
			self.version = self.issue.version
			self.versionId = self.issue.versionId
			self.environment = ""
			self.window.show_input_panel('Sprint:', self.issue.version, self.setSprint, None, None)	
				
	def setSprint(self, uinput):
		if self.version != uinput:
			self.version = uinput
			util = Util()
			self.versionId = util.findVersionId(self.issue.projectId, uinput)
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
    		"projectId": self.issue.projectId,
    		"versionId": self.versionId
		}

		response, data = self.connection.createTestCycle("", testCycle)
		cycleId = data['id']

		testLinks = self.issue.getAllTestLinks()

		issuesForCycle = {
		    "issues": testLinks,
		    "versionId": self.versionId,
		    "cycleId": cycleId,
		    "projectId": self.issue.projectId,
		    "method": "1"
		}

		response = self.connection.addTestsToTestCycle(issuesForCycle)

		sublime.message_dialog("Finish")


	
