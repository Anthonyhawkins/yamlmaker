import inspect
import os
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
    panic(f"Command `{command}` returned a none 0 status code.")
  return completed.stdout.decode('utf-8').rstrip()


class Sources(object):
  """
  Helper class for working with yaml based var files.
  """

  def __init__(self, sources):
    """
    Creat a source mapping of labels to var data and original file path for each file.
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
            print("Error - {f} is Not valid YAML.".format(f=file_path))

      except FileNotFoundError:
        print("Error - {f} No Such File.".format(f=file_path))

  def grab(self, source_label, path):
    """
    Method for grabbing a var from a var source, via the label of the file
    and the dot-deliminated path where the variable resides within the data.
    i.e. meta.endpoints.db
    """
    if source_label not in self.source_map:
      print("Error - No Source with label {l} exists".format(l=source_label))
      return None

    data = self.source_map[source_label]["data"]
    file_path = self.source_map[source_label]["file_path"]
    dict_path = ''
    for part in path.split('.'):
      dict_path += "[" + part + "]" if part.isdigit() else "['" + part + "']"

    try:
      return eval("data" + dict_path)
    except SyntaxError:
      print("Error - {p} is invalid syntax. Evaluated to {d}".format(p=path, d=dict_path))
      sys.exit(1)
    except KeyError:
      print("Error - {p} does not exist in file: {f}".format(p=path, f=file_path))
      sys.exit(1)
    except IndexError:
      print("Error - {p} index our of range in file: {f}".format(p=path, f=file_path))
      sys.exit(1)


class Files(object):
  """
  Helper class for working with the whole contents of files.
  """
  def __init__(self, files):
    """
    Creat a file mapping of labels to file contents and original file path for each file.
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
        print("Error - {f} No Such File.".format(f=file_path))

  def grab(self, file_label):
    """
    Method for grabbing the contnets of a file based on its label from the file_map
    """
    if file_label not in self.file_map:
      print("Error - No File with label {l} exists".format(l=file_label))
      return None
    return self.file_map[file_label]["text"]


class Include(object):
  """
  Implementation of the if else statement to be used when conditionally
  merging two dictionaries.
  """
  @staticmethod
  def when(expression, if_block, else_block={}):
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
  

