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
			text = TEMPLATE.format(**valuesMap)
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
					"@@ Testgruppen: {testgroup}\n"
					'@@ Komponente: {component}\n'
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
			valuesMap['component'] = settings.get('component', "")
			valuesMap['testgroup'] = settings.get('testgroup', "")
			
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

class NewBugCommand(sublime_plugin.TextCommand):
	def run(self, edit, issue_key=None):
		window = self.view.window()
		BUG_HEAD_TEMPLATE = (
				'\n'
				'@@ Projekt: {project}\n'
				#'@@ Stichwörter: {lables}\n'
				'@@ Domäne: {domain}\n'
				'@@ Umgebung: {environment}\n'
				'@@ Browser: {browser}\n'
				'@@ Komponente: {component}\n'
				'@@ Bearbeiter: {assignee}\n'
				'\n'
				'@@ Version: {version}\n'
				'\n'
				'\n'
				"@ Bug:\n"
				'@@ Releats:\n'
				'@@ Blocks:\n'
				"@@ Beschreibung\n"
				#"{beschreibung_template}"
				)

		keywords = re.findall(r'\{([a-z_]+)\}', BUG_HEAD_TEMPLATE)
		valuesMap = {}
		for key in keywords:
			valuesMap[key] = ""
		valuesMap['key'] = issue_key
		settings = sublime.load_settings('JiraWithLime.sublime-settings')
		valuesMap['project'] = settings.get('project', "")
		valuesMap['component'] = settings.get('component', "")
		valuesMap['browser'] = settings.get('browser', "")
		valuesMap['environment'] = settings.get('environment', "")
		valuesMap['domain'] = settings.get('domain', "")
		valuesMap['assignee'] = settings.get('assignee', "")
		
		text = BUG_HEAD_TEMPLATE.format(**valuesMap)

		window.new_file()
		view = window.active_view()
		view.insert(edit, 0, text)

class PushTest(sublime_plugin.TextCommand):
	def run(self, edit):
		window = self.view.window()
		window.run_command('test_grep', {'callback': 'create_test_issues'})

class PushBug(sublime_plugin.TextCommand):
	def run(self, edit):
		window = self.view.window()
		window.run_command('test_grep', {'callback': 'create_bug_issues'})

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
		self.domain = ""
		self.environment = ""
		self.browser = ""
		self.links = []

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
			
			found = re.search(r'@@ Komponente:(.*)', line)
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
				self.testValues[self.testNr]['links'].append(['tests', self.story])
				self.testValues[self.testNr]['type'] = "Test"
				self.resetFlags()
				continue			

			found = re.search(r'@ Bug:(.*)', line)
			if found:
				print("Found", "Bug", "in Line", self.lineNr, line)
				self.newTest()
				self.addValue('name', found.group(1))
				self.testValues[self.testNr]['type'] = "Bug"
				self.resetFlags()
				continue

			found = re.search(r'@@ Domäne:(.*)', line)
			if found:
				self.domain = self.stripSpaces(found.group(1))
				self.resetFlags()
				continue

			found = re.search(r'@@ Umgebung:(.*)', line)
			if found:
				self.environment = self.stripSpaces(found.group(1))
				self.resetFlags()
				continue

			found = re.search(r'@@ Browser:(.*)', line)
			if found:
				self.browser = self.stripSpaces(found.group(1))
				self.resetFlags()
				continue				

			found = re.search(r'@@ Key:(.*)', line)  
			if found:
				self.testValues[self.testNr]['key'] = self.stripSpaces(found.group(1))
				self.testValues[self.testNr]['keyLineNr'] = self.lineNr
				self.resetFlags()
				continue

			found = re.search(r'@@ Blocks:(.*)', line)  
			if found:
				#self.links.append(['Blocks', self.stripSpaces(found.group(1))])
				self.testValues[self.testNr]['links'].append(['Blocks', self.stripSpaces(found.group(1))])
				self.resetFlags()
				continue			

			found = re.search(r'@@ Relates:(.*)', line)  
			if found:
				#self.links.append(['Relates', self.stripSpaces(found.group(1))])
				self.testValues[self.testNr]['links'].append(['Relates', self.stripSpaces(found.group(1))])
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

			found = re.search(r'^----$', line)
			if found:
				self.newStep()
				self.resetFlags()
				self.step_flag = True
				continue

			found = re.search(r'(.*)->(.*)', line)
			if found and self.step_flag:
				self.addValue('steps', found.group(1))
				self.addValue('result', found.group(2))
				self.resetFlags()
				self.result_flag = True
				continue

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
				'testLineNr' : self.lineNr,
				'keyLineNr' : -1,
				'key' : '',
				'type' : '',
				'domain' : self.domain,
				'environment' : self.environment,
				'browser' : self.browser,
				'links' : []
				})

	def newStep(self):
		print("Add New Test Step")
		self.stepNr = self.stepNr+1
		self.testValues[self.testNr]['steps'].append("")
		self.testValues[self.testNr]['result'].append("")
		self.testValues[self.testNr]['data'].append("")

	def addValue(self, vtype, value):
		print("Add Value", "vtype", vtype, "value", value)
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
