from yamlmaker import generate, env, Sources, cmd

sources = Sources({
  "container-vars": "environments/" + env("ENVIRONMENT") + "/container-vars.yml",
  "replica-and-rollout-strategy": "environments/" + env("ENVIRONMENT") + "/replica-and-rollout-strategy.yml",
})

secrets = {
  "db-password": cmd("powershell Write-Host 'SuperSecret'")
}

config = {
  "apiVersion": "apps/v1",
  "kind": "Deployment",
  "metadata": {
    "name": "sl-demo-app"
  },
  "spec": {
    "selector": {
      "matchLabels": {
        "app": "sl-demo-app"
      }
    },
    "template": {
      "metadata": {
        "labels": {
          "app": "sl-demo-app"
        }
      },
      "spec": {
        "containers": [
          {
            "name": "app",
            "env": sources.grab("container-vars", "app") + [
              {
                "name": "DB_PASSWORD",
                "value": secrets["db-password"]
              }
            ],
            "image": "foo/bar:latest",
            "ports": [
              {
                "name": "http",
                "containerPort": 8080,
                "protocol": "TCP"
              }
            ]
          }
        ] # end containers
      } # end spec
    } # end template
  } | sources.grab("replica-and-rollout-strategy", "meta") # end spec
} # end config

generate(config)