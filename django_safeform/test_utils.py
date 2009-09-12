import re

input_re = re.compile('<input(.*?)>')
attrib_re = re.compile(r'(\w+)=(["\'])(.*?)(\2)')

def extract_input_tag_attrs(html):
    input_tags = []
    for input in input_re.findall(html):
        pairs = []
        for bits in attrib_re.findall(input):
            pairs.append((bits[0], bits[2]))
        input_tags.append(dict(pairs))
    return input_tags

def extract_input_tags(html):
    tag_attrs = extract_input_tag_attrs(html)
    return dict([
        (d['name'], d.get('value', ''))
        for d in tag_attrs
        if d.has_key('name')
    ])
