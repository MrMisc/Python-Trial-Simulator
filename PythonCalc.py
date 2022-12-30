import csv
import seaborn as sns
import numpy as np
import random 
import matplotlib.pyplot as plt
import time

def pitychaintilldeathm(lastroll, faith, stringthing): #with pity system - 2 fails in a row leads to one auto success | NEW:lastroll is option to retain information from previous roll to start from where you ended off from previous attempt!!!!
    def roll(massDist):
        randRoll = random.random() # in [0,1]
        summ = 0
        result = True
        for mass in massDist:
            summ += mass
            if randRoll < summ:
                return result
            else:
                return False
    level=1
    string = ' '
    RETARDED = []
    Prices = []
    for i in stringthing.split(" "):
        i, iprice = i.split("|")
        if '*' in str(i):
            RETARDED.append(float(i[:-1]))
        else:
            RETARDED.append(float(i))
        Prices.append(float(iprice))
    # print(len(RETARDED))
    #print(RETARDED)
    #print(RETARDED[level])
    #print(1-RETARDED[level])
    count = 1
    bottom = 0
    #Lets try to establish which arguments are critical points at which falling below is not possible - for now I think it is reasonable to expect that the critical points
    #behave exactly like the first level that we provide
    #First - let's try to extract and 'look for' critical points denoted by * after the probability values
    criticalno = []
    for i in range(len(stringthing)):
        if '*' in str(stringthing[i]):
            criticalno.append(i+1)   
    failedatcheckpoint = False  #To record if failure at checkpoint occurred in last roll - because if you fail once alr at a checkpoint, you CANNOT be given pity rank up if you fail at it again   
    mesos = 0        


    while count<int(faith)+1 and level+lastroll<len(stringthing.split(" "))+1:
        print(level-1+lastroll)
        print("VS")
        print(len(RETARDED))
        sampleMassDist = (RETARDED[level-1+lastroll],1-RETARDED[level-1+lastroll])
        t = roll(sampleMassDist) #do the roll
        mesos += Prices[level-1+lastroll]
        count+=1
        string+=str(t)+' '
        if t:
            level+=1
            failedatcheckpoint = False
        elif string.split(' ')[-1] == 'False' and failedatcheckpoint == False:
            level-=0 #just to indicate that you failed AND succeeded because of pity rank up right after at 100%
            string+='False True '
            count+=1  #even though you get a free success after this second consecutive False, it counts as another roll
            failedatcheckpoint = False
        elif len(criticalno) > 0:
            for i in criticalno:
                if level + lastroll == i:  #If you are at one of the critical points, you will not fail.
                    failedatcheckpoint = True
                    bottom += 1
        elif level+lastroll>1:  #Catch all term for dropping a level if no check point was triggered in previous if statement
            level-=1
            failedatcheckpoint = False
        elif level+lastroll==1: #This is supposed to be right at the bottom
            bottom+=1
            failedatcheckpoint = True
    return [string, bottom, mesos, level+lastroll==len(RETARDED)]




