from . import markdown2
import re

class MyMarkdownParser():

	def build_markdown(self, text):
		text = self.build_tables(text)
		return markdown2.markdown(text)

	def build_tables(self, text):

		# Headline				| Headline1 | Headline2   |
		# Markline (Allignment)	| --------- | :---------: |
		# Bode 					| text      |             |

		found_headline = False
		found_allignment = False
		headlines = []
		allignment = []
		text = text.split('\n')
		i = 0
		for line in text:
			isTable = re.search(r'^\|.*', line)
			if isTable:
				#content = re.findall(r'\|\s*([a-zA-Z0-9]*)\s*', l)
				content = line.split('|')
				content = content[1:] # Ignore first
				content = content[:-1] # Ignore last
				if not found_headline:
					found_headline = True
					self.headlines = content
					columns = len(content)
				elif not found_allignment:
					found_allignment = True
					allignment = []
					line = line.replace(" ", "")
					for s in content:
						if s.startswith(':') and s.endswith(':'):
							allignment.append('text-align:center;')
						elif s.startswith(':'):
							allignment.append('text-align:left;')
						elif s.endswith(':'):
							allignment.append('text-align:right;')
						else:
							allignment.append('')
					text[i]=''
					text[i-1] = '<table style="border-collapse:collapse;"><thead><tr>'
					for h in range(len(self.headlines)):
						text[i-1]+='<th style="border: 1px solid #ccc; padding: 6px 13px;%s">%s</th>'%(allignment[h], self.headlines[h]) 
					text[i-1]+= '</tr></thead><tbody>'
				else:
					text[i] = '<tr>'
					for s in range(len(content)):
						text[i]+='<td style="background-color: #fff; border: 1px solid #ccc; padding: 6px 13px;%s">%s</td>'%(allignment[s], content[s])
					text[i]+= '</tr>'
			elif found_headline:
				text[i-1]+='</tbody></table>'
				found_headline = False
				found_allignment = False
				headlines = []
				allignment = []
			i=i+1

		processed_text = ''
		for line in text:
			processed_text+=line+'<br>'
		print('processed_text', processed_text)
		return processed_text