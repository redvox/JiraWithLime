class LimeIssue:
	def __init__(self, jiraDataMap=None):
		self.key_loc = ['key']
		self.summary_loc = ['key', ]
		self.mapping = {
			'id' : ['id'],
			'key' : ['key'],
			'name' : ['fields', 'summary'],
			'type' : ['fields', 'issuetype', 'name'],
			#'description' : ['fields', 'issuetype', 'name'],
			'description' : ['fields', 'customfield_11800'],
			'reporter' : ['fields', 'reporter', 'displayName'],
			'created' : ['fields', 'created'],
			'updated' : ['fields', 'updated'],
			'text' : ['fields', 'description'],
			'project' : ['fields', 'project', 'key'],
			'project_name' : ['fields', 'project', 'name'],
			'projectId' : ['fields', 'project', 'id'],
			'version' : ['fields', 'versions', 'name'],
			'versionId' : ['fields', 'versions', 'id'],
			'assignee' : ['fields', 'assignee', 'name']
		}

		self.ignoreFields = [
			'key', 'name', 'type', 'reporter', 'created', 'updated', 'project',	'project_name', 'sprint'
		]

		if jiraDataMap != None:
			self.mapAttributes(jiraDataMap)
			self.links = jiraDataMap['fields']['issuelinks']

	def mapAttributes(self, jiraDataMap):
		for key in self.mapping: 
			value = self.getValue(jiraDataMap, self.mapping[key])
			self.addattr(key, value)	

	def mapLimeToJira(self, pyDataMap):
		jiraDataMap = {}
		for key in pyDataMap:
			if not key in self.ignoreFields:
				loc_list = self.mapping[key]
				fin = jiraDataMap
				for n in loc_list[:-1]:
					if not n in jiraDataMap:
						fin[n] = {}
					fin = fin[n]
				fin[loc_list[-1]] = pyDataMap[key]
		return jiraDataMap

	def getValue(self, dataMap, key_list):
		value = dataMap
		for key in key_list:
			if type(value) != list:
				try:
					value = value[key]
				except KeyError:
					print("Key Error with", key)
					return "Nicht gefunden"
			else:
				try:
					value = value[0][key]
				except (KeyError, IndexError):
					print("Key Error with", key)
					return "Nicht gefunden"
		if value == None:
			value = "Nicht vorhanden"
		return value

	def addattr(self, x, val):
		self.__dict__[x]=val

	def getattr(self, x):
		try:
			return self.__dict__[x]
		except KeyError:
			return ""

	def getAllTestLinks(self):
		tests = []
		for link in self.links:
			if link['type']['name'] == 'Tests':
				tests.append(link['inwardIssue']['key'])
		return tests


