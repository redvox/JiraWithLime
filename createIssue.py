import sublime, sublime_plugin
import re
from JiraWithLime.lime_connection import LimeConnection
from JiraWithLime.lime_issue import LimeIssue
from JiraWithLime.my_markdown import MyMarkdownParser
from JiraWithLime.util import Util
from . import markdown2

class PushTest(sublime_plugin.TextCommand):
	def run(self, edit):
		window = self.view.window()
		window.run_command('test_grep', {'callback': 'create_test_issues'})

class PushBug(sublime_plugin.TextCommand):
	def run(self, edit):
		window = self.view.window()
		window.run_command('test_grep', {'callback': 'create_bug_issues'})

class PushStory(sublime_plugin.TextCommand):
	def run(self, edit):
		window = self.view.window()
		window.run_command('test_grep', {'callback': 'create_story_issues'})

class createTestIssuesCommand(sublime_plugin.TextCommand):
	def run(self, edit, testValues):
		print("Beginn creating Test Issues")

		self.window = self.view.window()
		self.connection = LimeConnection()
		self.offset = 0
		self.parser = MyMarkdownParser() 
		for test in testValues:
			newIssue = {
				'fields' : {
					"project" : {
						'key' : test['project']
					},
					"summary" : test['name'],
					"description" : self.parser.build_markdown(test['description']),
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
				newIssue['fields']['customfield_15604'] = []

			if len(test['testgroups']) > 0:
				newIssue['fields']['customfield_15601'] = []

			for attribut in test['attributes']:
				if attribut != '':
					newIssue['fields']['customfield_15604'].append({'value' : attribut})
			for testgroup in test['testgroups']:
				if testgroup != '':
					newIssue['fields']['customfield_15601'].append(testgroup)
			for components in test['components']:
				if components != '':
					newIssue['fields']['components'].append({"name":components})

			if(test['key'] == ''):
				self.createTest(test, newIssue, edit)
			else:
				self.updateTest(test, newIssue, edit)
		sublime.message_dialog("Finish")
	
	def createTest(self, test, newIssue, edit):
		response, data = self.connection.createTestIssue(newIssue)

		if response.status_code != 200 and response.status_code != 201 and response.status_code != 204:
			sublime.error_message("Response: "+str(response.status_code))
			raise Exception("Status was", response.status_code)
				
		test['issue_id'] = data['id']
		test['key'] = data['key']

		###
		if test['keyLineNr'] > 0:
			pt = self.view.text_point(test['keyLineNr']-1+self.offset, 0)
			key_text = " "+test['key']
		else:
			pt = self.view.text_point(test['testLineNr']-1+self.offset, 0)
			key_text = "\n@@ Key: "+test['key']
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
				"key": test['key'] # Ausgehend
			},
		    "outwardIssue": {
		        "key": test['story'] # Wird getestet
		    }
		}
		self.connection.createLink("", link)

	def updateTest(self, test, newIssue, edit):
		response = self.connection.update(test['key'], newIssue)

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
		self.parser = MyMarkdownParser() 
		for test in testValues:
			newIssue = {
				'fields' : {
					"project" : {
						'key' : test['project']
					},
					"summary" : test['name'],
					"description" : self.parser.build_markdown(test['description']),
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
					# "customfield_11018" : {"value" : test['domain']},
					"customfield_11013" : {"value": test['environment']},
					"customfield_16038" : test['browser'],
					"customfield_16039" : test['device'],
					"customfield_16040" : test['operatingsystem']
				}
			}

			for components in test['components']:
				if components != '':
					newIssue['fields']['components'].append({"name":components})

			if(test['key'] == ''):
				self.createBug(test, newIssue, edit)
			else:
				self.updateBug(test, newIssue, edit)
		sublime.message_dialog("Finish")
	
	def createBug(self, test, newIssue, edit):
		response, data = self.connection.createTestIssue(newIssue)

		if response.status_code != 200 and response.status_code != 201 and response.status_code != 204:
			sublime.error_message("Response: "+str(response.status_code))
			raise Exception("Status was", response.status_code)
				
		test['issue_id'] = data['id']
		test['key'] = data['key']

		###
		if test['keyLineNr'] > 0:
			pt = self.view.text_point(test['keyLineNr']-1+self.offset, 0)
			key_text = " "+test['key']
		else:
			pt = self.view.text_point(test['testLineNr']-1+self.offset, 0)
			key_text = "\n@@ Key: "+test['key']
			self.offset = self.offset + 1

		line_region = self.view.line(pt)
		pt += line_region.b - line_region.a
		self.view.insert(edit, pt, key_text)
		###
		self.createLinks(test)

	def updateBug(self, test, newIssue, edit):
		response = self.connection.update(test['key'], newIssue)

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

