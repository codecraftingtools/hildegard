# Copyright (c) 2020 Jeffrey A. Webb

import yaml

from collections import OrderedDict
import sys

class Anonymous_Elements_Base(list):
    pass

class Named_Elements_Base(OrderedDict):
    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        value.name = key

def elements(element_type=None, attr_name=None, anonymous=False):
    if anonymous:
        if element_type is None:
            class_name = "Anonymous_Elements"
        else:
            class_name = "Anonymous_" + element_type.__name__ + "_Elements"
        base = Anonymous_Elements_Base
    else:
        if element_type is None:
            class_name = "Named_Elements"
        else:
            class_name = "Named_" + element_type.__name__ + "_Elements"
        base = Named_Elements_Base
    t = type(class_name, (base,), {})
    t._element_type = element_type
    t._attr_name = attr_name
    t._anonymous = anonymous
    return t

class Attribute:
    def __init__(self, name, type=None, alias=None, aliases=None, save=None,
                 reference=None, **kw):
        self.name = name
        self.type = type
        self.save = save
        self.reference = reference
        self.aliases = list(aliases) if aliases is not None else []
        if alias is not None:
            self.aliases.append(alias)
        self.default = None
        self.use_default = False
        self.value = None
        self.fixed_value = False
        for key, value in kw.items():
            if key == "default":
                self.use_default = True
                self.default = value
            elif key == "value":
                self.fixed_value = True
                self.value = value
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
                cls._override(et, a)
            else:
                et._attr_info_list.append(a)
                et._attr_info[a.name] = a
                for alias in a.aliases:
                    et._attr_info[alias] = a
        return et

    def _override(et, new_a):
        existing_a = et._attr_info[new_a.name]
        if existing_a.type is not None:
            if new_a.type is None:
                new_a.type = existing_a.type
            else:
                raise Exception("attribute type has already been specified")
        if existing_a.save is not None:
            if new_a.save is None:
                new_a.save = existing_a.save
            else:
                raise Exception("attribute save has already been specified")
        if existing_a.reference is not None:
            if new_a.reference is None:
                new_a.reference = existing_a.reference
            else:
                raise Exception(
                    "attribute reference has already been specified")
        if existing_a.fixed_value:
            if new_a.fixed_value:
                raise Exception("attribute value has already been specified")
            else:
                new_a.fixed_value = existing_a.fixed_value
        if existing_a.use_default and not new_a.use_default:
            new_a.use_default = True
            new_a.default = existing_a.default
        for alias in reversed(existing_a.aliases):
            if alias in new_a.aliases:
                new_a.aliases.remove(alias)
            new_a.aliases.insert(0,alias)
        # Replace existing attribute with new one
        old_index = et._attr_info_list.index(existing_a)
        et._attr_info_list.insert(old_index, new_a)
        et._attr_info_list.remove(existing_a)
        et._attr_info[new_a.name] = new_a
        for alias in new_a.aliases:
            et._attr_info[alias] = new_a

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
        if self._attr_info[key].fixed_value:
            return self._attr_info[key].value
        unaliased_key = self._attr_info[key].name
        return self._attrs[unaliased_key]

    def __setitem__(self, key, value):
        unaliased_key = self._attr_info[key].name
        if not unaliased_key in self._attrs:
            raise KeyError(key)
        if self._attr_info[key].fixed_value:
            raise AttributeError("attribute value is fixed")
        self._attrs[unaliased_key] = value

    def __getattr__(self, key):
        return self.__getitem__(key)

    def __setattr__(self, key, value):
        if "_attrs" in self.__dict__ and key in self._attrs:
            self.__setitem__(key, value)
        else:
            super().__setattr__(key, value)

def _find_referenced_entities(item, referenced_items):
    if isinstance(item, Entity):
        for name, value in item._attrs.items():
            if type(item)._attr_info[name].reference is True:
                referenced_items.append(value)
            if isinstance(value, Entity):
                _find_referenced_entities(value, referenced_items)
            elif isinstance(value, list):
                for list_item in value:
                    _find_referenced_entities(list_item, referenced_items)
            elif isinstance(value, OrderedDict):
                for subname, subvalue in value.items():
                    _find_referenced_entities(subvalue, referenced_items)
    elif isinstance(item, list):
        for subitem in item:
            _find_referenced_entities(subitem, referenced_items)
    return referenced_items
    
def save_to(item, level=0, file=None, found=None):
    top = False
    if found is None:
        top = True
        found = _find_referenced_entities(item, [])
    space = "  "
    if file is None:
        file = sys.stdout
    if top:
        file.write('# {format: "yaml", version: 0}')
    if isinstance(item, Entity):
        file.write(f"\n{space*level}- {item.__class__.__name__}:\n")
        if item in found:
            file.write(f"{space*(level+2)}_id: {id(item)}\n")
        for name, value in item._attrs.items():
            if value is None or value is "":
                pass
            elif type(item)._attr_info[name].reference is True:
                file.write(f"{space*(level+2)}{name}: {id(value)}\n")
            elif type(item)._attr_info[name].save is not False:
                if isinstance(value, list) and not value:
                    continue # Don't write out empty list items
                file.write(f"{space*(level+2)}{name}:")
                save_to(value, level=level+3, file=file, found=found)
    elif isinstance(item, list):
        if not item:
            file.write(" []\n")
        else:
            for list_item in item:
                save_to(list_item, level=level, file=file, found=found)
    elif isinstance(item, OrderedDict):
        for name, value in item.items():
            save_to(value, level=level, file=file, found=found)
    else:
        file.write(f" {item}\n")

def save(item, file_name=None):
    f = None
    if file_name:
        print(f"saving to file: {file_name}")
        f = open(file_name, "w")
    save_to(item, file=f)
    if file_name:
        f.close()
    
def _load_entities(tree, map, ids):
    entities = []
    for item in tree:
        entity_type_name = list(item.keys())[0]
        entity_type = map[entity_type_name]
        value = item[entity_type_name]
        attrs = {}
        entity_id = None
        for a_name, a_value in value.items():
            if a_name == "_id":
                entity_id = a_value
                continue
            if isinstance(a_value, list):
                attrs[a_name] = _load_entities(a_value, map, ids)
            elif isinstance(a_value, dict):
                pass
            else:
                if entity_type._attr_info[a_name].reference is True:
                    attrs[a_name] = ids[a_value]
                else:
                    attrs[a_name] = a_value
        entity = entity_type(**attrs)
        if entity_id is not None:
            ids[entity_id] = entity
        entities.append(entity)
    return entities

def load(file_name, map):
    ids = {}
    text = open(file_name).read()
    tree = yaml.load(text)
    return _load_entities(tree, map, ids)
