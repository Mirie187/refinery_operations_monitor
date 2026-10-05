"""import datetime as dt
import random
import time
temperature = 467
for i in range(5):
 change = random.randint(-10,10)
 temperature += change
 print(f"{dt.datetime.now()} | Temperature: {temperature}°C | Change: {change}°C")
 time.sleep(10)
"""
import time
import random 
temperature = 25
for i in range (10):
    change = random.randint(-2,2)
    temperature = temperature + change
    print(f"Temperature: {temperature}°C | Change: {change}°C")