class CreateStoryIssuesCommand(sublime_plugin.TextCommand):
	def run(self, edit, testValues):
		print("Beginn creating Story Issues")

		self.window = self.view.window()
		self.connection = LimeConnection()
		self.offset = 0
		self.parser = MyMarkdownParser()
		for test in testValues:
			newIssue = {
				'fields' : {
					"project" : {
						'key' : test['project']
					},
					"summary" : test['name'],
					"description" : self.parser.build_markdown(test['description']),
					"issuetype" : {
						"name" : test['type']
					},
					"priority" : {
						"id": "3"
					},
					"customfield_11800" : test['short_description'],
					"components" : [],
					"versions" : [{"name":test['version']}],
					"assignee" : {'name' : test['assignee']}
				}
			}

			if test['type'] == 'Story':
				newIssue['customfield_15502'] = test['short_description']
				newIssue['labels'] = test['labels']

			if test['type'] == 'Subtask':
				if self.prevIssueKey != '':
					newIssue['fields']['parent'] = {"key": self.prevIssueKey }
				else:
					newIssue['fields']['parent'] = {"key": test['parent'] }

			for components in test['components']:
				if components != '':
					newIssue['fields']['components'].append({'name':components})

			if(test['key'] == ''):
				self.createStory(test, newIssue, edit)
			else:
				self.updateStory(test, newIssue, edit)

			if test['type'] == 'Story':
				self.prevIssueKey = test['key']
				if test['epic'] != ['']:
					self.createEpicLinks(test)
		sublime.message_dialog("Finish")
	
	def createStory(self, test, newIssue, edit):
		response, data = self.connection.createTestIssue(newIssue)

		if response.status_code != 200 and response.status_code != 201 and response.status_code != 204:
			sublime.error_message("Response: "+str(response.status_code))
			raise Exception("Status was", response.status_code)
				
		test['issue_id'] = data['id']
		test['key'] = data['key']

		if test['keyLineNr'] > 0:
			pt = self.view.text_point(test['keyLineNr']-1+self.offset, 0)
			key_text = " "+test['key']
		else:
			pt = self.view.text_point(test['testLineNr']-1+self.offset, 0)
			key_text = "\n@@ Key: "+test['key']
			self.offset = self.offset + 1

		line_region = self.view.line(pt)
		pt += line_region.b - line_region.a
		self.view.insert(edit, pt, key_text)

	def updateStory(self, test, newIssue, edit):
		response = self.connection.update(test['key'], newIssue)

		if response.status_code != 200 and response.status_code != 201 and response.status_code != 204:
			sublime.error_message("Response: "+str(response.status_code))
			raise Exception("Status was", response.status_code)

	def createEpicLinks(self, test):
		print("Creating Epic Links", len(test['epic']))
		self.epicMap, self.epicArray = Util.getEpicMap()
		for epic in test['epic']:
			for oEpic in self.epicMap:
				if oEpic['name'] == epic:
					epicKey = oEpic['key']
					break
			link = {
					'ignoreEpics':'true',
					'issueKeys':[
						test['key']
						]
					}
			self.connection.addToEpic(epicKey, link)