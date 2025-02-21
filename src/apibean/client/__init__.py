import httpx

from .engine.curli import Curli
from .engine.space import ApibeanSpace
from .engine.utils import ApibeanUtils

session_store = ApibeanSpace()
account_store = ApibeanSpace()
curli = Curli(httpx, session_store=session_store, account_store=account_store)
utils = ApibeanUtils()

box = session_store
