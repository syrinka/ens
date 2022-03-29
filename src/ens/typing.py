import re
from dataclasses import dataclass, field, InitVar, asdict
from typing import List, Dict, Tuple, Union, Literal, NewType, Type
from datetime import datetime

import ens.config as conf
from ens.exceptions import *


@dataclass
class Code(object):
    _code_format = re.compile(
        r'([a-zA-Z0-9\-_\.]+)' + conf.CODE_DELIM + r'([a-zA-Z0-9\-_\.]+)'
    )

    code_str: InitVar[str]

    remote: str = field(init=False)
    nid: str = field(init=False)


    def __repr__(self):
        return self.remote + conf.CODE_DELIM + self.nid


    def __eq__(self, other):
        return repr(self) == (
            other if isinstance(other, str) \
            else repr(other)
        )


    def __iter__(self):
        return iter((self.remote, self.nid))


    def __post_init__(self, code_str: str):
        match = self._code_format.match(code_str)
        if match is None:
            raise InvalidCode(code_str)

        self.remote, self.nid = match[1], match[2]


    def __rich__(self):
        return '[plum4]{}[/]{}[cyan]{}[/]'.format(
            self.remote, conf.CODE_DELIM, self.nid
        )


@dataclass
class Novel(object):
    remote: str
    nid: str
    title: str
    author: str
    intro: str = None
    last_update: datetime = None


    def __rich__(self):
        return '[green]{}[/]  [magenta]@{}[/] ({})'.format(
            self.title, self.author, self.code.__rich__()
        )


    @property
    def code(self) -> Code:
        return Code(self.remote + conf.CODE_DELIM + self.nid)


    def as_dict(self):
        return asdict(self)


@dataclass
class Shelf(object):
    name: Union[str, None] = None
    novels: List[Novel] = field(default_factory=list)


    def __add__(self, novel):
        self.novels.append(novel)
        return self


    def __rich_console__(self, console, opt):
        if self.name is not None:
            yield f'\[{self.name}]'
        for i, novel in enumerate(self.novels):
            yield '#{}  {}'.format(i+1, novel.__rich__())


@dataclass
class RemoteNovel(object):
    code: Code
    title: str
    author: str
    intro: str = ''
    chap_count: int = None
    tags: set = field(default_factory=set)
    point: float = None
    fav: int = None
    last_update: datetime = None
    finish: bool = None
    expand: dict = field(default_factory=dict)


    def __rich__(self):
        text = ''
        def push(i='', style=None, nl=True):
            nonlocal text
            if style:
                text += '[{}]{}[/]'.format(style, i)
            else:
                text += i
            if nl:
                text += '\n'

        push('{}'.format(self.title), 'green', nl=False)
        if self.point != None:
            push(' <{}>'.format(self.point), 'yellow', nl=False)
        if self.fav != None:
            push(' ♥{}'.format(self.fav), 'bright_red', nl=False)
        push()
        if self.author is not None:
            push(self.author, 'bright_magenta')
        else:
            push('佚名')
        if self.chapters != None:
            push('{}章'.format(self.chap_count))
        if self.tags:
            push(' '.join('[{}]'.format(tag.strip()) for tag in self.tags))
        else:
            push('No tag')
        push(self.intro or 'No intro', 'cyan')
        for i, j in self.expand.items():
            push('{}: {}'.format(i, j))
        if self.last_update is not None:
            push('最后一次更新于 {}'.format(self.last_update))
        if self.finish:
            push('已完结', 'green')
        return text[:-1] # 去掉最后一个换行符


    def as_novel(self) -> Novel:
        return Novel(
            self.code.remote, self.code.nid,
            self.title, self.author, self.intro, self.last_update
        )


Catalog = NewType('Catalog', List[Dict[str, Union[str, List[str]]]])
"""
- name: vol1
    cids: 
    - cid1
    - cid2
    - ...
- ...
"""

if __name__ == '__main__':
    pass
