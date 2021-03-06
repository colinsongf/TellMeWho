import urllib, json
#import infobox
from collections import OrderedDict
from printable import print_table

api_key = ''
mqlread_url = 'https://www.googleapis.com/freebase/v1/mqlread'

def run(key, question, mode):
	global api_key 
	api_key = key
	x = extractX(question)
	if x == '':
		print 'Illegal Question!'
		return
	type_list = findType(x)
	result = []
	for t in type_list:
		result += MQLquery(x, t, mode)
	result.sort()
	#print result
	#result.insert(0, ('Name', ''))
	if len(result) == 0:
		print 'It seems no one created [' + x + ']'
		return
	if mode == 3:
		print_table(OrderedDict(result))
	else:
		counter = 0
		for item in result:
			counter += 1
			print str(counter) + '. ' + item.encode('ascii', 'ignore')

def extractX(question):
	x = ''
	if question.startswith('Who created ') or question.startswith('who created '):
		tokens = question.split()[2:]
		for t in tokens:
			x += t.strip('?') + ' '
		x = x.strip()
	return x

def findType(x):
	# accepted_type_list = {'/book/book': 'Author', '/organization/organization': 'BusinessPerson'}
	# _, type_list = infobox.topic(infobox.search(x), accepted_type_list)
	# result = []
	# for t in accepted_type_list:
	# 	if t in type_list:
	# 		result.append(accepted_type_list[t])
	# return result
	return ['Author', 'BusinessPerson']

def MQLquery(x, ans_type, mode):
	# build query
	if ans_type == 'Author':
		ans_point = "/book/author"
		query_point = "/book/author/works_written"
	elif ans_type == 'BusinessPerson':
		ans_point = "/organization/organization_founder"
		query_point = "/organization/organization_founder/organizations_founded"
	else:
		return []
	
	# qurey API
	query = [{
		query_point: [{
			"a:name": None,
			"name~=": x
		}],
		"id": None,
		"name": None,
		"type": ans_point
	}]
	params = {
		'query' : query,
		'key': api_key
	}
	url = mqlread_url + '?' + urllib.urlencode(params).replace('None', 'null').replace('%27', '%22')
	response = json.loads(urllib.urlopen(url).read())['result']

	# parse response
	if mode == 3:
		result = []
		for item in response:
			creations = []
			fullname_len = len(item[query_point])
			for i in range(fullname_len):
				creations.append({'As': ans_type, 'Creation': item[query_point][i]['a:name']})
			result.append((item['name'], creations))
	else:
		result = []
		for item in response:
			ans = item['name'] + '(as ' + ans_type + ') created '
			fullname_len = len(item[query_point])
			for i in range(fullname_len):
				if i == 0:
					ans += '<' + item[query_point][i]['a:name'] + '>'
				elif i == fullname_len - 1:
					ans += ' and <' + item[query_point][i]['a:name'] + '>.'
				else:
					ans += ', <' + item[query_point][i]['a:name'] + '>'
			result.append(ans)
	return result

def main():
	run('key', 'Who created Microsoft?')

if __name__ == '__main__': main()