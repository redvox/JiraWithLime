import sublime, sublime_plugin
import re
from JiraWithLime.lime_connection import LimeConnection
from JiraWithLime.lime_issue import LimeIssue
from . import markdown
from . import markdown2

class GetJiraHeadlineCommand(sublime_plugin.TextCommand):
	def run(self, edit, issue_key=None):
		window = self.view.window()
		if not issue_key:
			window.run_command('prompt_issue_key',
								{'callback': 'get_jira_headline'})
		else:
			connection = LimeConnection()
			issue = connection.get(issue_key)
			region = self.view.sel()
			line = self.view.line(region[0])
			self.view.insert(edit, line.end(), "\n@ "+issue.key+" - "+issue.name+"\n"+issue.description)

class PromptIssueKeyCommand(sublime_plugin.TextCommand):
	def run(self, edit, callback):
		window = self.view.window()
		settings = sublime.load_settings('JiraWithLime.sublime-settings')
		issue_key_hint = settings.get('project', "") + "-"
		call = lambda v: window.run_command(callback, {'issue_key': v})
		window.show_input_panel('Issue key', issue_key_hint, call, None, None)

class OpenIssueCommand(sublime_plugin.TextCommand):
	def run(self, edit, issue_key=None):
		window = self.view.window()
		if not issue_key:
			window.run_command('prompt_issue_key',
								{'callback': 'open_issue'})
		else:
			connection = LimeConnection()

			issue = connection.get(issue_key)

			TEMPLATE = (
					"{key} - {name}\n"
					"@@ Projekt: {project}\n"
					"@@ Projekt Name: {project_name}\n"
					"@@ Reporter: {reporter}\n"
					"@@ Bearbeiter: {assignee}\n"
					# "@@ Updated: {updated}\n"
					"Sprint: {version}\n"
					"\n"
					"@@ Description:\n"
					"{description}\n"
					"\n"
					"@@ Text:\n"
					"{text}\n"
					)

			keywords = re.findall(r'\{([a-z_]+)\}', TEMPLATE)
			valuesMap = {}
			for key in keywords:
				valuesMap[key] = issue.getattr(key)
			print("keywords", keywords)

			text = TEMPLATE.format(**valuesMap)
	
			# text = "this is a Test %(tx)s!" %{'tx': ' mit erfolg'}
			# sublime.active_window().open_file("test")
			window.new_file()
			view = window.active_view()
			view.insert(edit, 0, text)


class GetTestCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		connection = LimeConnection()

		issue = connection.get("LHO3-1710")

		region = self.view.sel()
		line = self.view.line(region[0])
		self.view.insert(edit, line.end(), "\n# "+issue.key+" - "+issue.name+"\n"+issue.description)	

# class InsertTestCommand(sublime_plugin.TextCommand):
# 	def run(self, edit):
# 	 	window = self.view.window()

# 		TEMPLATE = (
# 			"Key: {key}\n"
# 		  )

# 		text = TEMPLATE.format(**{'key':'dies ist ein test'})

# 		window.new_file()
# 		view = window.active_view()
# 		view.run_command('replace_all', {'text': text})

class ReplaceAllCommand(sublime_plugin.TextCommand):
	def run(self, edit, text):
		self.view.run_command('select_all')
		self.view.replace(edit, self.view.sel()[0], text)
		self.view.sel().clear()

class UpdateIssueCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		window = self.view.window()

		TEMPLATE = (
				"{key} - {name}\n"
				"@@ Projekt: {project}\n"
				"@@ Projekt Name: {project_name}\n"
				"@@ Reporter: {reporter}\n"
				"@@ Bearbeiter: {assignee}\n"
				# "@@ Updated: {updated}\n"
				# "Sprint: {sprint}\n"
				"\n"
				"@@ Description:\n"
				"{description}\n"
				"\n"
				"@@ Text:\n"
				"{text}\n"
				)

		self.view.run_command('select_all')
		text = self.view.substr(self.view.sel()[0])
		self.view.sel().clear()

		templateRegEx = re.sub(r'\{', "(?P<", TEMPLATE)
		templateRegEx = re.sub(r'\}', ">(.|\n)*)", templateRegEx)
		templateRegEx = re.compile(templateRegEx)
		inputValues = re.match(templateRegEx, text).groupdict()
		connection = LimeConnection()

		r = connection.update(inputValues['key'], LimeIssue().mapLimeToJira(inputValues))

