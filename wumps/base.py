# Copyright (c) 2020 Jeffrey A. Webb

class Attribute:
    def __init__(self, name, type=None, alias=None, aliases=None,
                 element=None, element_aliases=None, **kw):
        self.name = name
        self.type = type
        self.aliases = list(aliases) if aliases is not None else []
        if alias is not None:
            self.aliases.append(alias)
        # Note that element/element_aliases are not yet implemented
        self.element_aliases = (
            list(element_aliases) if element_aliases is not None else [])
        if element is not None:
            self.element_aliases.append(element)
        self.default = None
        self.use_default = False
        for key, value in kw.items():
            if key == "default":
                self.use_default = True
                self.default = value
            else:
                raise TypeError(
                    f"__init__() got an unexpected keyword argument '{key}'")

class Entity_Type(type):
    def __new__(cls, *args, **kw):
        et = super().__new__(cls, *args, **kw)
        et._attr_info_list = list(et._attr_info_list) if hasattr(
            et, "_attr_info_list") else list()
        et._attr_info = dict(et._attr_info) if hasattr(
            et, "_attr_info") else dict()
        for a in et._attributes:
            if a.name in et._attr_info:
                raise Exception(f"'{a.name}' attribute already exists")
            et._attr_info_list.append(a)
            et._attr_info[a.name] = a
            for alias in a.aliases:
                et._attr_info[alias] = a
        return et

class Entity(metaclass=Entity_Type):
    _attributes = (
        Attribute("name", str, default=""),
    )
    def __init__(self, *args, **kw):
        self._attrs = {}
        for a in self._attr_info_list:
            self._attrs[a.name] = (
                a.default if a.use_default else a.type() if
                a.type is not None else None)
        for key, value in kw.items():
            a = self._attr_info[key]
            if (a.type is not None and
                not isinstance(value, Entity)): # no Entity copy constructor yet
                value = a.type(value)
            self._attrs[a.name] = value

    def __getitem__(self, key):
        return self._attrs[key]

    def __setitem__(self, key, value):
        if not key in self._attrs:
            raise KeyError(key)
        self._attrs[key] = value

    def __getattr__(self, key):
        return self.__getitem__(key)

    def __setattr__(self, key, value):
        if "_attrs" in self.__dict__ and key in self._attrs:
            self.__setitem__(key, value)
        else:
            super().__setattr__(key, value)
