from os.path import expanduser
import requests
from requests.adapters import HTTPAdapter, RetryError
from urllib3.util.retry import Retry
from akamai.edgegrid import EdgeGridAuth, EdgeRc
from configparser import NoSectionError, NoOptionError
from urllib import parse
import os

from dotenv import load_dotenv
load_dotenv()

class EdgegridError(RuntimeError):
  pass

class Session(requests.Session):
  def __init__(self, switch_key=None, **kwargs):
    try:
      super(Session, self).__init__(**kwargs)

      self.switch_key = None

      if switch_key != None:
        self.switch_key = switch_key
      self.auth = EdgeGridAuth(
        client_token=os.environ.get('AKAMAI_CREDS_CLIENT_TOKEN'),
        client_secret=os.environ.get('AKAMAI_CREDS_CLIENT_SECRET'),
        access_token=os.environ.get('AKAMAI_CREDS_ACCESS_TOKEN'),
      )
      self.mount("https://", HTTPAdapter(
        pool_connections=1,
        pool_maxsize=10,
        max_retries=Retry(
          total=3,
          backoff_factor=5,
          status_forcelist=[429, 500, 502, 503, 504],
          allowed_methods=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE"],
        )
      ))
    except NoSectionError as e:
      raise EdgegridError(e.message)
    except NoOptionError as e:
      raise EdgegridError(e.message)

  def request(self, method, url, params=None, **kwargs):
    try:
      if self.switch_key:
        params = params if params else {}
        params.update(accountSwitchKey=self.switch_key)
      baseUrl = "https://{host}".format(host=os.environ.get('AKAMAI_CREDS_HOST'))
      url = parse.urljoin(baseUrl, url)
      response = super(Session, self).request(method, url, params=params, **kwargs)
      if response.status_code in (401, 403, *range(500, 600)):
        raise EdgegridError(response.json())
      return response
    except RetryError as e:
      raise EdgegridError(str(e))
  
  def upsert_ekv_item(self, namespace_id, group_id, item_id, payload, network):
      url = f'/edgekv/v1/networks/{network}/namespaces/{namespace_id}/groups/{group_id}/items/{item_id}'
      response = self.put(url, json=payload)
      return response

  def delete_ekv_item(self, namespace_id, group_id, item_id, network):
      url = f'/edgekv/v1/networks/{network}/namespaces/{namespace_id}/groups/{group_id}/items/{item_id}'
      response = self.delete(url)
      return response