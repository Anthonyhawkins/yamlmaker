from src.yamlmaker import Include


def test_include_when_if():
  config = {"foo": "bar"} | Include.when("x" == "x", {"biz": "baz"})
  assert config["biz"] == "baz"

def test_include_when_else():
  config = {
    "foo": "bar"
  } | Include.when("x" == "z", if_block={
    "biz": "baz"
  }, else_block={
    "foo": "zoo"
  })

  assert config["foo"] == "zoo"


def test_include_in_list():

  config = [
    "foo",
    "bar",
    Include.when("x" == "x", "baz")
  ]
  
  assert "baz" in config


def test_include_not_in_list():

  config = [
    "foo",
    "bar"
  ] + Include.when("z" == "x", "baz", [])
  
  assert "baz" not in config