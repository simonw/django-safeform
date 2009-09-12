"""
Simple functions for extracting input tags from HTML - when you're testing 
CSRF protection you need to be able to pull out the
    <input type="hidden" name="_csrf_token" value="...">
tags so you can POST a correct value.
"""
import re

input_re = re.compile('<input(.*?)>')
attrib_re = re.compile(r'(\w+)=(["\'])(.*?)(\2)')

def extract_input_tag_attrs(html):
    "Returns a list of HTML attribute dictionaries for all inputs found"
    input_tags = []
    for input in input_re.findall(html):
        pairs = []
        for bits in attrib_re.findall(input):
            pairs.append((bits[0], bits[2]))
        input_tags.append(dict(pairs))
    return input_tags

def extract_input_tags(html):
    "Returns a dictionary of name => value for all inputs found"
    tag_attrs = extract_input_tag_attrs(html)
    return dict([
        (d['name'], d.get('value', ''))
        for d in tag_attrs
        if d.has_key('name')
    ])
