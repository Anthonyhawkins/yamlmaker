import os 
from src.yamlmaker import cmd

def test_cmd():
  if os.name == "nt":
    config = {"foo": cmd("powershell Write-Host 'bar'")}
  else:
    config = {"foo": cmd("echo bar")}
  assert config["foo"] == "bar"

