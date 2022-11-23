import numpy as np
import matplotlib.pyplot as plt
from lmfit import Model, Parameters
import pandas as pd

def lmfit_lin(x,y,fitParams):

    def myFunction(x,m,c):
        return m*x + c

    gmodel = Model(myFunction)
    params = Parameters()
    # add with tuples: (NAME  VALUE VARY MIN  MAX  EXPR  BRUTE_STEP)
    params.add_many(('m', fitParams[0], True, None,None, None, None),

                    ('c', fitParams[1], True, None, None, None, None),
                    )

    lin_result = gmodel.fit(y, params, x=x)

    m = lin_result.params['m']
    c = lin_result.params['c']

    newX = np.linspace(min(x),max(x),1000)
    fitShift = myFunction(newX,m,c)

    return lin_result,newX,fitShift


units  = [1e-3,1e-3,1e-6,1e-6,1e-6,1e-9]
fnames = ['63mW','6.3mW','630uW','63uW','6.3uW','630nW']


ms   = np.zeros(len(fnames))
cs   = np.zeros(len(fnames))
merr = np.zeros(len(fnames))
cerr = np.zeros(len(fnames))


fig,ax = plt.subplots(2,3)

for i in range(len(fnames)):
    data = np.genfromtxt(
        fnames[i] + ".csv",
        delimiter=',',
        skip_header=2)

    x = data[:,0]*units[i]*1e+3
    y = data[:,1]



    if i <= 2:
        j = 0
    elif i>2:
        j = 1

    ax[j,i%3].plot(x,y,'o')

    result,newX,newY = lmfit_lin(x,y,[1,0])
    ax[j,i%3].plot(newX,newY)

    ms[i] = result.params['m'].value
    cs[i] = result.params['c'].value

    merr[i] = result.params['m'].stderr
    cerr[i] = result.params['c'].stderr



data = {
    "Sensitivity":fnames,
    "m":np.round(ms,decimals=3),
    "mError":np.round(merr,decimals=4),
    "c":np.round(cs,decimals=4),
    "cError":np.round(cerr,decimals=5)
    }


df = pd.DataFrame(data)

print(df)


df.to_latex("Table.tex",index=False,escape=False,na_rep='')


plt.show()
