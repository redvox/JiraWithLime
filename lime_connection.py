import sublime, sublime_plugin
import json
import base64
from . import requests
from JiraWithLime.lime_issue import LimeIssue

class LimeConnection:

	def __init__(self):
		settings = sublime.load_settings('JiraWithLime.sublime-settings')
		self.username = base64.b64decode(settings.get('username')).decode('utf-8')
		self.password = base64.b64decode(settings.get('password')).decode('utf-8')
		self.baseURL = settings.get('baseURL')
		
		self.issueURL = self.baseURL + "/rest/api/2/issue/"
		self.linkIssueURL = self.baseURL + "/rest/api/2/issueLink"
		self.addCommentURL = self.baseURL + "/rest/api/2/issue/%s/comment/"
		self.createTestStepURL = self.baseURL + "/rest/zapi/latest/teststep/"
		self.testCycleURL = self.baseURL + "/rest/zapi/latest/cycle/"
		self.testCycleAddTestsURL = self.baseURL + "/rest/zapi/latest/execution/addTestsToCycle/"
		self.transitionURL = self.baseURL + "/rest/api/2/issue/%s/transitions?expand=transitions.fields"
		self.uploadFileURL = self.baseURL + "/rest/api/2/issue/%s/attachment"
		# self.versionURL = self.baseURL + "/rest/api/2/version/"
		self.versionURL = self.baseURL + "/rest/zapi/latest/util/versionBoard-list"
		self.projectURL = self.baseURL + "/rest/zapi/latest/util/project-list"
		self.headers = {'content-type': 'application/json'}

	def get(self, issue):
		r = requests.get(self.issueURL+issue, headers=self.headers, auth=(self.username, self.password), verify=False)	
		self.printRequestStatus(r)
		return LimeIssue(json.loads(r.text))
	
	# """ Create Jira Issue with post """
	# def create(self, issue, data):
	# 	r = requests.post(self.issueURL+issue, data=json.dumps(data), headers=self.headers, auth=(self.username, self.password), verify=False)
	# 	self.printRequestStatus(r)
	# 	return r/jira_server/rest/zapi/latest/teststep/{issueId}

	""" Create Jira Issue with post """
	def createTestIssue(self, data):
		print("######### requests #########")
		print("Create Test Issue with data:", data)
		r = requests.post(self.issueURL, data=json.dumps(data), headers=self.headers, auth=(self.username, self.password), verify=False)
		self.printRequestStatus(r)
		print("######### requests #########")
		return r, json.loads(r.text)
	
	def createTestStep(self, issue, data):
		print("Create Test Step for", issue, "Data:", data)
		r = requests.post(self.createTestStepURL+issue, data=json.dumps(data), headers=self.headers, auth=(self.username, self.password), verify=False)
		self.printRequestStatus(r)
		return True	

	def getTestStep(self, issue):
		print("Get Test Step from", issue)
		r = requests.get(self.createTestStepURL+issue, headers=self.headers, auth=(self.username, self.password), verify=False)
		self.printRequestStatus(r)
		return r, json.loads(r.text)	

	def updateTestStep(self, issue_with_id, data):
		print("Update Teststep for", issue_with_id, "Data:", data)
		r = requests.put(self.createTestStepURL+issue_with_id, data=json.dumps(data), headers=self.headers, auth=(self.username, self.password), verify=False)
		self.printRequestStatus(r)
		return r	

	def deleteTestStep(self, issue_with_id, teststep_id):
		print("Delete Teststep for", issue_with_id, "teststep_id:", teststep_id)
		r = requests.delete(self.createTestStepURL+str(issue_with_id)+"/"+str(teststep_id), headers=self.headers, auth=(self.username, self.password), verify=False)
		self.printRequestStatus(r)
		return r

	def createLink(self, issue, data):
		print("Create Test Link for", issue, "Data:", data)
		r = requests.post(self.linkIssueURL+issue, data=json.dumps(data), headers=self.headers, auth=(self.username, self.password), verify=False)
		self.printRequestStatus(r)
		return True	
	
	def getAllVersionsOfProject(self, projectID):
		r = requests.get(self.versionURL+"?projectId="+projectID, headers=self.headers, auth=(self.username, self.password), verify=False)
		self.printRequestStatus(r)
		return r, json.loads(r.text)	

	def getAllProjects(self):
		r = requests.get(self.projectURL, headers=self.headers, auth=(self.username, self.password), verify=False)
		self.printRequestStatus(r)
		return r		
		

	""" Update Jira Issue with put """
	def update(self, issue, data):
		print("Update Jira Issue for", issue, "Data:", data)
		r = requests.put(self.issueURL+issue, data=json.dumps(data), headers=self.headers, auth=(self.username, self.password), verify=False)
		self.printRequestStatus(r)
		return r

	def createTestCycle(self, issue, data):
		print("Create Test Cycle for", issue, "Data:", data)
		r = requests.post(self.testCycleURL+issue, data=json.dumps(data), headers=self.headers, auth=(self.username, self.password), verify=False)
		self.printRequestStatus(r)
		return r, json.loads(r.text)

	def addTestsToTestCycle(self, data):
		print("Add Test to Testcyle with", "Data:", data)
		r = requests.post(self.testCycleAddTestsURL, data=json.dumps(data), headers=self.headers, auth=(self.username, self.password), verify=False)
		self.printRequestStatus(r)
		return r

	def printRequestStatus(self, request):
		print("------ RESPONSE ------")
		print(request.status_code)
		print(request.headers['content-type'])
		print(request.text)
		print("------ RESPONSE ------")

	