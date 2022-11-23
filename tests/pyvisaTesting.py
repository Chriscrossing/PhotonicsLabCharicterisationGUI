import pyvisa

rm = pyvisa.ResourceManager()

print(rm.list_resources())


for item in rm.list_resources():
    try:
        inst = rm.open_resource(item)
        print(inst.query("*IDN?"))
    except:
        print("nop")

