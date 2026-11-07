from dispytchr.adapters.inbound.http import create_app
from dispytchr.bootstrap import bootstrap

app = create_app(bootstrap())
