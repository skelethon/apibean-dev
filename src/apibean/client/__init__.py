import httpx

from .engine.agent import Agent
from .engine.curli import Curli
from .engine.space import ApibeanSpace
from .engine.utils import ApibeanUtils

class Store:
    session = ApibeanSpace(profile = "main")
    account = ApibeanSpace(profile = "anon")

store = Store()
curli = Curli(httpx, session_store=store.session, account_store=store.account)
agent = Agent(curli)
utils = ApibeanUtils()

curli.globals(headers={
    "accept": "application/json",
    "Content-Type": "application/json",
})
