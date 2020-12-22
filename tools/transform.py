import simplejson as json
import yaml

ymlData = { 'lowercaseOutputName': True, 'rules' : []}
    
fjson = open('plugin.json', 'r')
jsonData = json.load(fjson)
fjson.close()

metrics = jsonData["metrics"]
for metric in metrics :
    key = metric["timeseries"]["key"]
    domain = metric["source"]["domain"]
    attribute = metric["source"]["attribute"]
    keyProperties = metric["source"]["keyProperties"]
    keyProperties = '{keyProperties}'.format(keyProperties=keyProperties)
    keyProperties = keyProperties.replace('\'', '')
    keyProperties = keyProperties.replace('{', '')
    keyProperties = keyProperties.replace('}', '')
    keyProperties = keyProperties.replace(': ', '=')
    pattern = '{domain}<{keyProperties}><>{attribute}'.format(domain=domain, keyProperties=keyProperties, attribute=attribute)
    #print(key, pattern)
    rule = { 'pattern' : pattern , 'name':key,  'type': 'GAUGE'}
    ymlData['rules'].append(rule)

#print(ymlData)
with open(r'plugin.yaml', 'w') as file:
    documents = yaml.dump(ymlData, file)
    file.close()