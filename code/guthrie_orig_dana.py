from guthrie_modelc import *
from display import *

# Trial duration
duration = 3012.0*millisecond
# Default Time resolution
dt = 1.0*millisecond

numOfCues = 4

popCTX = numOfCues*popPerCueCTX
popSTR = numOfCues*popPerCueSTR

CTX_GUASSIAN_INPUT = getNormal(popPerCueCTX)
CTX_GUASSIAN_INPUT_2D = get2DNormal(popPerCueCTX, popPerCueCTX)

CTX = AssociativeStructure("CTX", pop=numOfCues*popPerCueCTX)
STR = AssociativeStructure("STR", pop=numOfCues*popPerCueSTR)
STN = Structure("STN")
GPI = Structure("GPI")
THL = Structure("THL")

OneToOne(CTX.cog('Z'), STR.cog('Isyn'), 1.0, clipWeights=True)
OneToOne(CTX.mot('Z'), STR.mot('Isyn'), 1.0, clipWeights=True)
OneToOne(CTX.ass('Z'), STR.ass('Isyn'), 1.0, clipWeights=True) 
CogToAss(CTX.cog('Z'), STR.ass('Isyn'), gain=+0.2, clipWeights=True)
MotToAss(CTX.mot('Z'), STR.ass('Isyn'), gain=+0.2, clipWeights=True)
OneToOne(CTX.cog('Z'), STN.cog('Isyn'), 1.0) 
OneToOne(CTX.mot('Z'), STN.mot('Isyn'), 1.0)
OneToOne(STR.cog('Z'), GPI.cog('Isyn'), -2.0) 
OneToOne(STR.mot('Z'), GPI.mot('Isyn'), -2.0)
AssToCog(STR.ass('Z'), GPI.cog('Isyn'), gain=-2.0)
AssToMot(STR.ass('Z'), GPI.mot('Isyn'), gain=-2.0)
OneToAll(STN.cog('U'), GPI.cog('Isyn'), gain=+1.0 )
OneToAll(STN.mot('U'), GPI.mot('Isyn'), gain=+1.0 )
OneToOne(GPI.cog('U'), THL.cog('Isyn'), -0.5) 
OneToOne(GPI.mot('U'), THL.mot('Isyn'), -0.5)
OneToOne(THL.cog('U'), CTX.cog('Isyn'), +1.0) 
OneToOne(THL.mot('U'), CTX.mot('Isyn'), +1.0)
OneToOne(CTX.cog('Z'), THL.cog('Isyn'), 0.4) 
OneToOne(CTX.mot('Z'), THL.mot('Isyn'), 0.4)

dtype = [ ("CTX", [("mot", float, numOfCues), ("cog", float, numOfCues), ("ass", float, numOfCues*numOfCues)]),
          ("STR", [("mot", float, numOfCues), ("cog", float, numOfCues), ("ass", float, numOfCues*numOfCues)]),
          ("GPI", [("mot", float, 4), ("cog", float, 4)]),
          ("THL", [("mot", float, 4), ("cog", float, 4)]),
          ("STN", [("mot", float, 4), ("cog", float, 4)])]

history = np.zeros(duration*1000, dtype)

def reset():
    clock.reset()
    for group in network.__default_network__._groups:
        group['U'] = 0
        group['V'] = 0
        group['Isyn'] = 0
    CTX.cog['Iext'] = 0
    CTX.mot['Iext'] = 0
    CTX.ass['Iext'] = 0

def getExtInput():
    v = 18 
    noise = 0.01
    return (CTX_GUASSIAN_INPUT )*(np.random.normal(v,noise)) 
#+  np.random.normal(0,noise)

def get2DExtInput():
    v = 18 
    noise = 0.01
    return (CTX_GUASSIAN_INPUT_2D)*(np.random.normal(v,noise)) 
#+ np.random.normal(0,v*noise)

@clock.at(500*millisecond)
def set_trial(t):
    c1,c2 = 0,1 
    m1,m2 = 0,1
    cp1, cp2 = c1 * popPerCueCTX, c2 * popPerCueCTX
    mp1, mp2 = m1 * popPerCueCTX, m2 * popPerCueCTX
    CTX.cog['Iext'] = 0
    CTX.mot['Iext'] = 0
    CTX.ass['Iext'] = 0
    CTX.cog['Iext'][cp1:cp1+popPerCueCTX] = getExtInput()
    CTX.cog['Iext'][cp2:cp2+popPerCueCTX] = getExtInput()
    CTX.mot['Iext'][mp1:mp1+popPerCueCTX] = getExtInput()
    CTX.mot['Iext'][mp2:mp2+popPerCueCTX] = getExtInput()
    CTX.ass['Iext'][cp1:cp1+popPerCueCTX,mp1:mp1+popPerCueCTX] = get2DExtInput()
    CTX.ass['Iext'][cp2:cp2+popPerCueCTX,mp2:mp2+popPerCueCTX] = get2DExtInput()


def print_act(t):
    print "%d CTX V %s" % (t*1000, sumActivity(CTX.mot['V']))
    print "%d CTX Isyn %s" % (t*1000, sumActivity(CTX.mot['Isyn']))
    print "%d CTX U %s" % (t*1000, sumActivity(CTX.mot['U']))
    print "%d STR Isyn %s" %(t*1000, sumActivity(STR.mot['Isyn']))
    #print "%d STR U %s" % (t*1000, sumActivity(STR.mot['U']))

@clock.at(1006*millisecond)
def check_trial(t):
    print_act(t)

@clock.at(511*millisecond)
def check_trial(t):
    print_act(t)

@clock.at(501*millisecond)
def check_trial(t):
    print_act(t)



@clock.at(2500*millisecond)
def reset_trial(t):
    print sumActivity(CTX.cog['U'])
    print sumActivity(CTX.mot['U'])
    plt.plot(1+np.arange(numOfCues*popPerCueCTX), np.maximum(CTX.mot['U'],0.0))
    CTX.cog['Iext'] = 0
    CTX.mot['Iext'] = 0
    CTX.ass['Iext'] = 0

def meanActivity(population):
    percue = np.reshape(population, (numOfCues, population.size/numOfCues))
    return percue.mean(axis=1)

def sumActivity(population):
    percue = np.reshape(population, (numOfCues, population.size/numOfCues))
    return percue.mean(axis=1)

@after(clock.tick)
def register(t):
    history["CTX"]["cog"][t*1000] = sumActivity(CTX.cog['U'])
    history["CTX"]["mot"][t*1000] = sumActivity(CTX.mot['U'])

reset()
run(time=duration,dt=dt)

display_ctx(history, duration)
