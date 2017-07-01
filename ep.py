# -*- coding: utf-8 -*-

def kickAssSwimDetect01(ch1,ch2,thre):

    import numpy as np
    
    print('processing channel data\n')
    ker = np.exp(-(np.arange(-60,61,1,'f4')**2)/(2*(20**2)));
    ker = ker / ker.sum()


    smch1 = np.convolve(ch1,ker,'same');
    pow1 = (ch1 - smch1)**2;
    fltCh1 = np.convolve(pow1,ker,'same');

    smch2 = np.convolve(ch2,ker,'same');
    pow2 = (ch2 - smch2)**2;
    fltCh2 = np.convolve(pow2,ker,'same');
    


    aa1 = np.diff(fltCh1);
    peaksT1 = (aa1[0:-1] > 0) * (aa1[1:] < 0);
    peaksIndT1 = np.argwhere(peaksT1>0).squeeze();

    aa2 = np.diff(fltCh2);
    peaksT2 = (aa2[0:-1] > 0) * (aa2[1:] < 0);
    peaksIndT2 = np.argwhere(peaksT2>0).squeeze();


    x_ = np.arange(0,0.10001,0.00001);  
    th1 = np.zeros(fltCh1.size,);
    th2 = np.zeros(fltCh2.size,);
    back1 = np.zeros(fltCh1.size,);
    back2= np.zeros(fltCh2.size,);

    if (len(ch1)<360000):
        d_=6000*1
    else:
        d_ = 6000*60;   #% 5 minutes threshold window

    last_i=0
    
    for i in np.arange(0,fltCh1.size-d_,d_):
        peaksIndT1_ = np.argwhere(peaksT1[0:(i+d_)]>0).squeeze();
        peaksIndT2_ = np.argwhere(peaksT2[0:(i+d_)]>0).squeeze();
        
        a1,_ = np.histogram(fltCh1[peaksIndT1_], x_)
        a2,_ = np.histogram(fltCh2[peaksIndT2_], x_)
        
        a1=a1.astype('f4')
        a2=a2.astype('f4')
        
        mx1 = (np.argwhere(a1 == a1.max())).min()
        mn1_ind=np.argwhere(a1[0:mx1] < (a1[mx1]/200))
        if (mn1_ind.size>0):
            mn1=mn1_ind.max()
        else:
            mn1=0;
        mx2 = (np.argwhere(a2 == a2.max())).min();
        mn2_ind=np.argwhere(a2[0:mx2] < (a2[mx2]/200))
        if (mn2_ind.size>0):
            mn2=mn2_ind.max()
        else:
            mn2=0;

        th1[i:(i+d_+1)] = x_[mx1] + thre*(x_[mx1]-x_[mn1]);
        th2[i:(i+d_+1)] = x_[mx2] + thre*(x_[mx2]-x_[mn2]);
        back1[i:(i+d_+1)] = x_[mx1] ;
        back2[i:(i+d_+1)] = x_[mx2] ;
              
        last_i=i

    th1[(last_i+d_+1):] = th1[last_i+d_];
    th2[(last_i+d_+1):] = th2[last_i+d_];
    back1[(last_i+d_+1):] = back1[last_i+d_] ;
    back2[(last_i+d_+1):] = back2[last_i+d_] ;


    print('\nAssigning bursts and swims\n');
    
    burstIndT1 = peaksIndT1[np.argwhere((fltCh1-th1)[peaksIndT1]>0).squeeze()];
    burstT1=np.zeros(fltCh1.size);
    burstT1[burstIndT1]=1;

    burstIndT2 = peaksIndT2[np.argwhere((fltCh2-th2)[peaksIndT2]>0).squeeze()];
    burstT2=np.zeros(fltCh1.size);
    burstT2[burstIndT2]=1;

    burstBothT = np.zeros(fltCh1.size);
    burstBothT[burstIndT1] = 1;
    burstBothT[burstIndT2] = 2;

    burstBothIndT = np.argwhere(burstBothT>0).squeeze();

    interSwims = np.diff(burstBothIndT);
    
    swimEndIndB = np.argwhere(interSwims > 600).squeeze();
    
    swimEndIndB = np.append(swimEndIndB,burstBothIndT.size-1)    
    
    swimStartIndB=0;
    swimStartIndB = np.append(swimStartIndB,swimEndIndB[:-1]+1); 
    nonSuperShort = np.argwhere(swimEndIndB != swimStartIndB).squeeze();
    
    swimEndIndB = swimEndIndB[nonSuperShort];
    swimStartIndB = swimStartIndB[nonSuperShort];

    # swimStartIndB is an index for burstBothIndT
    # burstBothIndT is an idex for time

    swimStartIndT = burstBothIndT[swimStartIndB];
    swimStartT = np.zeros(fltCh1.size);
    swimStartT[swimStartIndT] = 1;

    swimEndIndT = burstBothIndT[swimEndIndB];
    swimEndT = np.zeros(fltCh1.size);
    swimEndT[swimEndIndT] = 1;

    swimdata=dict();
    swimdata['fltCh1']=fltCh1.astype('f4')
    swimdata['fltCh2']=fltCh2.astype('f4')
    swimdata['back1']=back1.astype('f4')
    swimdata['back2']=back2.astype('f4')
    swimdata['th1']=th1.astype('f4')
    swimdata['th2']=th2.astype('f4')
    swimdata['burstBothT']=burstBothT
    swimdata['burstBothIndT']=burstBothIndT
    swimdata['burstIndT1']= burstIndT1
    swimdata['burstIndT2']= burstIndT2
    swimdata['swimStartIndB']= swimStartIndB
    swimdata['swimEndIndB']= swimEndIndB
    swimdata['swimStartIndT']= swimStartIndT
    swimdata['swimEndIndT']= swimEndIndT
    swimdata['swimStartT']= swimStartT
    swimdata['swimEndT']= swimEndT

    return swimdata



