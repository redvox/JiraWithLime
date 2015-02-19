import sublime, sublime_plugin
import re

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
		self.short_description = ""
		self.epic = ""
		self.domain = ""
		self.environment = ""
		self.browser = ""
		self.operatingsystem = ""
		self.device = ""
		self.links = []
		self.parent = ''

		self.resetFlags()
		for line in lineCollection:
			self.lineNr = self.lineNr+1

			found = re.search(r'^@@ Projekt:(.+)', line)
			if found:
				self.project = self.stripSpaces(found.group(1))
				continue
			
			found = re.search(r'^@@ Attribute:(.*)', line)
			if found:
				self.attributes = self.splitAndStrip(found)
				continue
			
			found = re.search(r'^@@ Testgruppen:(.*)', line)
			if found:
				self.testgroups = self.splitAndStrip(found)
				continue
			
			found = re.search(r'^@@ Komponente:(.*)', line)
			if found:
				self.components = self.splitAndStrip(found)
				continue
			
			found = re.search(r'^@@ Stichwörter:(.*)', line)
			if found:
				self.labels = self.splitAndStrip(found)
				continue

			found = re.search(r'^@@ Bearbeiter:(.*)', line)
			if found:
				print("Bearbeiter", line)
				self.assignee = self.stripSpaces(found.group(1))
				continue
			
			found = re.search(r'^@@ Story:(.+)', line)
			if found:
				self.story = self.stripSpaces(found.group(1))
				continue
			
			found = re.search(r'^@@ Version:(.+)', line)
			if found:
				self.version = self.stripSpaces(found.group(1))
				continue
			
			found = re.search(r'^@ Test:(.*)', line)
			if found:
				print("Found", "Test", "in Line", self.lineNr, line)
				self.newIssue()
				self.addValue('name', found.group(1))
				self.testValues[self.testNr]['links'].append(['tests', self.story])
				self.testValues[self.testNr]['type'] = "Test"
				self.resetFlags()
				continue			

			found = re.search(r'^@ Bug:(.*)', line)
			if found:
				print("Found", "Bug", "in Line", self.lineNr, line)
				self.newIssue()
				self.addValue('name', found.group(1))
				self.testValues[self.testNr]['type'] = "Bug"
				self.resetFlags()
				continue

			found = re.search(r'^@ Story:(.*)', line)
			if found:
				print("Found", "Story", "in Line", self.lineNr, line)
				self.newIssue()
				self.addValue('name', found.group(1))
				self.testValues[self.testNr]['type'] = "Story"
				self.resetFlags()
				continue

			found = re.search(r'^@ Subtask:(.*)', line)
			if found:
				print("Found", "Aufgabe", "in Line", self.lineNr, line)
				self.newIssue()
				self.addValue('name', found.group(1))
				self.testValues[self.testNr]['type'] = "Subtask"
				self.testValues[self.testNr]['epic'] = ""
				self.resetFlags()
				continue

			found = re.search(r'^@@ Epic:(.*)', line)
			if found:
				self.epic = self.splitAndStrip(found)
				continue

			found = re.search(r'^@@ Domäne:(.*)', line)
			if found:
				self.domain = self.stripSpaces(found.group(1))
				self.resetFlags()
				continue

			found = re.search(r'^@@ Umgebung:(.*)', line)
			if found:
				self.environment = self.stripSpaces(found.group(1))
				self.resetFlags()
				continue

			found = re.search(r'^@@ Browser:(.*)', line)
			if found:
				self.browser = self.splitAndStrip(found)
				self.resetFlags()
				continue		

			found = re.search(r'^@@ Device:(.*)', line)
			if found:
				self.device = self.splitAndStrip(found)
				self.resetFlags()
				continue	

			found = re.search(r'^@@ Betriebssystem:(.*)', line)
			if found:
				self.operatingsystem = self.splitAndStrip(found)
				self.resetFlags()
				continue				

			found = re.search(r'^@@ Key:(.*)', line)  
			if found:
				self.testValues[self.testNr]['key'] = self.stripSpaces(found.group(1))
				self.testValues[self.testNr]['keyLineNr'] = self.lineNr
				self.resetFlags()
				continue

			found = re.search(r'^@@ Blocks:(.*)', line)  
			if found:
				#self.links.append(['Blocks', self.stripSpaces(found.group(1))])
				self.testValues[self.testNr]['links'].append(['Blocks', self.stripSpaces(found.group(1))])
				self.resetFlags()
				continue			

			found = re.search(r'^@@ Relates:(.*)', line)  
			if found:
				#self.links.append(['Relates', self.stripSpaces(found.group(1))])
				self.testValues[self.testNr]['links'].append(['Relates', self.stripSpaces(found.group(1))])
				self.resetFlags()
				continue

			found = re.search(r'^@@ Subtask-Parent:(.*)', line)  
			if found:
				self.parent = self.stripSpaces(found.group(1))
				self.resetFlags()
				continue

			found = re.search(r'^@@ Beschreibung:*(.*)', line) #  
			if found:
				print("Found", "Beschreibung", "in Line", self.lineNr)
				self.description = found.group(1)
				self.testValues[self.testNr]['description'] = ""
				self.addValue('description', found.group(1))
				self.resetFlags()
				self.description_flag = True
				continue

			found = re.search(r'^@@ Kurzbeschreibung:*(.*)', line) #  
			if found:
				print("Found", "Kurzbeschreibung", "in Line", self.lineNr)
				self.short_description = found.group(1)
				self.testValues[self.testNr]['short_description'] = ""
				self.addValue('short_description', found.group(1))
				self.resetFlags()
				self.short_description_flag = True
				continue

			found = re.search(r'^----\s*$', line)
			if found:
				self.newStep()
				self.resetFlags()
				self.test_steps_flag = True
				self.step_flag = True
				continue

			found = re.search(r'^@@\s*$',line)
			if found and self.test_steps_flag:
				self.resetFlags()
				self.data_flag = True
				continue

			found = re.search(r'^->\s*$', line)
			if found and self.test_steps_flag:
				self.resetFlags()
				self.result_flag = True
				continue

			if self.description_flag:
				self.addValue('description', line)
				self.description += '  \n'
				self.description += line
				continue
				
			if self.short_description_flag:
				self.addValue('short_description', line)
				self.short_description += '  \n'
				self.short_description += line
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

	def newIssue(self):
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
				'short_description' : self.short_description,
				'steps' : [],
				'result' : [],
				'data' : [],
				'testLineNr' : self.lineNr,
				'keyLineNr' : -1,
				'key' : '',
				'type' : '',
				'domain' : self.domain,
				'epic' : self.epic,
				'environment' : self.environment,
				'browser' : self.browser,
				'operatingsystem' : self.operatingsystem,
				'device' : self.device,
				'links' : [],
				'parent' : self.parent
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
		self.short_description_flag = False
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