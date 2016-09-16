from tasks import add

result = add.delay(4, 12)
print(result.get())
