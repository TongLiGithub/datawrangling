# -*- coding: utf-8 -*-
"""
Created on Sun Apr 09 23:39:36 2017

@author: Tong LI
"""

# Data wrangling street map

# Use the following code to take a systematic sample of elements from your original OSM region. Try changing the value of k so that your resulting SAMPLE_FILE ends up at different sizes. When starting out, try using a larger k, then move on to an intermediate k before processing your whole dataset.
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET  # Use cElementTree or lxml if too slow

OSM_FILE = "HartfordCountry.osm"  # Replace this with your osm file
SAMPLE_FILE = "sample.osm"

k = 100 # Parameter: take every k-th top level element

def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag

    Reference:
    http://stackoverflow.com/questions/3095434/inserting-newlines-in-xml-file-generated-via-xml-etree-elementtree-in-python
    """
    context = iter(ET.iterparse(osm_file, events=('start', 'end')))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


with open(SAMPLE_FILE, 'wb') as output:
    output.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    output.write('<osm>\n  ')

    # Write every kth top level element
    for i, element in enumerate(get_element(OSM_FILE)):
        if i % k == 0:
            output.write(ET.tostring(element, encoding='utf-8'))

    output.write('</osm>')





## to use the iterative parsing to process the map file and find out not only what tags are there, but also how many, to get the feeling on how much of which data you can expect to have in the map. Fill out the count_tags function. It should return a dictionary with the tag name as the key and number of times this tag can be encountered in the map as value.


import xml.etree.cElementTree as ET
import pprint

def count_tags(filename):
    
    tags = {}
    for event, elem in ET.iterparse(filename):
        if elem.tag not in tags:
            tags[elem.tag] = 1
        else:
            tags[elem.tag] += 1
    return tags        

tags = count_tags('sample.osm')
pprint.pprint(tags)


## tag types
""" Before you process the data and add it into your database, you should check the "k" value for each "<tag>" and see if there are any potential problems.
## We have provided you with 3 regular expressions to check for certain patterns in the tags. As we saw in the quiz earlier, we would like to change the data model and expand the "addr:street" type of keys to a dictionary like this:
## {"address": {"street": "Some value"}}
## So, we have to see if we have such tags, and if we have any tags with problematic characters.

## Please complete the function 'key_type', such that we have a count of each of four tag categories in a dictionary:
  "lower", for tags that contain only lowercase letters and are valid,
  "lower_colon", for otherwise valid tags with a colon in their names,
  "problemchars", for tags with problematic characters, and
  "other", for other tags that do not fall into the other three categories.
