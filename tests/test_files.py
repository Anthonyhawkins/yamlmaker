from src.yamlmaker import Files


def test_files():

  files = Files({
    "my-cert": "tests/test_files/pubkey.cert"
  })

  config = {"foo": files.grab("my-cert")}
  assert config["foo"].startswith("-----BEGIN CERTIFICATE-----")
  assert config["foo"].endswith("-----END CERTIFICATE-----")