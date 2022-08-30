from datetime import datetime
from datetime import date
from enum import Enum

class TradeStatus(Enum):
    ACCEPTED = '1' 
    PENDING =  '2' 
    REJECTED = '0'



answer = round(6.4456, 2)

print(TradeStatus.ACCEPTED.value)
print(answer)