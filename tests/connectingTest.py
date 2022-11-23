from ThorlabsPM100 import ThorlabsPM100
import pickle, pyvisa


def connect(self):
    rm = pyvisa.ResourceManager()
    res = rm.list_resources()

    print("printing Res")
    print(res)
    
    #Needs Converting for windows
    Thor = rm.open_resource( [i for i in res if i.startswith('USB0')][0] ) 
    
    self.TLS = rm.open_resource(  [i for i in res if i.startswith('GPIB')][0] )

    self.TLS.write('*cls')
    self.Thor.write('*cls')

    print(self.TLS.query('*IDN?'))
    print(self.Thor.query('*IDN?'))

    self.Thor = ThorlabsPM100(Thor)


rm = pyvisa.ResourceManager()
res = rm.list_resources()

print(res)