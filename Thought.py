import re 

from dataclasses import dataclass

from typing import List, Dict

from .Name import Name
from .Link import Link
from .Tag import Tag


@dataclass
class Thought:
    """Represents a single thought in the ThoughtBox."""

    name: Name
    title: str
    tags: List[Tag]
    links: List[Link]

    content: List[str]
    sources: List[str]

    @staticmethod
    def parse(lines: List[str], name: Name) -> "Thought":
        print_warnings=False
        heading = None
        result:Dict[str,List[str]] = {'title':[''], 'content':[], 'tags': [], 'sources': [], 'links':[]}
        for line in lines:
            if line.startswith('# '):
                line= line[1:].strip()
                if heading is None:
                    heading = 'content'
                    result['title']=[line]
                else:
                    heading=line
            elif heading in result:
                result[heading].append(line)
            else:
                if print_warnings:
                    print('Warning: did not understand heading %s in %s. Ignoring.' % (heading, name))

        tags = []
        tag_re = re.compile('#\w*')

        for line in result['content']:
            matches = tag_re.finditer(line)
            for m in matches:
                tag = m.group()[1:]
                tags.append(tag)

        for line in result['sources']:
            matches = tag_re.finditer(line)
            for m in matches:
                tag = m.group()[1:]
                tags.append(tag)

        for line in result['tags']:
            if len(line) > 0:
                line = line.strip(' ,')
                tags.extend([ tag.strip() for tag in line.split(',')])


        links = []
        link_re = re.compile('\[\[.*?\]\]')

        for line in result['content']:
            matches = link_re.finditer(line)
            for m in matches:
                link = m.group()[2:-2]
                links.append(link)

        for line in result['sources']:
            matches = link_re.finditer(line)
            for m in matches:
                link = m.group()[2:-2]
                links.append(link)

        return Thought(name = name,
                       title=result['title'][0],
                       tags = [ Tag(id=0,title=t) for t in tags ],
                       links = [ Link(source=name, dest=Name.fromStr(l)) for l in links ],
                       content = result['content'],
                       sources = result['sources']
                       )
    
