import sublime, sublime_plugin
import re
from JiraWithLime.lime_connection import LimeConnection
from JiraWithLime.lime_issue import LimeIssue
from . import markdown
from . import markdown2

class CreateTestIssuesCommand(sublime_plugin.TextCommand):
	def run(self, edit, testValues):
		print("Beginn creating Test Issues")

		self.window = self.view.window()
		self.connection = LimeConnection()
		self.offset = 0

		for test in testValues:
			testIssue = {
				'fields' : {
					"project" : {
						'key' : test['project']
					},
					"summary" : test['name'],
					"description" : markdown2.markdown(test['description']),
					"issuetype" : {
						"name" : "Test"
					},
					"priority" : {
						"id": "3"
					},
					"customfield_15603" : [test['story']], #Story
					"components" : [],
					"versions" : [{"name":test['version']}],
					"labels" : test['labels'],
					"assignee" : {'name' : test['assignee']}
				}
			}

			if len(test['attributes']) > 0:
				testIssue['fields']['customfield_15604'] = []

			if len(test['testgroups']) > 0:
				testIssue['fields']['customfield_15601'] = []

			for attribut in test['attributes']:
				if attribut != '':
					testIssue['fields']['customfield_15604'].append({'value' : attribut})
			for testgroup in test['testgroups']:
				if testgroup != '':
					testIssue['fields']['customfield_15601'].append(testgroup)
			for components in test['components']:
				if components != '':
					testIssue['fields']['components'].append({"name":components})

			if(test['key'] == ''):
				self.createTest(test, testIssue, edit)
			else:
				self.updateTest(test, testIssue, edit)
		sublime.message_dialog("Finish")
	
	def createTest(self, test, testIssue, edit):
		response, data = self.connection.createTestIssue(testIssue)

		if response.status_code != 200 and response.status_code != 201 and response.status_code != 204:
			sublime.error_message("Response: "+str(response.status_code))
			raise Exception("Status was", response.status_code)
				
		test['issue_id'] = data['id']
		test['issue_key'] = data['key']

		###
		if test['keyLineNr'] > 0:
			pt = self.view.text_point(test['keyLineNr']-1+self.offset, 0)
			key_text = " "+test['issue_key']
		else:
			pt = self.view.text_point(test['testLineNr']-1+self.offset, 0)
			key_text = "\n@@ Key: "+test['issue_key']
			self.offset = self.offset + 1

		line_region = self.view.line(pt)
		pt += line_region.b - line_region.a
		self.view.insert(edit, pt, key_text)
		###

		for i in range(len(test['steps'])):
			if test['steps'][i] != '' or test['data'][i] != '' or test['result'][i] != '':
				teststep = {
					"step": test['steps'][i],
					"data": test['data'][i],
					"result": test['result'][i]
				}
				self.connection.createTestStep(test['issue_id'], teststep) #ID!  230076

		# Link Test
		# Auf die Blanke URL!!
		# inward key muss der Tests sein.
		link = {
			"type": {
		        "name": "Tests" # Tests, cloned by etc
		    },
		    "inwardIssue": {
				"key": test['issue_key'] # Ausgehend
			},
		    "outwardIssue": {
		        "key": test['story'] # Wird getestet
		    }
		}
		self.connection.createLink("", link)

	def updateTest(self, test, testIssue, edit):
		response = self.connection.update(test['key'], testIssue)

		if response.status_code != 200 and response.status_code != 201 and response.status_code != 204:
			sublime.error_message("Response: "+str(response.status_code))
			raise Exception("Status was", response.status_code)
			
		issue = self.connection.get(test['key'])
		r, data = self.connection.getTestStep(issue.id)

		for i in range(len(test['steps'])):
			if test['steps'][i] != '' or test['data'][i] != '' or test['result'][i] != '':

				teststep = {
					"step": test['steps'][i],
					"data": test['data'][i],
					"result": test['result'][i]
				}

				try:
					print("issue", issue)
					testStepId = data[i]['id']
					self.connection.updateTestStep(str(issue.id)+"/"+str(testStepId), teststep) #ID!  230076
				except IndexError:
					self.connection.createTestStep(issue.id, teststep) #ID!  230076	

		overSize = len(data) - (len(test['steps'])-1)
		if overSize > 0:
			for i in data[len(data)-overSize:]:
				print('i', i)
				testStepId = i['id']
				self.connection.deleteTestStep(issue.id, testStepId)

class CreateBugIssuesCommand(sublime_plugin.TextCommand):
	def run(self, edit, testValues):
		print("Beginn creating Bug Issues")

		self.window = self.view.window()
		self.connection = LimeConnection()
		self.offset = 0

		for test in testValues:
			testIssue = {
				'fields' : {
					"project" : {
						'key' : test['project']
					},
					"summary" : test['name'],
					"description" : markdown2.markdown(test['description']),
					"issuetype" : {
						"name" : "Bug"
					},
					"priority" : {
						"id": "3"
					},
					"components" : [],
					"fixVersions" : [{"name":test['version']}],
					# "labels" : test['labels'],
					"assignee" : {'name' : test['assignee']},
					"customfield_11018" : {"value" : test['domain']},
					"customfield_11013" : {"value": test['environment']},
					"customfield_11006" : {"value" : test['browser']}
				}
			}


			for components in test['components']:
				if components != '':
					testIssue['fields']['components'].append({"name":components})

			if(test['key'] == ''):
				self.createTest(test, testIssue, edit)
			else:
				self.updateTest(test, testIssue, edit)
		sublime.message_dialog("Finish")
	
	def createTest(self, test, testIssue, edit):
		response, data = self.connection.createTestIssue(testIssue)

		if response.status_code != 200 and response.status_code != 201 and response.status_code != 204:
			sublime.error_message("Response: "+str(response.status_code))
			raise Exception("Status was", response.status_code)
				
		test['issue_id'] = data['id']
		test['issue_key'] = data['key']

		###
		if test['keyLineNr'] > 0:
			pt = self.view.text_point(test['keyLineNr']-1+self.offset, 0)
			key_text = " "+test['issue_key']
		else:
			pt = self.view.text_point(test['testLineNr']-1+self.offset, 0)
			key_text = "\n@@ Key: "+test['issue_key']
			self.offset = self.offset + 1

		line_region = self.view.line(pt)
		pt += line_region.b - line_region.a
		self.view.insert(edit, pt, key_text)
		###
		self.createLinks(test)

	def updateTest(self, test, testIssue, edit):
		response = self.connection.update(test['key'], testIssue)

		if response.status_code != 200 and response.status_code != 201 and response.status_code != 204:
			sublime.error_message("Response: "+str(response.status_code))
			raise Exception("Status was", response.status_code)
			
		self.createLinks(test)

	def createLinks(self, test):
		print("Creating Links", len(test['links']))
		for link in test['links']:
			# Link Test
			# Auf die Blanke URL!!
			# inward key muss der Tests sein.
			link = {
				"type": {
			        "name": link[0] # Tests, cloned by etc Blocks, Relates
			    },
			    "inwardIssue": {
					"key": test['key'] # Ausgehend
				},
			    "outwardIssue": {
			        "key": link[1] # Wird getestet
			    }
			}
			self.connection.createLink("", link)