class NewTestsCommand(sublime_plugin.TextCommand):
	def run(self, edit, issue_key=None):
		window = self.view.window()
		if not issue_key:
			window.run_command('prompt_issue_key',
								{'callback': 'new_tests'})
		else:
			connection = LimeConnection()

			issue = connection.get(issue_key)

			TEST_HEAD_TEMPLATE = (
					"{key} - {name}\n"
					"{description}\n"
					"\n"
					"@@ Projekt: {project}\n"
					"@@ Story: {key}\n"
					"@@ Story Reporter: {reporter}\n"
					"\n"
					"@@ Version: {version}\n"
					"@@ Attribute: {attribute}\n"
					"@@ Testgruppen: {testgruppen}\n"
					'@@ Komponenten: {components}\n'
					'@@ Stichwörter: {lables}\n'
					'@@ Bearbeiter: {assignee}\n'
					"\n"
					)

			keywords = re.findall(r'\{([a-z_]+)\}', TEST_HEAD_TEMPLATE)
			valuesMap = {}
			for key in keywords:
				valuesMap[key] = issue.getattr(key)
			valuesMap['attribute'] = "Regressionstest, Live-Test, Automatisiert"
			valuesMap['key'] = issue_key
			settings = sublime.load_settings('JiraWithLime.sublime-settings')
			valuesMap['assignee'] = settings.get('assignee', "")
			valuesMap['components'] = settings.get('component', "")
			
			text = TEST_HEAD_TEMPLATE.format(**valuesMap)

			window.new_file()
			view = window.active_view()
			view.insert(edit, 0, text)
			window.run_command('add_test_template')
			window.run_command('add_test_template')
			window.run_command('add_test_template')

class AddTestTemplateCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		window = self.view.window()
		TEST_STEP_TEMPLATE = (
				"\n@ Test:\n"
				#"@@ Key:\n"
				"@@ Beschreibung\n"
				"{beschreibung_template}"
				"\n"
				"----\n"
				"\n"
				"->\n"
				"\n"
				"----\n"
				"\n"
				"->\n"
				"\n"
				"----\n"
				)

		settings = sublime.load_settings('JiraWithLime.sublime-settings')
		valuesMap = {}
		valuesMap['beschreibung_template'] = settings.get('beschreibung_template', "")
		text = TEST_STEP_TEMPLATE.format(**valuesMap)
		self.view.insert(edit, self.view.size(), text)

class PushTest(sublime_plugin.TextCommand):
	def run(self, edit):
		window = self.view.window()
		window.run_command('test_grep', {'callback': 'create_test_issues'})

