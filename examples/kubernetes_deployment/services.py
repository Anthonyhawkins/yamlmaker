from yamlmaker import generate

config = {
  "apiVersion": "v1",
  "kind": "Services",
  "metadata": {
    "name": "sl-demo-app"
  },
  "spec": {
    "ports": [
      {
        "name": "http",
        "port": 8080
      }
    ],
    "selector": {
      "app": "sl-demo-app"
    }
  }
}

generate(config)