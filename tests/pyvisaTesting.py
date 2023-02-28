import pyvisa

rm = pyvisa.ResourceManager()

ls = rm.list_resources()

with open("Output.txt", "w") as text_file:
    for item in ls: 
        text_file.write(str(ls) + "\n")