class TestGrepCommand(sublime_plugin.TextCommand):
	def run(self, edit, callback):
		window = self.view.window()

		self.view.run_command('select_all')
		text = self.view.substr(self.view.sel()[0])
		self.view.sel().clear()
		lineCollection = list(iter(text.splitlines()))

		self.testValues = []
		self.testNr = -1
		self.stepNr = -1
		self.lineNr = 0

		self.project = ""
		self.assignee = ""
		self.attributes = []
		self.testgroups = []
		self.components = []
		self.labels = []
		self.story = ""
		self.version = ""
		self.description = ""

		self.resetFlags()
		for line in lineCollection:
			self.lineNr = self.lineNr+1

			found = re.search(r'@@ Projekt:(.+)', line)
			if found:
				self.project = self.stripSpaces(found.group(1))
				continue
			
			found = re.search(r'@@ Attribute:(.*)', line)
			if found:
				self.attributes = self.splitAndStrip(found)
				continue
			
			found = re.search(r'@@ Testgruppen:(.*)', line)
			if found:
				self.testgroups = self.splitAndStrip(found)
				continue
			
			found = re.search(r'@@ Komponenten:(.*)', line)
			if found:
				self.components = self.splitAndStrip(found)
				continue
			
			found = re.search(r'@@ Stichwörter:(.*)', line)
			if found:
				self.labels = self.splitAndStrip(found)
				continue

			found = re.search(r'@@ Bearbeiter:(.*)', line)
			if found:
				print("Bearbeiter", line)
				self.assignee = self.stripSpaces(found.group(1))
				continue
			
			found = re.search(r'@@ Story:(.+)', line)
			if found:
				self.story = self.stripSpaces(found.group(1))
				continue
			
			found = re.search(r'@@ Version:(.+)', line)
			if found:
				self.version = self.stripSpaces(found.group(1))
				continue
			
			found = re.search(r'@ Test:(.*)', line)
			if found:
				print("Found", "Test", "in Line", self.lineNr, line)
				self.newTest()
				self.addValue('name', found.group(1))
				self.resetFlags()
				continue

			found = re.search(r'@@ Key:(.*)', line)  
			if found:
				self.testValues[self.testNr]['key'] = self.stripSpaces(found.group(1))
				self.testValues[self.testNr]['keyLine'] = self.lineNr
				self.resetFlags()
				continue

			found = re.search(r'@@ Beschreibung:*(.*)', line) #  
			if found:
				print("Found", "Beschreibung", "in Line", self.lineNr)
				self.description = found.group(1)
				self.testValues[self.testNr]['description'] = ""
				self.addValue('description', found.group(1))
				self.resetFlags()
				self.description_flag = True
				continue

			found = re.search(r'----', line)
			if found:
				self.newStep()
				self.resetFlags()
				self.step_flag = True
				continue

			found = re.search(r'(.*)->(.*)', line)
			if found:
				self.addValue('steps', found.group(1))
				self.addValue('result', found.group(2))
				self.resetFlags()
				self.result_flag = True
				continue

			# if self.test_flag:
			# 	self.addValue('name', line)
			# 	continue
			if self.description_flag:
				self.addValue('description', line)
				self.description += '  \n'
				self.description += line
				continue
			if self.step_flag:
				self.addValue('steps', line)
				continue
			if self.result_flag:
				self.addValue('result', line)
				continue
			if self.data_flag:
				self.addValue('data', line)
				continue

		window.run_command(callback, {'testValues': self.testValues})

	def newTest(self):
		self.testNr = self.testNr+1
		self.stepNr = -1
		self.testValues.append({
				'project' : self.project,
				'assignee' : self.assignee,
				'attributes' : self.attributes,
				'testgroups' : self.testgroups,
				'components' : self.components,
				'labels' : self.labels,
				'story' : self.story,
				'version' : self.version,
				'name' : "",
				'description' : self.description,
				'steps' : [],
				'result' : [],
				'data' : [],
				'lineNr' : self.lineNr,
				'keyLine' : -1,
				'key' : ""
				})

	def newStep(self):
		print("Add New Test Step")
		self.stepNr = self.stepNr+1
		self.testValues[self.testNr]['steps'].append("")
		self.testValues[self.testNr]['result'].append("")
		self.testValues[self.testNr]['data'].append("")

	def addValue(self, vtype, value):
		value = self.stripSpaces(value)
		if type(self.testValues[self.testNr][vtype]) == list:
			if self.testValues[self.testNr][vtype][self.stepNr] != '':
				self.testValues[self.testNr][vtype][self.stepNr] += '  \n'
			self.testValues[self.testNr][vtype][self.stepNr] += value
		else:
			if self.testValues[self.testNr][vtype] != '':
				self.testValues[self.testNr][vtype] += '  \n'
			self.testValues[self.testNr][vtype] += value

	def resetFlags(self):
		self.test_flag = False
		self.key_flag = False
		self.description_flag = False
		self.step_flag = False
		self.result_flag = False
		self.data_flag = False

	def stripSpaces(self, value):
		print("strip", value)
		while len(value) > 0 and (value[0] == ' ' or value[0] == '\t' or value[0] == '\n'):
			value = value[1:]
		while len(value) > 0 and (value[-1] == ' ' or value[-1] == '\t' or value[-1] == '\n'):
			value = value[:-1]
		return value

	def splitAndStrip(self, matchObj):
		vals = matchObj.group(1).split(',')
		for i in range(len(vals)):
			vals[i] = self.stripSpaces(vals[i])
		return vals
		
class CreateTestIssuesCommand(sublime_plugin.TextCommand):
	def run(self, edit, testValues):
		print("Beginn creating Test Issues")

		self.window = self.view.window()
		self.connection = LimeConnection()

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
					"customfield_15604" : [], #Attribute {"value":"Regressionstest"}
					"customfield_15601" : [], #Testgruppen "Integration-Test", "Test Test"
					"customfield_15603" : [test['story']], #Story
					"components" : [],
					"versions" : [{"name":test['version']}],
					"labels" : test['labels'],
					"assignee" : {'name' : test['assignee']}
				}
			}

			for attribut in test['attributes']:
				testIssue['fields']['customfield_15604'].append({'value' : attribut})
			for testgroup in test['testgroups']:
				testIssue['fields']['customfield_15601'].append(testgroup)
			for components in test['components']:
				testIssue['fields']['components'].append({"name":components})

			print("key",test['key'],"key")

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
				
		issue_id = data['id']
		issue_key = data['key']
		test['issue_id'] = issue_id
		test['issue_key'] = issue_key

		###
		if test['keyLine'] > 0:
			pt = self.view.text_point(test['keyLine']-1, 0)
			key_text = " "+test['issue_key']
		else:
			pt = self.view.text_point(test['lineNr']-1, 0)
			key_text = "\n@@ Key: "+test['issue_key']

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
				self.connection.createTestStep(issue_id, teststep) #ID!  230076

		# Link Test
		# Auf die Blanke URL!!
		# inward key muss der Tests sein.
		link = {
			"type": {
		        "name": "Tests" # Tests, cloned by etc
		    },
		    "inwardIssue": {
				"key": issue_key # Ausgehend
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
		print('overSize', overSize)
		if overSize > 0:
			for i in data[len(data)-overSize:]:
				print('i', i)
				testStepId = i['id']
				self.connection.deleteTestStep(issue.id, testStepId)

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
