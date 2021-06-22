from src.yamlmaker import Sources
import pytest

@pytest.fixture(autouse=True)
def sources():
  sources = Sources({
    "my-vars": "tests/test_vars/vars.yml"
  })
  yield sources

def test_key_value(sources):
  config = {"foo": sources.grab("my-vars", "foo")}
  assert config["foo"] == "bar"

def test_list(sources):
  config = {"buz": sources.grab("my-vars", "buz.1")}
  assert config["buz"] == "goo"

def test_object_list(sources):
  config = {"ten": sources.grab("my-vars", "alpha.beta.1.ten")}
  assert config["ten"] == 10