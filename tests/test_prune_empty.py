from src.yamlmaker import prune_empty

def test_prune_empty():
  config = {"foo": prune_empty(["biz", "baz", ""])}
  assert len(config["foo"]) == 2
