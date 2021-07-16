import inspect
import os
import subprocess
import sys
import yaml
from yaml.parser import ParserError


def env(env_variable):
  """
  wrapper for os.getenv
  - return "" string if None to aid 
    with concatination. 
  """
  var = os.getenv(env_variable)
  return var if var else ""


def prune_empty(items):
  """
  Remove None items from a list.
  """
  return list(filter(None, items))


def cmd(command):
  """
  Run a command and return its stdout 
  """
  try:
    completed = subprocess.run(
        command.split(" "),
        stdout=subprocess.PIPE,
    )
  except FileNotFoundError:
    panic(f"Command `{command}` not found.")

  if completed.returncode > 0:
    panic(f"Command `{command}` returned a non 0 status code.")
  return completed.stdout.decode('utf-8').rstrip()


class Sources(object):
  """
  Helper class for working with yaml based var files.
  """

  def __init__(self, sources):
    """
    Create a source mapping of labels to var data and original file path for each file.
    """
    self.source_map = {}
    for source_label, file_path in sources.items():
      self.source_map[source_label] = {
        "data": None,
        "file_path": file_path
      }
      try:
        with open(r'{f}'.format(f=file_path)) as file:
          try:
            self.source_map[source_label]["data"] = yaml.load(file, Loader=yaml.FullLoader)
          except ParserError:
            panic(f"{file_path} is Not valid YAML.")

      except FileNotFoundError:
        panic(f"{file_path} No Such File.")

  def grab(self, source_label, path):
    """
    Method for grabbing a var from a var source, via the label of the file
    and the dot-delimited path where the variable resides within the data.
    i.e. meta.endpoints.db
    """
    if source_label not in self.source_map:
      panic(f"No Source with label {source_label} exists")
      return None

    data = self.source_map[source_label]["data"]
    file_path = self.source_map[source_label]["file_path"]
    dict_path = ''
    for part in path.split('.'):
      dict_path += "[" + part + "]" if part.isdigit() else "['" + part + "']"

    try:
      return eval("data" + dict_path)
    except SyntaxError:
      panic(f"{path} is invalid syntax. Evaluated to {dict_path}")
    except KeyError:
      panic(f"{path} does not exist in file: {file_path}")
    except IndexError:
      panic(f"{path} index our of range in file: {file_path}")


class Files(object):
  """
  Helper class for working with the whole contents of files.
  """
  def __init__(self, files):
    """
    Create a file mapping of labels to file contents and original file path for each file.
    """
    self.file_map = {}
    for file_label, file_path in files.items():
      self.file_map[file_label] = {
        "text": None,
        "file_path": file_path
      }
      try:
        with open(r'{f}'.format(f=file_path)) as file:
          self.file_map[file_label]["text"] = file.read()
      except FileNotFoundError:
        panic(f"{file_path} No Such File.")

  def grab(self, file_label):
    """
    Method for grabbing the contnets of a file based on its label from the file_map
    """
    if file_label not in self.file_map:
      panic(f"No File with label {file_label} exists")
    return self.file_map[file_label]["text"]


class Include(object):
  """
  Implementation of the if else statement to be used when conditionally
  merging two dictionaries or lists.
  """
  @staticmethod
  def when(expression, if_block, else_block=None):
    if not else_block:
      if type(if_block) is list:
        else_block = []
      elif type(if_block) is dict:
        else_block = {}
      else:
        else_block = ""
    return if_block if expression else else_block


def generate(config, name=None, return_result=False):
  """
  Generate a yaml file 
  """
  if not name:
    frame = inspect.stack()[1]
    module = inspect.getmodule(frame[0])
    slash = '\\' if os.name == "nt" else "/"
    filename = module.__file__.split(slash)[-1].replace(".py", "")
  else:
    filename = name

  yaml.SafeDumper.org_represent_str = yaml.SafeDumper.represent_str

  def multi_str(dumper, data):
    if '\n' in data:
      return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
    return dumper.org_represent_str(data)
  yaml.add_representer(str, multi_str, Dumper=yaml.SafeDumper)
  yaml.SafeDumper.ignore_aliases = lambda *args: True

  if return_result:
    return yaml.safe_dump(config, sort_keys=False, default_flow_style=False)

  with open(filename + ".yml", 'w') as file:
      yaml.safe_dump(config, file, sort_keys=False, default_flow_style=False)

def panic(message, error=None):
  """
  Error Out and Exit 1
  """
  print(Text.red(f"Error: {message}"))
  if error: print(Text.red(error))
  sys.exit(1)

class Text(object):
  @staticmethod
  def blue(text):
    return f'\033[94m{text}\033[0m'

  @staticmethod
  def cyan(text):
    return f'\033[96m{text}\033[0m'

  @staticmethod
  def green(text):
    return f'\033[92m{text}\033[0m'

  @staticmethod
  def yellow(text):
    return f'\033[93m{text}\033[0m'

  @staticmethod
  def red(text):
    return f'\033[91m{text}\033[0m'

  @staticmethod
  def bold(text):
    return f'\033[1m{text}\033[0m'

  @staticmethod
  def underline(text):
    return f'\033[4m{text}\033[0m'

  @staticmethod
  def header(text):
    return f'\033[95m{text}\033[0m'
  

