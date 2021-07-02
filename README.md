# YAMLmaker
**Stop Templating. Start Generating.**

YAMLmaker is a simple utility module to help you *generate* YAML using pure python.
## Hello World
`pip install yamlmaker`
```python
#hello_world.py
from yamlmaker import generate

config = {
  "hello": "world"
}

generate(config)
```

```
python hello_world.py
```
```yaml
#hello_world.yml
hello: world
```
## Background
YAML is being used for many of the cool new tools in technology. Kubernetes, Concourse, Salt, Ansible etc. all use YAML but building complex configurations can be a real pain.

It all starts with trying to interpolate a few variables into a YAML config, but before you know it, you're adding if statements, looping, and developing custom macros. perhaps you're using jinja2, YTT, spruce, or kustomize. These tools all try to work within the YAML document itself and can only offer so much control.  

At some point you need to ask yourself if it's easier adding a programing language within a data structure or working with a data structure within a programing language.  That's where YAMLmaker's approach comes from.  This isn't a new tool or CLI utility, it's simply a helper module which allows you to simply generate YAML using pure python.

## Python 3.9 Caveat
This module strictly works with python `3.9+`. The reason being is that 3.9 introduces the new [dictionary union operator](https://www.python.org/dev/peps/pep-0584/) `dict1 | dict2`.


## Utilities
### generate(list | dictionary)
The `generate()` function is the core of YAMLmaker. Under the cover it wraps the PyYAML's `yaml.dump()` function. In addition to just dumping to a YAML file it does the following.

1. Creates a YAML file with the same name as the Python file. i.e. `python my_config.py` will produce a file called `my_config.yml`
2. Handles multiline content using the yaml `|- `. For example, if you include a certificate it will display nicely on multiple lines.
3. Does not include anchors or pointers in the yaml `& and *` etc. 
4. Preserves Sorting.  The order in which you write your configuration will be the same order when generated into YAML.
#### Example
```python
#example.py
from yamlmaker import generate
config = {
  "hello": "world"
}

generate(config)
```
```yaml
#example.yml
hello: world
```

### env(string)
The `env()` utility returns the value of the name of an environment variable, passed, as a string.

If the environment variable does not exist it will return an empty string, `""`.

#### Example
```bash
#bash
export FOO="bar"
```

```python
#example.py
from yamlmaker import generate, env
config = {
  "foo": env("FOO")
}

generate(config)
```
```yaml
#example.yml
foo: bar
```

### cmd(string)
The `cmd()` function will return the value for the command passed to it as string. For instance, if you have to pluck a secret from vault or require the output of a bash/powershell command. 

#### Powershell Example
```python
#example.py
from yamlmaker import generate, cmd
config = {
  "foo": cmd("powershell Write-Host 'bar'")
}
generate(config)
```
```yaml
#example.yml
foo: bar
```
#### Bash Example
```python
#example.py
from yamlmaker import generate, cmd
config = {
  "foo": cmd("echo bar") #*
}
generate(config)
```
```yaml
#example.yml
foo: bar
```
***Note:** When passing bash commands, remove the quotes around strings to ensure the value is returned properly.  If you need to use an environment variable within the command you can do this: 
```python
cmd("echo " + env('FOO'))
```

### Sources(dictionary)
The `Sources` class helps with sourcing in external YAML data, such as variable files.

Sources works by instantiating a new instance of `Sources` and passing it dictionary where the labels are the keys and the file_paths are the values.  This ensures that the files are only loaded once, and it provides an alias that the file can go by to avoid referencing long path names every time a value is needed from the source file.

#### Example
```python
from yamlmaker import Sources

sources = Sources({
  "foo-vars": "some/path/to/foo-vars.yml",
  "bar-vars": "some/path/to/bar-vars.yml"
})
```

### Sources.grab(label, path)
Once an instance of sources has been created, you can then use the `grab()` method to pluck out values.

The grab method takes the label of the source to grab from and the path to the value using dot notation.  Using integers will reference the position of a list item.  

#### Examples
```yaml
# foo-vars.yml
foo: bar
biz: baz
buz:
  - boo
  - goo
  - doo
```
```yaml
# bar-vars.yml
alpha:
  beta:
    - one: 1
      two: 2
      three: 3
    - ten: 10
      twenty: 20
```

```python
#example.py
from yamlmaker import generate, Sources

sources = Sources({
  "foo-vars": "some/path/to/foo-vars.yml",
  "bar-vars": "some/path/to/bar-vars.yml"
})

config = {
  "thing-one": sources.grab("foo-vars","biz") ,
  "thing-two": sources.grab("foo-vars", "buz.1")
  "thing-three": sources.grab("bar-vars", "alpha.beta.1.ten")
}

generate(config)
```

```yaml
#example.yml
thing-one: baz
thing-two: goo
thing-three: 10
```

### Files(dictionary)
The `Files` class helps with sourcing in external file content, such as pem files, etc.  

Sources works by instantiating a new instance of `Files` and passing it dictionary where the labels are the keys and the file_paths are the values.  This ensures that the files are only loaded once, and it provides an alias that the file can go by to avoid referencing long path names every time the contents of a file is needed.

#### Example
```python
from yamlmaker import Files

files = Files({
  "pub-key": "some/path/to/pubkey.cert"
})
```
### Files.grab(label)
Once an instance of files has been created, you can then use the `grab()` method to retrieve the contents of a file by its label.


#### Examples
```
#pubkey.cert

-----BEGIN CERTIFICATE-----
MIINMDCCDBigAwIBAgIQFwVvbgUxBFQFAAAAAIfenTANBgkqhkiG9w0BAQsFADBC
MQswCQYDVQQGEwJVUzEeMBwGA1UEChMVR29vZ2xlIFRydXN0IFNlcnZpY2VzMRMw
EQYDVQQDEwpHVFMgQ0EgMU8xMB4XDTIxMDUyNDAxMzYwMFoXDTIxMDgxNjAxMzU1
OVowZjELMAkGA1UEBhMCVVMxEzARBgNVBAgTCkNhbGlmb3JuaWExFjAUBgNVBAcT
DU1vdW50YWluIFZpZXcxEzARBgNVBAoTCkdvb2dsZSBMTEMxFTATBgNVBAMMDCou
...
U2mUhTIelGiXuuurDjTQD11oCR2jrp6hi4aToQ+yG3b1Kv82JBcZxRhUggLVbGJM
ktsuqVkVli8n7gmjGH5pP27T/JqAam4ej/Gqd+6SklI9xE0+DHI2bkB0IGTdzTPR
8dt6A10e5tlmXsAb/8HCyUuNwqtUrgQN4zKmigZG8SdTYqlfy1mXHvPO6b/qZ0jF
ZUKuCmlAJryMEsyJdcX6yl4Hvub6/O7QUoaxr6L3Kr3UJ8hIy8GdmqLP2YWVt9Au
Uz4hDpQ9cE705FYs43M7S/40IeI=
-----END CERTIFICATE-----
```
```python
#example.py
from yamlmaker import generate, Files

files = Files({
  "pub-key": "some/path/to/pubkey.cert"
})

config = {
  "some-pub-key": files.grab("pub-key")
}

generate(config)
```
```yaml
some-pub-key: |-
  -----BEGIN CERTIFICATE-----
  MIINMDCCDBigAwIBAgIQFwVvbgUxBFQFAAAAAIfenTANBgkqhkiG9w0BAQsFADBC
  MQswCQYDVQQGEwJVUzEeMBwGA1UEChMVR29vZ2xlIFRydXN0IFNlcnZpY2VzMRMw
  EQYDVQQDEwpHVFMgQ0EgMU8xMB4XDTIxMDUyNDAxMzYwMFoXDTIxMDgxNjAxMzU1
  OVowZjELMAkGA1UEBhMCVVMxEzARBgNVBAgTCkNhbGlmb3JuaWExFjAUBgNVBAcT
  DU1vdW50YWluIFZpZXcxEzARBgNVBAoTCkdvb2dsZSBMTEMxFTATBgNVBAMMDCou
  ...
  U2mUhTIelGiXuuurDjTQD11oCR2jrp6hi4aToQ+yG3b1Kv82JBcZxRhUggLVbGJM
  ktsuqVkVli8n7gmjGH5pP27T/JqAam4ej/Gqd+6SklI9xE0+DHI2bkB0IGTdzTPR
  8dt6A10e5tlmXsAb/8HCyUuNwqtUrgQN4zKmigZG8SdTYqlfy1mXHvPO6b/qZ0jF
  ZUKuCmlAJryMEsyJdcX6yl4Hvub6/O7QUoaxr6L3Kr3UJ8hIy8GdmqLP2YWVt9Au
  Uz4hDpQ9cE705FYs43M7S/40IeI=
  -----END CERTIFICATE-----
```

### Include
The `Include` helper class acts like an if statement and is useful when you need to append to or merge additional data into a data structure.  

### Include.when(statement, if_block, else_block)
The Include class contains one method, called, `when` which implements an if-else block.

The `if_block` and `else_block` simply return the value passed to them if the expression is `True` or `False`.  By default, the `else_block` will return an empty for the `Type` of the value passed in for the `if_block`. i.e. `""`, `[]`, or `{}`.

#### Examples with Dictionaries
**When True**
```python
#example.py
from yamlmaker import generate, Include

config = {
  "foo": "bar"
} | Include.when("x" == "x", {
  "biz": "baz"
})

generate(config)
```
```yaml
#example.yml
foo: bar
biz: baz
```
**When False**
```python
#example.py
from yamlmaker import generate, Include

config = {
  "foo": "bar"
} | Include.when("x" == "y", {
  "biz": "baz"
})

generate(config)
```
```yaml
#example.yml
foo: bar
```
**Use of Else Block**
```python
#example.py - using positional args
from yamlmaker import generate, Include

config = {
  "foo": "bar"
} | Include.when("x" == "y", {
  "biz": "baz"
}, {
  "biz": "zub"
})

generate(config)
```
```python
#example.py - using keyword args
from yamlmaker import generate, Include

config = {
  "foo": "bar"
} | Include.when("x" == "y", if_block={
  "biz": "baz"
}, else_block={
  "biz": "zub"
})

generate(config)
```

```yaml
#example.yml
foo: bar
biz: zub
```
#### Examples with Lists
```python
#example.py
from yamlmaker import generate, Include

config = {
  "foos": [
    "biz",
    "baz",
  ] + Include.when("x" == "x", [
    "bin",
    "zub"
  ])
}
generate(config)
```
```yaml
#example.yml
foos:
- biz
- baz
- bin
- zub

```
#### In-line List Examples
Instead of using the concat operator, `+` you can also specify the Include to be used in-line within the data-structure. 

However, this will produce empty values within the list. see `prune_empty()` for how to deal with this.

**When True**
```python
from yamlmaker import generate, Include

config = {
  "foos": [
    "biz",
    Include.when("x" == "x", "baz")
  ]
}
generate(config)
```
```yaml
#example.yml
foos:
- biz
- baz
```
**When False**
```python
from yamlmaker import generate, Include

config = {
  "foos": [
    "biz",
    Include.when("x" == "y", "baz")
  ]
}
generate(config)
```
```yaml
#example.yml
foos:
foos:
- biz
- ""
```

### prune_empty()
As seen above, when using `Include.when()` in-line, within a list, it will leave a blank value where the `Include` statement was. To solve this you can wrap the list with `prune_empty()` which will eliminate the empty values.

```python
#example.py
from yamlmaker import generate, Include, prune_empty

config = {
  "foos": prune_empty([
    "biz",
    Include.when("x" == "y", "baz")
  ])
}
generate(config)
```
```yaml
#example.yml
foos:
- biz
```

## Pure Python Examples
Some examples using just Python and generate.
### For Loop
YAMLmaker doesn't include things like looping etc. But here is an example using Python and the `for` loop to help generate a list.
```python
#example.py
from yamlmaker import generate

config = {
  "things": [
    {
      "foo": item
    } for item in [
      "bar",
      "biz",
      "baz"
    ]
  ]
}
generate(config)
```
```yaml
#example.yml
things:
- foo: bar
- foo: biz
- foo: baz
```
### Merging Dictionaries
In Python 3.9 and in the examples above, the union operator `|` is used heavily to merge multiple dictionaries together.  Just be aware that the behavior is to always override an existing key rather than perform a deep merge.
```python
#example.py
from yamlmaker import generate

config_one = {
  "foo": "bar"
}

config_two = {
  "biz": "bar",
  "things": [
    "one",
    "two"
  ]
}

config_three = {
  "foo": "notbar",
  "things": [
    "three"
  ]
}

config = config_one | config_two | config_three
generate(config)
```
```yaml
#example.yml
foo: notbar
biz: bar
things:
- three
```