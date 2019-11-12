#!/usr/bin/python

import json
import re

import html2text
import mistune

with open("README.md") as r:
    lines = r.readlines()

head_rgx = re.compile('(#+) ([^#]*)')
def sectioned_lines():
    sections = list()

    for line in lines:
        line = line.strip()
        m = head_rgx.match(line)
        if m:
            pounds, text = m.groups()

            depth = len(pounds)

            while len(sections) >= depth:
                sections.pop()

            sections.append(text)

        else:
            yield sections, line

discipline_rgx = re.compile('[*] (.+)')
def sectioned_discipline_lines():
    for sections, line in sectioned_lines():
        if sections[0:2] == ['Introduction', 'The Database']:
            m = discipline_rgx.match(line)
            if m:
                yield sections[2:], m.groups()[0]

lifespan_both_rgx = re.compile('(?P<birth_date>[^-]+)-(?P<death_date>.+)')
lifespan_birth_rgx = re.compile('b. (?P<birth_date>.+)')
lifespan_death_rgx = re.compile('b. (?P<death_date>.+)')

def parse_lifespan(lifespan):
    if lifespan is None:
        return dict()

    m = lifespan_both_rgx.fullmatch(lifespan)
    if m:
        return m.groupdict()

    m = lifespan_birth_rgx.fullmatch(lifespan)
    if m:
        return m.groupdict()

    return lifespan_death_rgx.fullmatch(lifespan).groupdict()

# name_and_lifespan_rgx = re.compile('(?P<name_plus_link_maybe>.+)(?: \((?P<lifespan>[^)]+)\))?')
name_and_lifespan_rgx = re.compile('(?P<name_plus_link_maybe>.+?)(?: \((?P<lifespan>[^)]+)\))?')#.fullmatch("Bob (5-10)").groupdict()
name_rgx_s = "(?P<name>[^()]+)"
name_rgx = re.compile(name_rgx_s)
name_with_link_rgx = re.compile("(?P<name_with_link>\[%s\]\((?P<wikipedia_url>https://en\.wikipedia\.org/wiki/(?P<wikipedia_entry>[^\]]+))\))" % name_rgx_s)
def discipline_data():
    for sections, line in sectioned_discipline_lines():
        # print(line)

        name_and_lifespan, discipline_date, tagline, notes = line.split('—')

        name_and_lifespan_groups = name_and_lifespan_rgx.fullmatch(name_and_lifespan).groupdict()

        name_plus_link_maybe = name_and_lifespan_groups['name_plus_link_maybe']
        m = name_with_link_rgx.fullmatch(name_plus_link_maybe)
        if m:
            fields = m.groupdict()
            del fields['name_with_link']
            del fields['wikipedia_entry']
        else:
            fields = {'name': name_plus_link_maybe}

        # name_with_link_groups = name_with_link_rgx.fullmatch(name_and_lifespan_groups['name_plus_link_maybe']).groupdict()

        # fields = name_with_link_groups
        # fields['lifespan'] = name_and_lifespan_groups['lifespan']
        fields.update(parse_lifespan(name_and_lifespan_groups['lifespan']))
        fields['date_md'] = discipline_date
        fields['date_txt'] = markdown_to_txt(discipline_date)
        fields['tagline_md'] = tagline
        fields['tagline_txt'] = markdown_to_txt(tagline)
        fields['notes_md'] = notes
        fields['notes_txt'] = markdown_to_txt(notes)

        fields['outcome'] = notes_txt_to_outcome(fields['notes_txt'])

        yield fields

        # yield {
        #     "name_and_lifespan": name_and_lifespan_groups,
        #     "date": discipline_date,
        #     "tagline": tagline,
        #     "notes": notes
        # }


md = mistune.Markdown()
html = html2text.HTML2Text()
html.ignore_links = True
def markdown_to_txt(markdown):
    return html.handle( md.render(markdown) ).strip().replace('\n',' ').replace('  ',' ')

token_rgx = re.compile('[a-z0-9-]+')
def notes_txt_to_outcome(notes_txt):
    parts = token_rgx.findall(notes_txt.lower())
    if parts[0] in ('apparently','probably','presumably'):
        return parts[1]

    if parts[0:2] == ['no', 'action']:
        return "no action"

    if parts[0] == 'deprived':# Special case for Matthias F. Cowley
        return "priesthood deauthorized"

    if parts[0] == 'withdrew':
        return "resigned"

    return parts[0]

if __name__=="__main__":
    for d in discipline_data():
        print(json.dumps(d))