def SFm(ctx,trials, faith, *args):  #helps to loop through the tries. This is for batches UNTIL success
    SUCCESSWEWANT = len(args)
    faith = abs(int(faith))
    faith = max(len(args),faith)
    def TrueCount(stringie, lastround):
        final = False
        n = len([x for x in stringie.split(' ') if x == 'False'])
        if len([x for x in stringie.split(' ') if x == 'True']) - len([x for x in stringie.split(' ') if x == 'False']) +int(lastround) == SUCCESSWEWANT:
            final = True
        return [final,n]
    data = []  #Number of tries it took until we got a success and stopped the trial
    N=[]  #Number of falses for the last successful set of attempts per trial
    NAve=[]  #Average number of falses and max for the entire set of attempts per trial: [Average,Maximum]
    NSum = []
    NStat = []
    tapdata = []
    Meso = []
    for i in range(int(trials)):
        mesospertrial = 0
        tapdata_count = 0
        nall = []
        count = 1
        lasttime = 0
        checkthis, BOTTOM, meso = pitychaintilldeathm(lasttime, faith, *args) #first run - BOTTOM is the number of times one failed at a critical point which is not to be counted in the overall number of levels progressed
        #per session!
        mesospertrial += meso
        # print(checkthis) #print the string of results for the first batch of runs
        nall.append(TrueCount(checkthis, lasttime)[1])
        tapdata_count += len(checkthis.split(" "))
        finalcheck = ""
        while TrueCount(checkthis, lasttime)[0] == False:
            #print(count)
            count += 1
            lasttime += len([x for x in checkthis.split(' ') if x == 'True']) - len([x for x in checkthis.split(' ') if x == 'False'])+BOTTOM  #Update the trial number you previously were at!!!
            lasttime = max(lasttime,0)
            # print(lasttime)
            finalcheck = checkthis
            checkthis, BOTTOM, mesos = pitychaintilldeathm(lasttime, faith, *args)          
            mesospertrial += mesos
            nall.append(TrueCount(checkthis, lasttime)[1])
            tapdata_count += len(checkthis.split(" "))
            #print(checkthis)
        tapdata.append(tapdata_count)
        data.append(count)
        Meso.append(round(mesospertrial, 1))
        # print(f"{checkthis} is the final set of true and falses obtained for the last attempt for trial {i}")
        # print(f"Number of fails for trial {i}'s final attempt is {TrueCount(checkthis, lasttime)[1]}")
        N.append(TrueCount(finalcheck, lasttime)[1])
        NStat.append([np.mean(nall), max(nall), sum(nall)])
        NSum.append(sum(nall))
        NAve.append(np.mean(nall))
    #Making copies for the histogram 
    histdata = np.array(np.copy(data))
    histdata2 = np.array(np.copy(data))
    histN = np.array(np.copy(N))
    histNSum= np.array(np.copy(NSum))
    histNAve= np.array(np.copy(NAve))
    __,SortedNAve = (np.array(t) for t in zip(*sorted(zip(histdata, histNAve))))
    __,SortedNSum = (np.array(t) for t in zip(*sorted(zip(histdata, histNSum))))
    histdata = sorted(histdata)
    rate = 0.6
    d = max(histdata)/(int(int(trials)**rate)) #bin ranges of attempts
    print(f"Rate is {d}")
    P = []
    for i in range(int(int(trials)**rate)):
        try:
            #y = max([histdata.index(x) for x in histdata if x<=d*(i+1) if x>d*(i)])
            #print(i)
            #print(d*(i))
            y = np.max(np.where(np.logical_and(histdata>d*(i), histdata<=d*(i+1))))
            #y1 = min([histdata.index(x) for x in histdata if x<=d*(i+1) if x>d*(i)])
            y1 = np.min(np.where(np.logical_and(histdata>d*(i), histdata<=d*(i+1))))
            print(y1,y)
            perbin = [[SortedNAve[x], SortedNSum[x]] for x in range(int(y1),int(y))]
            avg_min = min([x[0] for x in perbin])
            avg_max = max([x[0] for x in perbin])
            total_min = min([x[1] for x in perbin])
            total_max = max([x[1] for x in perbin])
            P.append([avg_min, avg_max,total_min,total_max])
        except:
            pass
        #print(perbin)
        
    x = np.linspace(1,int(trials),int(trials))
    plt.clf()
    fig = plt.figure()
    plt.style.use('fivethirtyeight') 
    plt.figure(figsize=(20,10))
    plt.xlim(0,max(data))
    plt.xlabel("No. of attempts")
    plt.ylabel("Density")
    plt.title("Attempts distribution prior to success - Failures annotated")
    splot = sns.distplot(data, hist=True, kde=True, 
             bins=int(int(trials)**rate), 
             kde_kws={'linewidth': 4})
    labelno = 0
    for p in splot.patches:
        try:
            splot.annotate(f"Average \n {P[labelno][0]:.2f} - {P[labelno][1]:.2f} \n Total  \n {P[labelno][2]} - {P[labelno][3]}",
                       (p.get_x() + p.get_width() / 2., p.get_height()),
                       ha='center', va='center',
                       xytext=(0, 9),
                       textcoords='offset points', set_fontsize = 80)
        except:
            pass
        labelno += 1
    plt.savefig(fname='plot2')
    plt.style.use("seaborn-dark")
    plt.clf()
    plt.figure(figsize=(20,10))
    for param in ['figure.facecolor', 'axes.facecolor', 'savefig.facecolor']:
        plt.rcParams[param] = '#212946'  # bluish dark grey
    for param in ['text.color', 'axes.labelcolor', 'xtick.color', 'ytick.color']:
        plt.rcParams[param] = '0.9'  # very light grey
    plt.grid(color='#2A3459')
    # colors = random.choice(['#99fcff', '#fb53fe', "#FFE74C", "#FFFFFF", "#6BF178", "#BF0603", "#35A7FF", "#8447FF", "#D972FF", "#F6F930", "#D2F898", "#FCFCFC", "#ED4D6E", "#E9D6EC", "#59A96A", "#9BDEAC", "#B4E7CE", "#4392F1", "#61E786", "#E3EBFF", "#38369A", "#020887"])
    colors = random.choice(["#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)])for i in range(200)])
    MARK = random.choice([".", ",", "o", "v", "^", "<", ">", "1", "2", "3", "4", "8", "s", "p", "P", "*", "h", "H", "+", "x", "X", "d", "D", "|", "_"])
    linestyle_tuple = [
     ((0, (1, 10))),
     ((0, (1, 1))),
     ((0, (1, 1))),
     ((0, (5, 10))),
     ((0, (5, 5))),
     ((0, (5, 1))),
     ((0, (3, 10, 1, 10))),
     ((0, (3, 5, 1, 5))),
     ((0, (3, 1, 1, 1))),
     ((0, (3, 5, 1, 5, 1, 5))),
     ((0, (3, 10, 1, 10, 1, 10))),
     ((0, (3, 1, 1, 1, 1, 1)))]
    plt.plot(x, data, color = colors, marker = MARK, linestyle = random.choice(linestyle_tuple))
    if int(trials)<300:
        print(N)
        COMB = [str(Meso[i]) +" u"+ "\n" + str(N[i]) +"\n"+ "["+str(int(NStat[i][0]))+"/" + str(NStat[i][1]) +"/" + str(NStat[i][2]) + "]" for i in range(len(N))] #something wrong with N[i] currently
        for i,txt in enumerate(COMB):
            text = plt.annotate(txt, (x[i],data[i]))
            text.set_fontsize(8)
    plt.xlabel("Trials (separate) from start point")
    plt.ylabel("No of attempts until success")
    plt.title(f"{ctx.message.author}\'s starforce simulation - with pity sys.: {faith} attempts,{trials} times")
    plt.savefig(fname='plot')



def sim(trials, faith, stringthing):  #SFm without the plotting. Checking for time against Rust equivalent 
    SUCCESSWEWANT = len(stringthing)
    faith = abs(int(faith))
    faith = max(len(stringthing),faith)
    def TrueCount(stringie, lastround):
        final = False
        n = len([x for x in stringie.split(' ') if x == 'False'])
        if len([x for x in stringie.split(' ') if x == 'True']) - len([x for x in stringie.split(' ') if x == 'False']) +int(lastround) == SUCCESSWEWANT:
            final = True
        return [final,n]
    data = []  #Number of tries it took until we got a success and stopped the trial
    N=[]  #Number of falses for the last successful set of attempts per trial
    NAve=[]  #Average number of falses and max for the entire set of attempts per trial: [Average,Maximum]
    NSum = []
    NStat = []
    tapdata = []
    Meso = []
    for i in range(int(trials)):
        mesospertrial = 0
        tapdata_count = 0
        nall = []
        count = 1
        lasttime = 0
        checkthis, BOTTOM, meso, state = pitychaintilldeathm(lasttime, faith, stringthing) #first run - BOTTOM is the number of times one failed at a critical point which is not to be counted in the overall number of levels progressed
        #per session!
        mesospertrial += meso
        # print(checkthis) #print the string of results for the first batch of runs
        nall.append(TrueCount(checkthis, lasttime)[1])
        tapdata_count += len(checkthis.split(" "))
        finalcheck = ""
        while state:
            #print(count)
            print("We have entered the whilest of while loops")
            count += 1
            lasttime += len([x for x in checkthis.split(' ') if x == 'True']) - len([x for x in checkthis.split(' ') if x == 'False'])+BOTTOM  #Update the trial number you previously were at!!!
            lasttime = max(lasttime,0)
            # print(lasttime)
            finalcheck = checkthis
            checkthis, BOTTOM, mesos, state = pitychaintilldeathm(lasttime, faith, stringthing)          
            mesospertrial += mesos
            nall.append(TrueCount(checkthis, lasttime)[1])
            tapdata_count += len(checkthis.split(" "))
            #print(checkthis)
        tapdata.append(tapdata_count)
        data.append(count)
        Meso.append(round(mesospertrial, 1))
        # print(f"{checkthis} is the final set of true and falses obtained for the last attempt for trial {i}")
        # print(f"Number of fails for trial {i}'s final attempt is {TrueCount(checkthis, lasttime)[1]}")
        N.append(TrueCount(finalcheck, lasttime)[1])
        NStat.append([np.mean(nall), max(nall), sum(nall)])
        NSum.append(sum(nall))
        NAve.append(np.mean(nall))


#Uncomment for normal method 1 simulation block. Adjust NO accordingly for number of trials

# st = time.time()
# NO = list(range(10,110,10))+list(range(150,1050, 50)) + list(range(2000, 11000, 1000))+ list(range(20000,110000,10000))
# print(NO[0])
# data = []
# for i in NO:
#     sim(i, 5, "0.5|0.0045 0.45|0.00563 0.4|0.00698 0.35|0.00853 0.3|0.01028 0.3*|0.0318 0.3|0.03746 0.3135|0.04371 0.3135|0.05517 0.3135|0.06337 0.3135*|0.07952")


#     et = time.time()
#     elapsed_time = et - st
#     print('Execution time:', elapsed_time, 'seconds')


#     data.append([i, elapsed_time])
# with open('times.csv', 'w') as f:
#     writer = csv.writer(f)
#     writer.writerows(data)




def pitychaintilldeath0m(lastroll, faith, stringthing): #with pity system - 2 fails in a row leads to one auto success | NEW:lastroll is option to retain information from previous roll to start from where you ended off from previous attempt!!!! 100% false dependent.
    def roll(massDist):
        randRoll = random.random() # in [0,1]
        summ = 0
        result = True
        for mass in massDist:
            summ += mass
            if randRoll < summ:
                return result
            else:
                return False
    def countFalses(stringie):
        cunt = 0
        for i in stringie.split(' '):
            if i == 'False':cunt+=1
            else:pass
        return cunt
    level=1
    string = ' '
    #RETARDED = [float(x) for x in args]
    RETARDED = []
    Prices = []
    for i in stringthing.split(" "):
        i, iprice = i.split("|")
        if '*' in str(i):
            RETARDED.append(float(i[:-1]))
        else:
            RETARDED.append(float(i))
        Prices.append(float(iprice))
    print(len(RETARDED))
    #print(RETARDED)
    #print(RETARDED[level])
    #print(1-RETARDED[level])
    count = 1
    bottom =0 #Number of times failed at bottom
    #Lets try to establish which arguments are critical points at which falling below is not possible - for now I think it is reasonable to expect that the critical points
    #behave exactly like the first level that we provide
    #First - let's try to extract and 'look for' critical points denoted by * after the probability values
    criticalno = []
    for i in range(len(stringthing.split(" "))):
        if '*' in str(stringthing[i]):
            criticalno.append(i+1)     
    failedatcheckpoint = False  #To record if failure at checkpoint occurred in last roll - because if you fail once alr at a checkpoint, you CANNOT be given pity rank up if you fail at it again     
    mesos = 0       
    while countFalses(string) < int(faith) and level+lastroll<len(RETARDED)+1:
        print(f"level + lastroll is {level+lastroll} ")
        print("while...")
        print(f"Length of retarded is {len(RETARDED)}")
        sampleMassDist = (RETARDED[level-1+lastroll],1-RETARDED[level-1+lastroll])
        t = roll(sampleMassDist)
        mesos += Prices[level-1+lastroll]
        count+=1
        string+=str(t)+' '           
        if t:
            level+=1
            failedatcheckpoint = False
        elif string.split(' ')[-1] == 'False' and failedatcheckpoint == False:
            level-=0
            string+='False True '
            count+=1
            failedatcheckpoint = False
        elif len(criticalno) > 0:
            for i in criticalno:
                if level + lastroll == i:  #If you are at one of the critical points, you will not fail.
                    failedatcheckpoint = True
                    bottom += 1            
        elif level+lastroll>1:
            level-=1
            failedatcheckpoint = False
        else:
            bottom+=1
            failedatcheckpoint = True
    return [string, bottom, mesos, int(level+lastroll)<int(len(RETARDED))]





def SFIm(trials, faith, stringthing):  #helps to loop through the tries. This is for batches UNTIL success. HOWEVER, THIS TIME THIS IS FAILURE SAFED INSTEAD. WE SHALL TRY TO CAP BASED OFF OF TOTAL NUMBER OF FAILURES PER SESSION - FAITH.Impulsive tapping. dependent on number of falses
    SUCCESSWEWANT = len(stringthing.split(" "))
    faith = abs(int(faith))
    # faith = max(len(args),faith)  You do not do this for the impulsive run!!!
    def TrueCount(stringie, lastround):
        final = False
        n = len([x for x in stringie.split(' ') if x == 'False'])
        if len([x for x in stringie.split(' ') if x == 'True']) - len([x for x in stringie.split(' ') if x == 'False']) +int(lastround) == SUCCESSWEWANT:
            final = True
        return [final,n]
    data = []  #Number of tries it took until we got a success and stopped the trial
    N=[]  #Number of falses for the last successful set of attempts per trial
    NAve=[]  #Average number of falses and max for the entire set of attempts per trial: [Average,Maximum]
    NSum = []
    NStat = []
    Meso = []
    for i in range(int(trials)):
        mesospertrial = 0
        nall = []
        count = 1
        lasttime = 0
        checkthis, BOTTOM, meso, state = pitychaintilldeath0m(lasttime, faith, stringthing) #first run
        mesospertrial+=meso
        print(checkthis) #print the string of results for the first batch of runs
        nall.append(TrueCount(checkthis, lasttime)[1])
        finalcheck = ""
        while state:
            #print(count)
            count += 1
            lasttime += len([x for x in checkthis.split(' ') if x == 'True']) - len([x for x in checkthis.split(' ') if x == 'False'])+BOTTOM  #Update the trial number you previously were at!!!
            lasttime = max(lasttime,0)
            print(lasttime)
            finalcheck=checkthis
            checkthis, BOTTOM, mesos, state = pitychaintilldeath0m(lasttime, faith, stringthing)
            mesospertrial+=mesos
            nall.append(TrueCount(checkthis, lasttime)[1])
            print(f"State is {state}")
            #print(checkthis)
        print(f"State is now.. {state}")
        print(f"It took {count} sessions, with {mesospertrial}")
        data.append(count)
        Meso.append(round(mesospertrial, 1))
        N.append(TrueCount(finalcheck, lasttime)[1])
        NStat.append([np.mean(nall), max(nall), sum(nall)])
        NSum.append(sum(nall))
        NAve.append(np.mean(nall))    
    #Making copies for the histogram 
    histdata = np.array(np.copy(data))
    histdata2 = np.array(np.copy(data))
    histN = np.array(np.copy(N))
    histNSum= np.array(np.copy(NSum))
    histNAve= np.array(np.copy(NAve))
    __,SortedNAve = (np.array(t) for t in zip(*sorted(zip(histdata, histNAve))))
    __,SortedNSum = (np.array(t) for t in zip(*sorted(zip(histdata, histNSum))))
    histdata = sorted(histdata)
    rate = 0.6
    d = max(histdata)/(int(int(trials)**rate)) #bin ranges of attempts
    print(f"Rate is {d}")
    P = []
    for i in range(int(int(trials)**rate)):
        try:
            #y = max([histdata.index(x) for x in histdata if x<=d*(i+1) if x>d*(i)])
            #print(i)
            #print(d*(i))
            y = np.max(np.where(np.logical_and(histdata>d*(i), histdata<=d*(i+1))))
            #y1 = min([histdata.index(x) for x in histdata if x<=d*(i+1) if x>d*(i)])
            y1 = np.min(np.where(np.logical_and(histdata>d*(i), histdata<=d*(i+1))))
            print(y1,y)
            perbin = [[SortedNAve[x], SortedNSum[x]] for x in range(int(y1),int(y))]
            avg_min = min([x[0] for x in perbin])
            avg_max = max([x[0] for x in perbin])
            total_min = min([x[1] for x in perbin])
            total_max = max([x[1] for x in perbin])
            P.append([avg_min, avg_max,total_min,total_max])
        except:
            pass
        #print(perbin)
        
    x = np.linspace(1,int(trials),int(trials))        
    return None




st = time.time()
NO = list(range(10,110,10))+list(range(150,1050, 50)) + list(range(2000, 11000, 1000))
print(NO[0])
data = []
for i in NO:
    SFIm(i, 10, "0.5|0.0045 0.45|0.00563 0.4|0.00698 0.35|0.00853 0.3|0.01028 0.3*|0.0318 0.3|0.03746 0.3135|0.04371 0.3135|0.05517 0.3135|0.06337 0.3135*|0.07952")


    et = time.time()
    elapsed_time = et - st
    print('Execution time:', elapsed_time, 'seconds')


    data.append([i, elapsed_time])
with open('times2.csv', 'w') as f:
    writer = csv.writer(f)
    writer.writerows(data)