See the 'process_map' and 'test' functions for examples of the expected format.
"""

import re 
lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')


#re.match(pattern, string, flags=0): If zero or more characters at the beginning of string match the regular expression pattern, 
                                     #return a corresponding MatchObject instance. Return None if the string does not match the pattern; 
                                     #note that this is different from a zero-length match.
def key_type(element, keys):
    if element.tag == "tag":
        # YOUR CODE HERE
        attribute = element.attrib['k']
        if(re.match(lower, attribute) != None):
            keys['lower'] += 1
        elif(re.match(lower_colon, attribute) != None):
            keys['lower_colon'] += 1
        elif(re.match(problemchars, attribute) != None):
            keys['problemchars'] += 1
        else:
            keys['other'] +=  1
    
    return keys
        
    


def process_map(filename):
    keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0}
    for _, element in ET.iterparse(filename):
        keys = key_type(element, keys)

    return keys



keys = process_map('sample.osm')
pprint.pprint(keys)




## Auditing street names
import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

OSMFILE = "sample.osm"
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
street_types = defaultdict(set)


expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Square", "Lane", "Road", "Trail", "Parkway", "Commons", "Expressway", "Highway", "Passway", "Turnpike"]
#expected = [] 

def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)


def print_sorted_dict(d):
    keys = d.keys()
    keys = sorted(keys, key=lambda s: s.lower())
    for k in keys:
        v=d[k]
        print "%s: %d" % (k,v)
        
def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street"), (elem.attrib['k'] == "tiger:name_type")


def audit():
    osm_file = open(OSMFILE, "r")
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
    pprint.pprint(dict(street_types))


audit()



## problem for the street names: Expy & Expressway, Highway $ Hwy, Ln, Passway, Rd, St, Tpke $ Turnpike, Pl



# improving street names
mapping = { "St": "Street",
            "St": "Street",
            "Ave": "Avenue",
            "Rd": "Road",
            "Expy": "Expressway",
            "Hwy": "Highway",
            "Ln": "Lane",
            "Pl": "Place",
            "Tpke": "Turnpike"
            }

def audit2(osmfile):
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
    osm_file.close()
    return street_types

def update_name(name, mapping):

    sorted_keys = sorted(mapping.keys(), key=len, reverse=True) 
   
    for abbrv in sorted_keys:
        if(abbrv in name):
            #print(abbrv)
            return name.replace(abbrv, mapping[abbrv])

    return name

st_types = audit2(OSMFILE)

for st_type, ways in st_types.iteritems():
    for name in ways:
        better_name = update_name(name, mapping)
        print name, "=>", better_name


# investigate zipcode
#zipcode_type_re = re.compile(r'^06\d{3}', re.IGNORECASE) #format: 06xxx
zipcode_types = set()
expectedzip = []

def auditzip():
    osm_file = open(OSMFILE, "r")
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if (tag.attrib['k'] == "tiger:zip_right"):
                    zipcode_types.add(tag.attrib['v'])
                elif (tag.attrib['k'] == "tiger:zip_left"):
                    zipcode_types.add(tag.attrib['v'])
                elif (tag.attrib['k'] == "addr:postcode"):
                    zipcode_types.add(tag.attrib['v'])
    pprint.pprint(zipcode_types)


auditzip() #print all zipcodes, all look fine (5 digits, starts with 06)


'''
## test whether zip_left = zip_right
OSMFILE = "sample.osm"
zipcodetest = set()

def auditzip2():
    osm_file = open(OSMFILE, "r")
    rightzip = str()
    leftzip = str()
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "way":
            for tag in elem.iter("tag"):
                if tag.attrib['k'] == "tiger:zip_right":
                    rightzip = tag.attrib['v']
                if tag.attrib['k'] == "tiger:zip_left":
                    leftzip = tag.attrib['v']
                if rightzip != leftzip:
                    
                #if (rightzip != leftzip):
                #    zipcodetest.add((rightzip, leftzip))
    #pprint.pprint(zipcodetest)

auditzip2()
'''

# investigate city

city_types = set()
expectedcity = []

def auditcity():
    osm_file = open(OSMFILE, "r")
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if (tag.attrib['k'] == "tiger:county"):
                    city_types.add(tag.attrib['v'])
                
    pprint.pprint(city_types)


auditcity() # "New Haven, CT", "Hartford, CT:New Haven, CT", "Litchfield, CT:New Haven, CT"

## improve city names
mappingcity = { "Hartford, CT:New Haven, CT": "New Haven, CT",
               "Litchfield, CT:New Haven, CT": "New Haven, CT",
               "Hartford, CT:Litchfield, CT": "Litchfield, CT",
               "Hartford, CT; Tolland, CT:Tolland, CT": "Tolland, CT",
               "Hartford, CT; Tolland, CT": "Tolland, CT",
               "New London, CT:Tolland, CT": "Tolland, CT",
               "Hartford, CT:Middlesex, CT": "Middlesex, CT",
               "Middlesex, CT:New Haven, CT": "New Haven, CT",
               "Middlesex, CT:New London, CT": "New London, CT",
               "; Hartford, CT": "Hartford, CT",
               "Hartford, CT:New London, CT": "New London, CT"
               }

def auditcity2(osmfile):
    osm_file = open(osmfile, "r")
    city_types = set()
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if (tag.attrib['k'] == "tiger:county"):
                    city_types.add(tag.attrib['v'])
    osm_file.close()
    return city_types


def update(name, mapping): 
    words = name.split()
    for w in range(len(words)):
        if words[w] in mapping:
            words[w] = mapping[words[w]] 
            name = " ".join(words)
    return name

'''
def update_name(name, mappingcity):

    sorted_keys = sorted(mappingcity.keys(), key=len, reverse=True) 
   
    for abbrv in sorted_keys:
        if(abbrv in name):
            #print(abbrv)
            return name.replace(abbrv, mappingcity[abbrv])

    return name
'''
ct_types = auditcity2(OSMFILE)

for name in ct_types:
    better_name = update_name(name, mappingcity)
    print name, "=>", better_name

print ct_types

tagtype = set()

osm_file = open(OSMFILE, "r")
for event, elem in ET.iterparse(osm_file, events=("start",)):
    if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if (tag.attrib['k'] == "tiger:county"):  
                    value = tag.attrib['v']
                    for name in mappingcity.keys():
                        if value == name:
                            tag.attrib['v'] = mappingcity[name]
                            tagtype.add(tag.attrib['v'])
                    
                            
    
mappingcity["; Hartford, CT"]

mappingcity.keys()

# investigate phone

phone_types = set()
expectedphone = []

def auditphone():
    osm_file = open(OSMFILE, "r")
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if (tag.attrib['k'] == "phone"):
                    phone_types.add(tag.attrib['v'])
                                
    pprint.pprint(phone_types)


auditphone() #format needs to be unified


# improving phone numbers
mappingphone = {'+1 203 5740096': '203-574-0096',
                '+1 860 223 2885': '860-223-2885',
                '8602161255': '860-216-1255'                
                }

def auditphone2(osmfile):
    osm_file = open(osmfile, "r")
    phone_types = set()
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if (tag.attrib['k'] == "phone"):
                    phone_types.add(tag.attrib['v'])
    osm_file.close()
    return phone_types

def update_phone(name, mappingphone):

    sorted_keys = sorted(mappingphone.keys(), key=len, reverse=True) 
   
    for abbrv in sorted_keys:
        if(abbrv in name):
            #print(abbrv)
            return name.replace(abbrv, mappingphone[abbrv])

    return name

ph_types = auditphone2(OSMFILE)

for name in ph_types:
    better_name = update_name(name, mappingphone)
    print name, "=>", better_name















