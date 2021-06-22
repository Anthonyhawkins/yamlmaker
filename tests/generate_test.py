import os
from src.yamlmaker import generate

def test_generate():
  config = {
    "foo": "bar",
    "biz": "baz",
    "buz": ["boo", "goo", "doo"],
    "alpha": {
      "beta": [
        {
          "one": 1,
          "two": 2,
          "three": 3
        },
        {
          "ten": 10,
          "twenty": 20
        }
      ]
    }
  }

  generate(config)
  assert os.path.exists("generate_test.yml")
  os.remove("generate_test.yml")