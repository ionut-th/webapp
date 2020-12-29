
from  sqlalchemy import *


# Object that holds collection of Tables, optional db binding
meta = MetaData()


users = Table(
   'users', meta, 
   Column('id', Integer, primary_key = True), 
   Column('name', String), 
   Column('hash', String), 
)

