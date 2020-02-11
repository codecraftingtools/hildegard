# Copyright (c) 2020 Jeffrey A. Webb

import inspect

class Attribute:
    def __init__(self, name, type=None, default=None, alias=None, aliases=None):
        self.name = name
        self.type = type
        self.aliases = aliases if aliases is not None else []
        if alias is not None:
            self.aliases.append(alias)
        self.default = default if default is not None else default
        
class Entity:
    _attributes = ()

    def __init__(self, *args, **keywords):
        classes = inspect.getmro(type(self))[:-1]
        self._attr_dict = {}
        self._attr_aliases = {}
        for c in reversed(classes):
            for a in c._attributes:
                self._attr_dict[a.name] = a
                for alias in a.aliases:
                    self._attr_aliases[alias] = a.name
                if a.default is None:
                    if type is None:
                        setattr(self, a.name, None)
                    else:
                        setattr(self, a.name, a.type())
                else:
                    setattr(self, a.name, a.default)
        for arg in args:
            i = 0
            for name in arg:
                i = i + 1
                value = arg[name]
                if i > 1:
                    raise Exception("Entity constructor args should be "
                                    "dictionaries with only one element")
            self._set_attr(name, value)

        for name, value in keywords.items():
            self._set_attr(name, value)
            
    def _set_attr(self, name, value):
        name = self._attr_aliases.get(name, name)
        a = self._attr_dict[name]
        if a.type in [list]:
            if type(value) in [list, tuple]:
                for subitem in value:
                    getattr(self, name).append(subitem)
            else:
                getattr(self, name).append(value)
        else:
            setattr(self, name, value)
