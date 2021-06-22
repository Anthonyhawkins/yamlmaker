from src.yamlmaker import env
import os

# This test stays at the top to ensrue empty env
def test_empty_env():
  config = {"foo": env("FOO")}
  assert config["foo"] == ""

def test_env():
  os.environ["FOO"] = "bar"
  config = {"foo": env("FOO")}
  assert config["foo"] == "bar"

