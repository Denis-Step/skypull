import skypull

skyBox = skypull.SkyGrab()

s = skyBox.get_inventory({'eventKeywords': ['cancelled']})
print(s)