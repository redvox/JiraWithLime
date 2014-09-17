from . import requests
import zipfile
import re

class Update():

	def checkForUpdate(self):
		print("Test for Update")
		f = open('version.txt', 'r')
		current_Version = f.read()

		response = requests.get('https://raw.githubusercontent.com/redvox/JiraWithLime/master/version.txt', stream=True)
		online_version = response.text

		print("current_Version", current_Version)
		print("online_version", online_version)

		if current_Version != online_version:
			print("Up-Date available. Start update.")
			self.update()
		else:
			print("Your version is Up-To-Date")

	def update(self):
		response = requests.get('https://github.com/redvox/JiraWithLime/archive/1.0.zip', stream=True)
		if response.status_code == 200:
			with open("update.zip", 'wb') as f:
				for chunk in response.iter_content():
					f.write(chunk)

		fh = open('update.zip', 'rb')
		z = zipfile.ZipFile(fh)
		print("z.namelist()", z.namelist())
		for name in z.namelist():
			local_name = name[17:]
			found = re.search(r'.*/$', name)
			print(found)
			if name != 'JiraWithLime.sublime-settings' and local_name != '' and not found:
				print('name', name)
				print('local_name', local_name)
		
				data = z.read(name)
		
				myfile = open(local_name, "wb")
				myfile.write(data)
				myfile.close()
				# z.extract('JiraWithLime1-0/version.txt', '')
		fh.close()

up = Update()
up.checkForUpdate()