def create_stim_blocks(stimParam5):

    import numpy as np
    
    blocks=np.zeros([2,stimParam5.size]);
    blocknum=1;

    stimParam5[0:49]=0;

    for i in np.arange(1,np.floor(stimParam5.max())):

        startInd = np.argwhere(stimParam5 == i).min();
        endInd   = np.argwhere(stimParam5 == i).max();
        blocks[0,startInd:endInd+1]=blocknum;
        blocknum=blocknum+1;


    blocks[1,np.argwhere(blocks[0,]==0).squeeze()]=1;

    return blocks.astype('f4'), stimParam5


def calc_blockpowers(swimdata,blocklist):
    import numpy as np

    totblock=int(blocklist.max());

    fltData1=swimdata['fltCh1'];
    fltData2=swimdata['fltCh2'];
    backData1=swimdata['back1'];
    backData2=swimdata['back2'];
    
    StartIndT=swimdata['swimStartIndT'];
    EndIndT=swimdata['swimEndIndT'];

    blockpowers=np.zeros([3,totblock]);

    for ii in np.arange(0,StartIndT.size):
        
        pspan=np.arange(StartIndT[ii],EndIndT[ii]+1);

        spower1=fltData1[pspan].sum()-backData1[pspan].sum()                          
        spower2=fltData2[pspan].sum()-backData2[pspan].sum()
                        
        if spower1<0:
            spower1=0
        if spower2<0:
            spower2=0
       
        P=spower1+spower2;
        
        nblock=int(blocklist[0,StartIndT[ii]]-1);

        if(nblock>=0):
            blockpowers[0,nblock] = blockpowers[0,nblock] +spower1;
            blockpowers[1,nblock] = blockpowers[1,nblock] +spower2;
            blockpowers[2,nblock] = blockpowers[2,nblock] +P;
            
    
    return blockpowers

