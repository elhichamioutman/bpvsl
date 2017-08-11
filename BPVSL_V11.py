from tkinter import *
from tkinter.ttk import *
import xml.etree.ElementTree as etree
from random import uniform
from tkinter.scrolledtext import ScrolledText
import subprocess
import os
s=d=None #s et d sont la source et la destination d'une sequence
D={} # Tous les elements de BPMN
C={} # Coherence de BPMN       
class BPVSL:
    def __init__(self,root):
        root.title("BPVSL-New Process")
        self.style = Style()
        self.style.theme_use("clam")
        self.style.configure('H.TFrame')#, background='cornflowerblue')
        self.style.configure('G.TFrame', background='plum')
        self.style.configure('M.TFrame', background='white')
        self.style.configure('B.TFrame', background='plum')
        self.style.configure('My.TButton', borderwidth=0)#,background='cornflowerblue')
        self.style.configure('A.TButton', font=('',9,'bold'),
                             foreground='gray42',
                             background='gray72')#,background='cornflowerblue')
        self.style.configure('I.TButton', )#,background='cornflowerblue')
        self.style.configure('C.TCanvas', background='#ffffff',bd=1)
        #Frames
        self.FrmHaut()
        self.FrmTabs()
        self.FrmGauche()
        self.FrmMain()
        self.FrmBas()
        #dictionnaire des elt de BPMN
        self.Events={}
        self.Tasks={}
        self.Gateways={}
        self.Sequences={}
        #nbr des elt de BPMN
        self.nbrEvents=0
        self.nbrTasks=0
        self.nbrGateways=0
        self.nbrSequences=0
        self.typBPMN = -1 #type des elt de BPMN:-1:None,0:Event,1:Task,
                          #                      2:Gateway,3:Sequence
        #Dessiner Sequence        
        self.lastX = None
        self.lastY = None
        self.redLine = None
        #fichier xml : si importer self.xml = 1
        self.xml = 0
        self.id = '' #nom d'un elt de BPMN ds un fichier xml
        self.type = '' #type d'un elt de BPMN ds un fichier xml
        #name of xml file to import or export
        self.filenameI = ''
        self.filenameE = None
        self.sa = 0 #variable to save as
        self.p,self.q = 0,0 #variables si menu contextuel est activé
        self.dictID={}#pour supprimer une sequence par le menu contextuel
        self.cl = 0#variable de click afin de .....
        self.spv = StringVar()#variable activation of complex gateways
        self.spvv={}#variable activation of complex gateways
        self.cohe=True #verification coherence variable
        self.LESCHEMINS,self.LESCHEMINSALL=None,None#paths of property
        self.cmdS=''#command Simulate/Reply
    def redmenu(self):
        if self.p == 1 or self.q == 1:
            self.SqMenu.unpost()
            self.ctMenu.unpost()
            self.p,self.q = 0,0
            return 1
        if self.redLine != None:
            return 1
    def passer(self):
        if self.redmenu(): return
        pass
    def quiter(self):
        if self.redmenu(): return
        if self.cl == 0:
            root.destroy()
            return
        if len(self.Events)>=1:
            msg = messagebox.askyesnocancel('Info','Save BPMN?')
            if msg == None : return
            elif msg == True : self.Export()
        root.destroy()
    def new(self):
        if self.redmenu() : return
        if len(self.Events)>=1:
            msg = messagebox.askyesnocancel('Info','Save BPMN?')
            if msg == None : return
            elif msg == True : self.Export()
            self.Clear()
            root.title("BPVSL-New Process")
            if self.filenameI != '':
                self.filenameI = ''
            if self.filenameE != None:
                self.filenameE = None
    def FrmHaut(self):
        self.frmHaut = Frame(root, style='H.TFrame')
        self.btnHaut={0:['New',PhotoImage(file="images/new.gif"),self.new],
                      1:['Open',PhotoImage(file="images/open.gif"),self.Import],
                      2:['Save',PhotoImage(file="images/save.gif"),self.Export],
                      3:['Print',PhotoImage(file="images/print.gif"),self.Imprimer],
                      4:['Exit',PhotoImage(file="images/quiter.gif"),self.quiter],
                      5:['Help',PhotoImage(file="images/help.gif"),self.passer]}     
        for c in self.btnHaut:
            c = Button(self.frmHaut,
                       image=self.btnHaut[c][1],text=self.btnHaut[c][0],compound="left",
                       style='My.TButton',
                       width=6,command=self.btnHaut[c][2])            
            c.pack(side='left', anchor='nw', padx=0, pady=0)            
        self.frmHaut.pack(side=TOP, fill=X)
    def close(self,event):
        self.CheckFrame.destroy()
    def initiRadio1(self,event):
        for i in range(5):
            self.tpG[i].set('')
        visited = self.trTasks1.selection()
        if len(visited) > 1:
            self.tpG[0].config(state='disabled')
            self.vr.set('')
        else:
            self.tpG[0].config(state='!disabled')
    def Check(self):
        if len(self.Events) == 0:
            messagebox.showinfo("Info","Create BPMN!")
            return
        if self.redmenu(): return
        if self.Cohe()==False: return
        self.CheckFrame = Toplevel()
        #self.CheckFrame.resizable(0,0)
        self.CheckFrame.title("Verification")
        self.CheckFrame.bind('<Escape>', self.close)
        w, h = root.winfo_screenwidth()*0.38, root.winfo_screenheight()*0.71
        x11, y11 = root.winfo_screenwidth()*0.3, root.winfo_screenheight()*0.2
        self.CheckFrame.geometry("%dx%d+%d+%d" % (w, h, x11, y11))
        style = Style(self.CheckFrame)
        style.configure('Treeview', rowheight=30,columnwidth=5)
        self.select = {}
        self.trTasks1 = Treeview(self.CheckFrame,height=5)#,show="headings")
        self.trTasks1.bind("<ButtonRelease-1>", self.initiRadio1)
        vsb = Scrollbar(self.CheckFrame,orient="vertical", command=self.trTasks1.yview)
        self.trTasks1.configure(yscrollcommand=vsb.set)
        self.trTasks1.grid(column=1, row=1, sticky='nsew')
        vsb.grid(column=2, row=1, sticky='ns')
        self.trTasks1.bind( "<Button-1>", self.SelecttrTasks1)
        self.trTasks1.heading("#0", text='Tasks Ai')
        self.image_0 = PhotoImage(file ='images/task1.gif')         
        i=0
        for elt in self.Tasks:
            self.trTasks1.insert('',"end", str(i),text=self.Tasks[elt][4],image=self.image_0)
            i+=1
        self.frmTr=Frame(self.CheckFrame,style='I.TButton')#,style='M.TFrame')
        Label(self.frmTr,  border=1, style='I.TButton',
              text = "           Gateways           ",
              font = ('', 9, 'bold')).grid(column=0,columnspan=2,row=0)
        image_1 = PhotoImage(file ='images/sequence11.gif')
        image_2 = PhotoImage(file ='images/gateway11.gif')
        image_3 = PhotoImage(file ='images/gateway22.gif')
        image_4 = PhotoImage(file ='images/gateway33.gif')
        image_5 = PhotoImage(file ='images/gateway44.gif')        
        MODES = [("", "F", image_1),
                 ("", "E", image_2),
                 ("", "I",image_3),
                 ("", "P",image_4),
                 ("", "C",image_5)]
        self.vr = StringVar()
        self.bg=[]
        s = 'normal'
        j=0
        GF = ('A o--> B','A o-- B','A o--o B','A -->o B',
              '...')
        self.tpG,self.GE,self.GI,self.GP,self.GC=[],[],[],[],[]
        for elt in self.Gateways:                    
            if len(self.Gateways[elt][2])==1:
                self.GE.append(self.Gateways[elt][4])
            elif len(self.Gateways[elt][2])==2:
                self.GI.append(self.Gateways[elt][4])
            elif len(self.Gateways[elt][2])==3:
                self.GP.append(self.Gateways[elt][4])
            elif len(self.Gateways[elt][2])==5:
                self.GC.append(self.Gateways[elt][4])
        ss = 'disabled'
        for cmd, mode, img in MODES:
            self.bg.append(Radiobutton(self.frmTr,compound="left",
                            variable=self.vr, value=mode, state=s,
                                       image= img, command=self.radio))
            
            self.bg[j].grid(column=0,row=j+1,sticky='w')
            self.tpG.append(Combobox(self.frmTr ,state=ss,width=10))#,height=4))
            if mode=='F':
                self.tpG[j]['values'] = GF
                self.tpG[j].bind("<<ComboboxSelected>>", self.combo0)
            else:
                if mode == 'E' :
                    self.tpG[j]['values'] = self.GE
                    self.tpG[j].bind("<<ComboboxSelected>>", self.combo1)
                elif mode == 'I' :
                    self.tpG[j]['values'] = self.GI
                    self.tpG[j].bind("<<ComboboxSelected>>", self.combo2)
                elif mode == 'P' :
                    self.tpG[j]['values'] = self.GP
                    self.tpG[j].bind("<<ComboboxSelected>>", self.combo3)
                elif mode == 'C' :
                    self.tpG[j]['values'] = self.GC
                    self.tpG[j].bind("<<ComboboxSelected>>", self.combo4)
            self.tpG[j].grid(column=1,row=j+1,sticky='w')
            j+=1
        self.frmTr.grid(column=3, row=1, sticky='nsew')
        self.trTasks2 = Treeview(self.CheckFrame,height=5)#,show="headings")
        vsb = Scrollbar(self.CheckFrame,orient="vertical", command=self.trTasks2.yview)
        self.trTasks2.configure(yscrollcommand=vsb.set)
        self.trTasks2.grid(column=5, row=1, sticky='nsew')
        vsb.grid(column=6, row=1, sticky='ns')
        self.trTasks2.heading("#0", text='Tasks Bi')
        lbV = Label(self.CheckFrame,text="Property means : ")
        lbV.grid(column=1, row=2, columnspan=6, padx=0,sticky='w')
        self.v = StringVar()
        self.lbVerify = Label(self.CheckFrame,textvariable=self.v)
        self.lbVerify.grid(column=2, row=2, columnspan=5, padx=0,sticky='w')
        self.checkV = IntVar()
        self.checkV.set(0)
        self.chVerify=Checkbutton(self.CheckFrame, text="Formula  : \tf1:",
                                  variable=self.checkV, onvalue=1,
                                  offvalue=0, command=self.chV)
        self.chVerify.grid(column=1, row=3, columnspan=6, padx=0,sticky='w')
        self.txtVerify=Entry(self.CheckFrame,width=48,state='disabled')
        self.txtVerify.grid(column=2, row=3, columnspan=5, padx=0,sticky='w')
        self.btnV=Button(self.CheckFrame,text="    Verify    ",
                         command=self.btnVerify)
        self.btnV.grid(column=2, row=4, columnspan=5,sticky='w')
        self.btnS=Button(self.CheckFrame,text="Simulate/Reply",
                         command=self.btnSimulate,state='disabled')
        self.btnS.grid(column=4, row=4, columnspan=5,sticky='w')
        self.txtResult = ScrolledText(self.CheckFrame)#, height = 20)
        self.txtResult.grid(column=1, row=5, sticky='nsew',columnspan=6)        
        self.CheckFrame.transient(root)
        self.CheckFrame.update_idletasks()
        self.CheckFrame.grab_set()
        root.wait_window(self.CheckFrame)
    def combo0(self,event):
        t=self.tpG[0].get()
        if t=='A o--> B':
            self.v.set('If A occurs then eventually B occurs after A')
        elif t=='A o-- B':
            self.v.set('If A occurs then B occurs before or after A')
        elif t=='A o--o B':
            self.v.set('If A occurs then B occurs in the next position after A')
        elif t=='A -->o B':
            self.v.set('If B occurs then A occurs before B')
        else:
            self.v.set('...')
        visited=self.trTasks1.selection()    
        for elt in self.trTasks2.get_children(''):
            self.trTasks2.delete(elt)
        curs=[]   
        for i in visited:
            curs.append(self.trTasks1.item(i)['text'])
        for elt in self.Tasks:
                if self.Tasks[elt][4]==curs[0]:
                    cur=elt
        curs = self.parcoursFlow(cur)
        i=0
        for elt in curs:
            self.trTasks2.insert('',"end", str(i),text=elt,image=self.image_0)
            i+=1
    def combo1(self,event):
        visited=self.trTasks1.selection()    
        for elt in self.trTasks2.get_children(''):
            self.trTasks2.delete(elt)
        curs=[]
        for i in visited:
            curs.append(self.trTasks1.item(i)['text'])
        self.v.set('One of Ai is followed by one of Bi')
        g = self.tpG[1].get()
        for elt in self.Gateways:
            if self.Gateways[elt][4]==g:
                g=elt
                break            
        curs=self.parcoursGateway(curs,g)
        i=0
        for elt in curs:
            self.trTasks2.insert('',"end", str(i),text=elt,image=self.image_0)
            i+=1
    def combo2(self,event):
        visited=self.trTasks1.selection()    
        for elt in self.trTasks2.get_children(''):
            self.trTasks2.delete(elt)
        curs=[]
        for i in visited:
            curs.append(self.trTasks1.item(i)['text'])
        self.v.set('At least one of Ai is followed by at least one of Bi')
        g = self.tpG[2].get()
        for elt in self.Gateways:
            if self.Gateways[elt][4]==g:
                g=elt
                break            
        curs=self.parcoursGateway(curs,g)
        i=0
        for elt in curs:
            self.trTasks2.insert('',"end", str(i),text=elt,image=self.image_0)
            i+=1
    def combo3(self,event):
        visited=self.trTasks1.selection()    
        for elt in self.trTasks2.get_children(''):
            self.trTasks2.delete(elt)
        curs=[]
        for i in visited:
            curs.append(self.trTasks1.item(i)['text'])
        self.v.set('Ai execute simultaneously, Bi has to be executed afterwards')
        g = self.tpG[3].get()
        for elt in self.Gateways:
            if self.Gateways[elt][4]==g:
                g=elt
                break            
        curs=self.parcoursGateway(curs,g)
        i=0
        for elt in curs:
            self.trTasks2.insert('',"end", str(i),text=elt,image=self.image_0)
            i+=1
    def combo4(self,event):
        visited=self.trTasks1.selection()    
        for elt in self.trTasks2.get_children(''):
            self.trTasks2.delete(elt)
        curs=[]
        for i in visited:
            curs.append(self.trTasks1.item(i)['text'])
        self.v.set('with condition:At least one of Ai is followed by at least one of Bi')
        g = self.tpG[4].get()
        for elt in self.Gateways:
            if self.Gateways[elt][4]==g:
                g=elt
                break            
        curs=self.parcoursGateway(curs,g)
        i=0
        for elt in curs:
            self.trTasks2.insert('',"end", str(i),text=elt,image=self.image_0)
            i+=1
    def chV(self):
        if self.checkV.get() == 1:
            self.trTasks1.state(['disabled'])
            self.trTasks2.state(['disabled'])
            for i in range(5):
                self.bg[i].state(['disabled'])
                self.tpG[i].state(['disabled'])
            self.txtVerify.state(['!disabled'])
            self.txtVerify.focus_set()
        else:
            self.trTasks1.state(['!disabled'])
            self.trTasks2.state(['!disabled'])
            for i in range(5):
                self.bg[i].state(['!disabled'])
                self.tpG[i].state(['!disabled'])
            self.txtVerify.state(['disabled'])
    def plus(self, Seq):
        elt1, elt2 = Seq
        if C[elt1] >= 1:
            if C[elt2] ==-1: C[elt2]  = 1
            elif C[elt2]!=0 and elt2!='E1' : C[elt2] += 1
    """
    def removeLTLAnd(self,e,TD):
        T = []
        for seq in self.Sequences:
            if seq[1] == e:
                T.append(seq[1])
        for elt in T[:len(T)-1]:
            print(':: atomic{remove'+str(len(T))+'('+TD[D[elt][4]]+',',end='')
        print(TD[D[T[len(T)-1]][4]]+') -> add1('+TD[D[e][4]]+');}\n')
    """        
    def Cohe(self):
        if len(self.Events) == 0:
            messagebox.showinfo("Info","Create BPMN!")
            return
        if self.redmenu(): return
        self.initialize()
        L = []
        V = []
        cur = 'E0'
        L.append(cur)
        seqV = []
        eltA = []
        TT = self.parcoursp()
        TD = {D[TT[i]][4]:'T['+str(i)+']' for i in range(len(TT))}
        while L:
            cur = L.pop(0)
            if C[cur] < 1: continue 
            #====================================================================
            if cur[0]=='G' : # si gateway, compter le nombre d'entrées actives
                pa = pt = 0
                for elt in self.Sequences:
                    if elt[1] == cur and self.Sequences[elt][1] and C[ elt[0] ]!=-1:
                        pa += 1 # Une entrée active de plus
                    if elt[1] == cur : pt += 1
                if pa==0:
                    C[cur]= -1
                    continue
            #====================================================================
            if cur[0]=='E' or cur[0]=='T':
                for seq in self.Sequences:
                    if seq[0] == cur :
                        self.plus( seq )
                        if seq[1] not in L: L.append(seq[1])
                if cur != 'E1' : C[cur] = 0 # absorber les joutons ('_')
            #============================================================
            elif cur[0]=='G' and len(D[cur][2])==1: # exclusive gateway
                if pa == 1 and C[cur]>=1: # exatement une entrée active
                    absorb = False
                    for seq in self.Sequences:
                        if seq[0] == cur :
                            if self.Sequences[ seq ][1]:# Sortie active
                                self.plus( seq )  # transmettre le jouton
                                absorb = True
                            if seq[1] not in L: L.append(seq[1])
                    if absorb : C[cur] = 0 # absorber les joutons ('_')
                else :
                    pass# plusieurs entrées  :S
            #============================================================                
            elif cur[0]=='G' and len(D[cur][2])==2: # inclusive gateway
                if pa > C[cur] : # le nbr de joutons < nbr d'entrées actives
                    continue
                # Sinon, si la sortie est active alors: sir fi amani allah
                absorb = False
                for seq in self.Sequences:
                    if seq[0] == cur :
                        if self.Sequences[ seq ][1]:# Sortie active
                            self.plus( seq )  # transmettre le jouton
                            absorb = True
                        if seq[1] not in L: L.append(seq[1])
                if absorb :C[cur] = 0 # absorber les joutons ('_')
            #============================================================
            elif cur[0]=='G' and len(D[cur][2])==3: # parallel gateway
                # le nbr de joutons < nbr d'entrées actives
                # ou le nbr de port actif < nbr port total
                if pa < pt or pa > C[cur] :
                    continue
                # Sinon, si la sortie est active alors: sir fi amani allah
                absorb = False
                for seq in self.Sequences:
                    if seq[0] == cur :
                        if self.Sequences[ seq ][1]:# Sortie active
                            self.plus( seq )  # transmettre le jouton
                            absorb = True
                        if seq[1] not in L: L.append(seq[1])
                if absorb : C[cur] = 0 # absorber les joutons ('_')
            #============================================================                                    
            elif cur[0]=='G' and len(D[cur][2])==5: # Complex gateway
                if pa > C[cur] : # le nbr de joutons < nbr d'entrées actives
                    continue
                # Sinon, si la sortie est active alors: sir fi amani allah
                if C[cur] == self.spvv[cur]:
                    absorb = False
                    for seq in self.Sequences:
                        if seq[0] == cur :
                            if self.Sequences[ seq ][1]:# Sortie active
                                self.plus( seq )  # transmettre le jouton
                                absorb = True
                            if seq[1] not in L: L.append(seq[1])
                    if absorb : C[cur] = 0 # absorber les joutons ('_')
            #============================================================
        # COLORIAGE
        cohh = []
        for e in C:
            if e!='E1' and C[e] != 0: # if node note visited or don't fire
                if e[0]!='G':
                    self.Canevas.itemconfig(D[e][2], fill="orange red")
                else:
                    cohh += [e]
                    self.Canevas.itemconfig(D[e][2][0], fill="orange red")
                    if len(D[e][2])==2:
                        self.Canevas.itemconfig(D[e][2][1], fill="orange red")
        coh = True
        for elt in C: # is it 7ofra ???
            if elt not in ('E0','E1'):                    
                a = b = 0
                for seq in self.Sequences:
                    if seq[0] == elt: a += 1
                    if seq[1] == elt: b += 1
                if a*b == 0:
                    messagebox.showinfo("Info","Incoherent BPMN!, verify "+D[elt][4])
                    coh = False
                    return False
        if C['E1']==-1 : # end event dont get activated
            self.Canevas.itemconfig(D['E1'][2], fill="orange red")
            elts=''
            for e in cohh:
                elts += D[e][4]+' '
            messagebox.showinfo("Info","Incoherent BPMN!, verify : "+elts)
            coh = False
            return False
        if coh == True:
            messagebox.showinfo("Info","Coherent BPMN!")
        return True
    #==============================================================================        
    def initialize(self):
        if len(self.Events) == 0:
            messagebox.showinfo("Info","Create BPMN!")
            return
        if self.redmenu(): return
        for seq in self.Sequences:
            if self.Sequences[seq][2]==False:
                self.Canevas.itemconfig(self.Sequences[seq][0],
                                        fill="orange")
            else:
                self.Canevas.itemconfig(self.Sequences[seq][0],
                                        fill="chartreuse")
        for e in C:
            if e=='E0':
                color,line = 'pale green','medium sea green'
                self.Canevas.itemconfig(D[e][2],outline=line,fill=color)
            elif e=='E1':
                color,line = 'pink','indian red'
                self.Canevas.itemconfig(D[e][2],outline=line,fill=color)
            elif e[0]=='T':
                line,color = 'cornflower blue','LightBlue1'
                self.Canevas.itemconfig(D[e][2],outline=line,fill=color)
            elif e[0]=='G':
                line,color = 'yellow green','lemon chiffon'
                self.Canevas.itemconfig(D[e][2][0],outline=line,fill=color)
                if len(D[e][2])==2:
                    self.Canevas.itemconfig(D[e][2][1], fill=color)        
        C['E0']=1
        for e in C:
            if e!='E0':
                C[e]=-1
    def parcoursFlow(self,cur):
        curs=[]
        L = []
        V = []
        L.append(cur)
        i=0
        while L:
            cur = L.pop(0)
            for seq in self.Sequences:
                if seq[0]== cur :
                    if seq[1] in self.Tasks:
                        curs.append(self.Tasks[seq[1]][4])
                        i+=1  
                    if seq[1] not in V:
                        L.append(seq[1])
                        V.append(seq[1])
        return curs
    def parcours(self,sr,de):
        t = 0
        L = []
        V = []
        L.append(sr)
        V.append(sr)
        i=0
        while L:
            if t==1:
                break
            cur = L.pop(0)
            for seq in self.Sequences:
                if seq[0]== cur :
                    #self.txtResult.insert(END,D[cur][4]+'--'+D[seq[1]][4]+'\t')
                    if seq[1] == de:
                        t = 1
                        break
                    if seq[1] not in V:
                        L.append(seq[1])
                        V.append(seq[1])
        return t
    def parcoursGateway(self,items,g):      
        k=0
        for elt in items:
            for elt1 in self.Tasks:
                if self.Tasks[elt1][4]==elt:
                    k+=self.parcours(elt1,g)
                    break
        if k==len(items):
            return self.parcoursFlow(g)
        else:
            return []
    def findPath(self, src, dist):
        if src == dist: return [ [dist] ]
        Paths = [  ]
        for seq in self.Sequences:
            p = [ ]
            if seq[0]== src and self.Sequences[seq][1]:
                p    = self.findPath(seq[1], dist)
                Paths += [ [src]+ ch for ch in p ]
        return Paths
    def findPathAll(self, src, dist):
        if src == dist: return [ [dist] ]
        Paths = [  ]
        for seq in self.Sequences:
            p = [ ]
            if seq[0]== src:
                p    = self.findPathAll(seq[1], dist)
                Paths += [ [src]+ ch for ch in p ]
        return Paths
    def parcoursToken(self,sr,de):
        t = 0
        L = []
        V = []
        L.append(sr)
        V.append(sr)
        i=0
        while L:    
            if t==1:
                break
            cur = L.pop(0)
            for seq in self.Sequences:
                if seq[0]== cur :
                    if seq[1] == de:
                        t = 1
                        break
                    if seq[1] not in V:
                        L.append(seq[1])
                        V.append(seq[1])
        return t
    def radio(self):
        visited=self.trTasks1.selection()
        if(len(visited)==0):
            messagebox.showinfo("Info","Select at least one task!")
            self.vr.set('')
            for i in range(0,5):
                self.tpG[i].set('')
                self.tpG[i].config(state='disabled') 
            return
        if self.vr.get()=='F' and len(visited)>1:
            messagebox.showinfo("Info","Select one Task!")
            self.vr.set('')
                
        elif self.vr.get()=='F' and len(visited)==1:
            for i in range(1,5):
                self.tpG[i].set('')
            self.v.set('If A occurs then B occurs before or after A')
            self.tpG[0].config(state='readonly')
            for i in range(1,5):
                self.tpG[i].config(state='disabled')
        elif len(visited)>=1:
            if self.vr.get()=='E':
                self.tpG[1].config(state='readonly')
                for i in range(0,5):
                    if i!=1:
                        self.tpG[i].config(state='disabled')
                for i in range(0,5):
                    if i!=1:
                        self.tpG[i].set('')
            elif self.vr.get()=='I':
                self.tpG[2].config(state='readonly')
                for i in range(0,5):
                    if i!=2:
                        self.tpG[i].config(state='disabled')
                for i in range(0,5):
                    if i!=2:
                        self.tpG[i].set('')
            elif self.vr.get()=='P':
                self.tpG[3].config(state='readonly')
                for i in range(0,5):
                    if i!=3:
                        self.tpG[i].config(state='disabled')
                for i in range(0,5):
                    if i!=3:
                        self.tpG[i].set('')
            elif self.vr.get()=='C':
                self.tpG[4].config(state='readonly')
                for i in range(0,5):
                    if i!=4:
                        self.tpG[i].config(state='disabled')
                for i in range(0,5):
                    if i!=4:
                        self.tpG[i].set('')
    def parcoursp(self):
        L = []
        V = []
        cur = 'E0'
        L.append(cur)
        V.append(cur)
        while L:
            cur = L.pop(0)
            for seq in self.Sequences:
                if seq[0]== cur :
                    if seq[1] not in V:
                        L.append(seq[1])
                        V.append(seq[1])
        return V       
    def BPMNtoPromela(self):
        if self.filenameI=='' and self.filenameE==None:
            pml = 'BPMN'
        elif self.filenameI!='' and self.filenameE==None:
            pml=''
            for c in self.filenameI[-5::-1]:
                    if c=='/':
                        break
                    pml += c
            pml = pml[::-1]
        else:
            pml=''
            for c in self.filenameE.name[-5::-1]:
                    if c=='/':
                        break
                    pml += c
            pml = pml[::-1]        
        pml+='.pml'
        pr = open('promela/'+pml, 'w')
        t  = len(D)
        TT = self.parcoursp()
        TD = {D[TT[i]][4]:'T['+str(i)+']' for i in range(len(TT))}
        L = []
        for elt in TT:
            n = 0
            for seq in self.Sequences:
                if seq[0] == elt and  elt[0] == 'G' and len(D[elt][2])>1:
                    n+=1
            L.append(n)
            add=[]
            for j in range(1,max(L)+1):                
                add.append('#define add'+str(j)+'('
                     +''.join(['x'+str(i)+',' for i in range(1,j)])
                     +'x'+str(j)+')\t'
                     +''.join(['x'+str(i)+'++;' for i in range(1,j+1)])+'\n'
                     )
            if len(add)==0:
                add.append('#define add1(x)\tx++\n')
                
        Lpromela=['#define Transition ',str(t)+'\n',
                 'int T[Transition];\n',
                 ''.join(['#define '+D[TT[i]][4]+' T['+str(i)+']\n' for i in range(len(TT))]),
                 '#define remove1(x)\t(x>0)\t	-> x--\n',
                 #'#define add1(x)\tx++\n',
                  ''.join([elt for elt in add]),
                 'init\n',
                 '{\n',
                 'T[0]=1;\n',
                 'do\n']
        self.txtResult.delete(0.0, 'end')
        L = []
        V = []
        cur = 'E0'
        L.append(cur)
        V.append(cur)
        while L:
            cur = L.pop(0)
            TTT = []
            for seq in self.Sequences:
                if seq[0]== cur :
                    if cur=='E0' or cur[0]=='T' or (cur[0]=='G' and len(D[cur][2])==1):
                        Lpromela.append(':: atomic{remove1('+TD[D[cur][4]]+') -> add1('+TD[D[seq[1]][4]]+');}\n')
                    if (cur[0]=='G' and len(D[cur][2])>1):
                        TTT.append(seq[1])
                    if seq[1] not in V:
                        L.append(seq[1])
                        V.append(seq[1])
            if (cur[0]=='G' and len(D[cur][2])>1):
                Lpromela.append(':: atomic{remove1('+TD[D[cur][4]]+') -> add'+str(len(TTT))+'(')
                for elt in TTT[:len(TTT)-1]:
                    Lpromela.append(TD[D[elt][4]]+',')
                Lpromela.append(TD[D[TTT[len(TTT)-1]][4]]+');}\n')
        Lpromela.append(':: else -> skip;\n')
        Lpromela.append('od\n')
        Lpromela.append('}\n')
        Lpromela.append('ltl f0\t{<>('+D['E0'][4]+'>=1)}\n')
        pr.writelines(Lpromela)
        pr.close()
        return pml,TD
    def colorPaths(self,color,paths1,paths2=[]):
        for CHEMIN in paths1:
            if CHEMIN not in paths2:
                seq = tuple()
                for e in CHEMIN:
                    seq += (e,)
                    if len(seq)==2:
                        self.Canevas.itemconfig(self.Sequences[seq][0],fill=color)
                        seq=(seq[1],)
    def testPath(self,path):
        c = 0
        for e1 in path:
            for e2 in e1:
                if e2[0]=='G':
                    c+=1
        if c == len(path):
            return True
        return False
    def btnSimulate(self):
        if self.cmdS=='':
            return
        self.txtResult.delete(0.0, 'end')
        self.txtResult.insert(END,'BPMN elements:\n')
        LL=[]
        for elt in self.TD1:
            LL.append(self.TD1[elt])
        LL.sort()
        for elt1 in LL:
            for elt2 in self.TD1:
                if self.TD1[elt2]==elt1:
                    self.txtResult.insert(END,'\t'+elt2+'\t<->\t'+elt1+'\n')
                    break
        self.txtResult.insert(END,'\nSpin Simulate/Reply:\n')
        p = subprocess.Popen(self.cmdS, shell=True, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
        for line in p.stdout.readlines():
            self.txtResult.insert(END,line)
    def btnVerify(self):
        for seq in self.Sequences:
            if self.Sequences[seq][2]==False:
                self.Canevas.itemconfig(self.Sequences[seq][0],
                                        fill="orange")
            else:
                self.Canevas.itemconfig(self.Sequences[seq][0],
                                        fill="chartreuse")
        if self.checkV.get()==0:
            cur1=self.trTasks1.selection()
            cur2=self.trTasks2.selection()
            if len(cur1)==0 or len(cur2)==0:
                return
            curs1=[]
            for i in cur1:
                curs1.append(self.trTasks1.item(i)['text'])
            curs2=[]
            for i in cur2:
                curs2.append(self.trTasks2.item(i)['text'])
            ########verification results:
            ######Sequenciel
            if self.vr.get()=='F' and self.tpG[0].get()!='':
                for elt in self.Tasks:
                    if self.Tasks[elt][4]==curs1[0]:
                        sr=elt
                        break                    
                for elt in self.Tasks:
                    if self.Tasks[elt][4]==curs2[0]:
                        de=elt
                self.LESCHEMINS = self.findPath(sr,de)
                self.LESCHEMINSALL = self.findPathAll(sr,de)
                if not len(self.LESCHEMINS):
                    messagebox.showinfo("Info","Unverified property!")
                    self.colorPaths('red',self.LESCHEMINSALL,self.LESCHEMINS)
                elif C[sr]!=0:
                    messagebox.showinfo("Info","Unverified property!")
                    self.colorPaths('red',self.LESCHEMINS)
                else:
                    messagebox.showinfo("Info","Verified property!")
                    self.colorPaths('red',self.LESCHEMINSALL,self.LESCHEMINS)
                    self.colorPaths('blue',self.LESCHEMINS)
            ######Xor, Or, And et AndComplex
            elif self.vr.get()!='F' and (self.tpG[1].get()!='' or
                                         self.tpG[2].get()!='' or
                                         self.tpG[3].get()!='' or
                                         self.tpG[4].get()!=''):
                if self.vr.get()=='E':
                    g = self.tpG[1].get()
                elif self.vr.get()=='I':
                    g = self.tpG[2].get()
                elif self.vr.get()=='P':
                    g = self.tpG[3].get()
                elif self.vr.get()=='C':
                    g = self.tpG[4].get()
                for elt2 in self.Gateways:
                    if self.Gateways[elt2][4]==g:
                        break
                K1=0
                path1={}
                for elt in curs1:
                    k1=0
                    for elt1 in self.Tasks:
                        if self.Tasks[elt1][4]==elt:
                            break
                    self.LESCHEMINS = self.findPath(elt1,elt2)
                    path1[elt]=self.LESCHEMINS
                    self.LESCHEMINSALL = self.findPathAll(elt1,elt2)
                    self.colorPaths('red',self.LESCHEMINSALL,self.LESCHEMINS)
                    if C[elt1]==-1:
                        self.colorPaths('red',self.LESCHEMINS)
                    elif C[elt1]!=-1:                        
                        self.colorPaths('blue',self.LESCHEMINS)
                        k1+=len(self.LESCHEMINS)
                    if k1>=1:k1=1
                    K1+=k1
                g1 = gg1 = True
                for e1 in path1:
                    for e2 in path1:
                        for i in range(len(path1[e1])):
                            g1 = self.testPath(path1[e1])
                            for j in range(len(path1[e2])):
                                if set(path1[e1][i])<set(path1[e2][j]):
                                    K1-=1
                            if g1==False:
                                gg1=False                                    
                K2=0
                path2={}
                for elt in curs2:
                    k2=0
                    for elt1 in self.Tasks:
                        if self.Tasks[elt1][4]==elt:
                            break
                    self.LESCHEMINS = self.findPath(elt2,elt1)
                    path2[elt]=self.LESCHEMINS
                    self.LESCHEMINSALL = self.findPathAll(elt2,elt1)
                    if k2>=1:k2=1
                    else:self.colorPaths('red',self.LESCHEMINSALL,self.LESCHEMINS)
                    if C[elt2]==-1:
                        self.colorPaths('red',self.LESCHEMINS)
                    elif C[elt2]!=-1:                        
                        self.colorPaths('blue',self.LESCHEMINS)
                        k2+=len(self.LESCHEMINS)
                    K2+=k2
                g2 = gg2 = True
                for e1 in path2:
                    for e2 in path2:
                        for i in range(len(path2[e1])):
                            g2 = self.testPath(path2[e1])      
                            for j in range(len(path2[e2])):
                                if set(path2[e1][i])<set(path2[e2][j]):
                                    K2-=1
                            if g2==False:
                                gg2=False
                
                if self.vr.get()=='E':
                    if K1==0 or K2==0 or gg1==False or gg2==False:
                        messagebox.showinfo("Info","Unverified property!")                        
                    else:
                        messagebox.showinfo("Info","Verified property!")
                elif self.vr.get()=='I':
                    if K1==0 or K2==0 or gg1==False or gg2==False:
                        messagebox.showinfo("Info","Unverified property!")
                    else:
                        messagebox.showinfo("Info","Verified property!")
                elif self.vr.get()=='P':
                    if K1<len(curs1) or K2<len(curs2) or gg1==False or gg2==False:
                        messagebox.showinfo("Info","Unverified property!")
                    else:
                        messagebox.showinfo("Info","Verified property!")
                elif self.vr.get()=='C':
                    if K1==0 or K2==0 or gg1==False or gg2==False:
                        messagebox.showinfo("Info","Unverified property!")
                    else:
                        messagebox.showinfo("Info","Verified property!")
        else :
            self.txtResult.delete(0.0, 'end')
            f = self.txtVerify.get()
            if f=='':
                messagebox.showinfo("Info","Write LTL property!")
                self.txtVerify.focus_set()
                return
            self.pml1,self.TD1 = self.BPMNtoPromela()                
            ltl = open('promela/'+self.pml1, 'r')
            L=ltl.readlines()
            ph=L[:len(L)-2:-1]
            n=''
            for elt in ph[0][5:]:
                if elt == '\t':
                    break
                n+=elt
            ltl.close()
            ltl = open('promela/'+self.pml1, 'a')
            ltl.write('ltl f'+str(int(n)+1)+'\t{'+f+'}')
            ltl.close()
            p = subprocess.Popen("spin -a promela/"+self.pml1+";gcc -DMEMLIM=1024 -O2 -DXUSAFE -w -o pan pan.c;./pan -m1000 -a -f -c1 -N f"+str(int(n)+1),                        
            #p = subprocess.Popen("spin -f '"+f+"' >> foo.aut;spin -a -N foo.aut promela/wf2.pml;gcc -o pan pan.c;./pan -a",
                                 shell=True, stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT)
            #print("spin -a promela/wf2.pml;gcc -DMEMLIM=1024 -O2 -DXUSAFE -w -o pan pan.c;./pan -m1000 -a -f -c1 -N '"+f+"'")
            ft = Toplevel()
            ft.resizable(0,0)
            ft.geometry("%dx%d+%d+%d" % (200, 30, 650, 400))
            ft.title('SPIN')            
            space = " "
            s=''
            label = Label(ft, text=s, background='green2')
            label.pack(anchor='nw')
            for k in range(80):
                s += space
                # increments every 100 milliseconds
                label.after(100,label.config(text=s))
                label.update() # needed
            self.txtResult.insert(END,'BPMN elements:\n')
            LL=[]
            for elt in self.TD1:
                LL.append(self.TD1[elt])
            LL.sort()
            for elt1 in LL:
                for elt2 in self.TD1:
                    if self.TD1[elt2]==elt1:
                        self.txtResult.insert(END,'\t'+elt2+'\t<->\t'+elt1+'\n')
                        break
            self.txtResult.insert(END,'\nSpin Results:\n')
            t=True
            for line in p.stdout.readlines():
                self.txtResult.insert(END,line)
                if 'errors: ' in str(line):
                    r=line.decode("utf-8")[-2]
                if 'Error' in str(line):
                    t=False
            if r=='0' and t==True:
                messagebox.showinfo("Info","Verified property!")
                self.btnS.state(['disabled'])
            else:
                messagebox.showinfo("Info","Unverified property!")
                self.btnS.state(['!disabled'])
                self.cmdS = "spin -p -s -r -X -v -n123 -l -g -k promela/"+self.pml1+".trail -u10000 promela/"+self.pml1
            retval = p.wait()
            ft.destroy()
    def SelecttrTasks1(self,event):
        if self.v.get()!='':
            self.v.set('')
            for elt in self.trTasks2.get_children(''):
                self.trTasks2.delete(elt)        
    def SaveAs(self):
        if len(self.Events) == 0:
            messagebox.showinfo("Info","Create BPMN!")
            return
        self.sa = 1
        self.Export()
        
    def Export(self):
        if self.redmenu(): return
        if len(self.Events) == 0:
            messagebox.showinfo("Info","Create BPMN!")
            return    
        if self.filenameI=='' or self.sa == 1:
            if self.filenameE != None:
                self.filename = self.filenameE.name
            else:
                self.filename = self.filenameI
            initial = ''
            for c in self.filename[::-1]:
                if c=='/':
                    break
                initial += c
            initial = initial[::-1]
            self.filenameE = filedialog.asksaveasfile(mode='w',
                                                      initialdir = "/xml/",
                                                      initialfile = initial,
                                                      defaultextension=".xml",
                                                      filetypes = (("xml files",
                                                                    "*.xml"),
                                                                   ("all files",
                                                                    "*.*")))
            if self.filenameE == None:
                return
            self.filename = self.filenameE.name
        else:
            if self.filenameE != None:
                self.filename = self.filenameE.name
            else:
                self.filename = self.filenameI
        with open('xml/xml.xml') as file1:
            with open(self.filename, 'w') as file2:
                for line in file1:
                    file2.write(line)
        file1.close()
        file2.close()
        tree = etree.parse(self.filename)
        for e in tree.getiterator():
            if 'process' in e.tag:
                e.attrib['id']='bpmn'
                e.attrib['name']='bpmn'
                for elt in D:
                    if elt[0]=='E' and int(elt[1])==0:
                        etree.SubElement(e,'startEvent',dict(id=D[elt][4],x=str(D[elt][0]),y=str(D[elt][1])))
                    elif elt[0]=='E' and int(elt[1])>=1:
                        etree.SubElement(e,'endEvent',dict(id=D[elt][4],x=str(D[elt][0]),y=str(D[elt][1])))
                    elif elt[0]=='T':
                        etree.SubElement(e,'task',dict(id=D[elt][4],name=D[elt][4],x=str(D[elt][0]),y=str(D[elt][1])))
                    elif elt[0]=='G':
                        if len(D[elt][2])==1:
                            etree.SubElement(e,'exclusiveGateway',dict(id=D[elt][4],name=D[elt][4],x=str(D[elt][0]),y=str(D[elt][1])))
                        elif len(D[elt][2])==2:
                            etree.SubElement(e,'inclusiveGateway',dict(id=D[elt][4],name=D[elt][4],x=str(D[elt][0]),y=str(D[elt][1])))
                        elif len(D[elt][2])==3:
                            etree.SubElement(e,'parallelGateway',dict(id=D[elt][4],name=D[elt][4],x=str(D[elt][0]),y=str(D[elt][1])))
                        elif len(D[elt][2])==5:
                            etree.SubElement(e,'complexGateway',dict(id=D[elt][4],name=D[elt][4],x=str(D[elt][0]),y=str(D[elt][1]),nbr=str(self.spvv[elt])))
                        else:
                            pass
                    else:
                        pass
                for elt in self.Sequences:
                    ss,dd = D[elt[0]][4],D[elt[1]][4]
                    cs,ds = self.Sequences[elt][1],self.Sequences[elt][2]
                    etree.SubElement(e,'sequenceFlow',
                                     dict(sourceRef=ss,targetRef=dd,
                                          conditionExpression=str(cs),
                                          default=str(ds)))
        tree.write(self.filename,encoding='UTF-8', xml_declaration=True)
        messagebox.showinfo("Save","successful save")
        fileName = ''
        for c in self.filename[::-1]:
            if c=='/':
                break
            fileName += c
        fileName = fileName[::-1]
        root.title("BPVSL-"+fileName)
        if self.sa == 1:
            self.sa = 0
        if self.cl == 1:
            self.cl = 0
    def Imprimer(self):
        if self.redmenu(): return
        f = filedialog.asksaveasfile(mode='w', initialfile = 'bpmn.ps',
                                     initialdir = "/images/",
                                     defaultextension=".ps",
                                     filetypes = (("ps files","*.ps"),
                                                  ("all files","*.*")))
        if f==None:
            return
        self.Canevas.postscript(file=f.name, colormode='color')
        messagebox.showinfo("Save","successful save image")
    def Import(self):
        if self.redmenu(): return
        if len(self.Events)>=1:
            msg = messagebox.askyesnocancel('Info','Save BPMN?')
            if msg == None:
                return
            elif msg == True:
                self.Export()
            self.Clear()
            root.title("BPVSL-New Process")
        self.filenameI = filedialog.askopenfilename(initialdir = "/xml",title = "choose your file",filetypes = (("xml files","*.xml"),("all files","*.*")))
        if self.filenameI == '':
            return
        self.xml = 1 # variable pour importer un fichier xml
        tree = etree.parse(self.filenameI)
        for i in range(len(tree.getroot())):
            if 'process' in tree.getroot()[i].tag:
                break
        for j in range(len(tree.getroot()[i])):
            if 'x' and 'y' in tree.getroot()[i][j].attrib:
                self.X, self.Y = float(tree.getroot()[i][j].attrib['x']), float(tree.getroot()[i][j].attrib['y'])
            else:
                self.X, self.Y = uniform(50, 1000), uniform(50, 500)
            if 'startEvent' in tree.getroot()[i][j].tag:
                self.typBPMN = 0
                self.id = tree.getroot()[i][j].attrib['id']
                self.type = 'Start Event'
                self.dessiner(None)
            elif 'task' in tree.getroot()[i][j].tag:
                self.typBPMN = 1
                self.id = tree.getroot()[i][j].attrib['id']
                self.type = 'Task'
                self.dessiner(None)
            elif 'userTask' in tree.getroot()[i][j].tag:
                self.typBPMN = 1
                self.id = tree.getroot()[i][j].attrib['id']
                self.type = 'Task'
                self.dessiner(None)
            elif 'exclusiveGateway' in tree.getroot()[i][j].tag:
                self.typBPMN = 2
                self.id = tree.getroot()[i][j].attrib['id']
                self.type = 'Exclusive gateway'
                self.dessiner(None)
            elif 'inclusiveGateway' in tree.getroot()[i][j].tag:
                self.typBPMN = 2
                self.id = tree.getroot()[i][j].attrib['id']
                self.type = 'Inclusive gateway'
                self.dessiner(None)
            elif 'parallelGateway' in tree.getroot()[i][j].tag:
                self.typBPMN = 2
                self.id = tree.getroot()[i][j].attrib['id']
                self.type = 'Parallel gateway'
                self.dessiner(None)
            elif 'complexGateway' in tree.getroot()[i][j].tag:
                self.typBPMN = 2
                self.id = tree.getroot()[i][j].attrib['id']
                self.type = 'Complex gateway'
                if 'nbr' in tree.getroot()[i][j].attrib:
                    self.spvv['G'+str(self.nbrGateways)]=int(tree.getroot()[i][j].attrib['nbr'])
                else:
                    self.spvv['G'+str(self.nbrGateways)]=0
                self.dessiner(None)
            elif 'endEvent' in tree.getroot()[i][j].tag:
                self.typBPMN = 0
                self.id = tree.getroot()[i][j].attrib['id']
                self.type = 'End Event'
                self.dessiner(None)
            else:
                pass
        ss = dd = None
        for j in range(len(tree.getroot()[i])):
            if 'sequenceFlow' in tree.getroot()[i][j].tag:
                if 'conditionExpression' and 'default' in tree.getroot()[i][j].attrib:
                    cs=tree.getroot()[i][j].attrib['conditionExpression']
                    ds=tree.getroot()[i][j].attrib['default']
                    if cs == 'True':
                        cs = True
                    else:
                        cs = False
                    if ds == 'True':
                        ds = True
                    else:
                        ds = False
                else:
                    cs,ds=True,False
                for elt1 in D:
                    if D[elt1][4]== tree.getroot()[i][j].attrib['sourceRef']:
                        ss = elt1
                        for elt2 in D:
                            if D[elt2][4]== tree.getroot()[i][j].attrib['targetRef']:
                                dd = elt2
                                break
                        break
                if ss != None and dd != None:
                    if ds == False:
                        col = 'orange'
                    else:
                        col = 'chartreuse'                    
                    l = self.Canevas.create_line(D[ss][0]+10,D[ss][1],
                                                 #(D[ss][0]+D[dd][0])//2,
                                                 #(D[ss][1]+D[dd][1])//2,
                                                 D[dd][0]-10,D[dd][1], width=3,
                                                 arrow='last',capstyle='round',
                                                 smooth=1,fill=col)                    
                    self.Sequences[ss,dd]=[l,cs,ds]#l=ligne,False=no condition, False=defalt=no 
                ss = dd = None    
            else:
                pass
        self.xml = 0
        self.typBPMN = 5
        self.btn[6].config(style='A.TButton')
        for i in range(6):
            self.btn[i].config(style='I.TButton')
        if self.nbrEvents == 1:
            self.btn[0].state(['disabled'])
        nameFile = ''
        for c in self.filenameI[::-1]:
            if c=='/':
                break
            nameFile += c
        nameFile = nameFile[::-1]
        root.title("BPVSL-"+nameFile)
    def FrmTabs(self):
        self.frmTabs = Frame(root)
        self.Tabs = Notebook(self.frmTabs)
        self.Tabs.pack(fill='both')
        frmTab={0:'File',1:'Edit',2:'Format',3:'View',4:'Export/Import',
                5:'Verification'}
        tabAux=()#pour générer des variables des onglets
        for c in frmTab:
            Aux = Frame(self.Tabs)
            tabAux+=(Aux,)
            if c in range(1,5):
                st='disabled'
            else:
                st='normal'
            self.Tabs.add(Aux, text=frmTab[c], state=st)
        btnHaut={0:('New','Open','Save','Save as','Print','Exit'),
                 1:('Paste','Cut','Copy','Select','Clear'),
                 2:('Align Horizontal','Align Vertical'),
                 3:('Zom in','Zom out','Grid'),
                 4:('Image','Promela','XML'),
                 5:('Coherence','New visual property','Import property')}
        self.c = []
        k = 0
        self.checkCmd = IntVar()
        self.checkCmd.set(1)
        st='normal'
        for i in range(len(tabAux)):
            for j in range(len(btnHaut[i])):
                if i == 0 and j == 0:
                    cmd = self.new
                elif i == 0 and j == 1:
                    cmd = self.Import
                elif i == 0 and j == 2:
                    cmd = self.Export
                elif i == 0 and j == 3:
                    cmd = self.SaveAs
                elif i == 0 and j == 4:
                    cmd = self.Imprimer
                elif i == 0 and j == 5:
                    cmd = self.quiter
                elif i == 5 and j == 0:
                    cmd = self.Cohe
                elif i == 5 and j == 1:
                    cmd = self.Check
                elif i == 5 and j == 2:
                    cmd = None
                    st = 'disabled'                    
                if i==2 or i==5:
                    d = 16
                else: d = 6
                self.c += [Button(tabAux[i],text=btnHaut[i][j],width=d, command = cmd,state=st)]
                self.c[k].pack(side='left', anchor='e', padx=3, pady=3)
                k += 1
                if i == 0 and j == 5:
                    self.c += [Checkbutton(tabAux[i], text="Grid", variable=self.checkCmd, onvalue=1, offvalue=0, command=self.Chb)]
                    self.c[k].pack(side='left', anchor='e', padx=3, pady=3)
                    k += 1
        self.frmTabs.pack(side=TOP, fill=X)
    def btnEvent(self):
        if self.redmenu(): return
        self.typBPMN = 0
        self.btn[0].config(style='A.TButton')
        for i in range(7):
            if i!=0:
                self.btn[i].config(style='I.TButton')
    def btnTask(self):
        if self.redmenu(): return
        self.typBPMN = 1
        self.btn[1].config(style='A.TButton')
        for i in range(7):
            if i!=1:
                self.btn[i].config(style='I.TButton')
    def btnGateway(self):
        if self.redmenu(): return
        self.typBPMN = 2
        self.btn[2].config(style='A.TButton')
        for i in range(7):
            if i!=2:
                self.btn[i].config(style='I.TButton')
    def btnSequence(self):
        if self.redmenu(): return
        self.typBPMN = 3
        self.btn[3].config(style='A.TButton')
        for i in range(7):
            if i!=3:
                self.btn[i].config(style='I.TButton')
    def btnSequenced(self):
        if self.redmenu(): return        
        self.typBPMN = 4
        self.btn[4].config(style='A.TButton')
        for i in range(7):
            if i!=4:
                self.btn[i].config(style='I.TButton')
    def Clear(self):        
        self.Canevas.delete(ALL)
        D.clear()
        C.clear()
        self.Events.clear()
        self.Tasks.clear()
        self.Gateways.clear()
        self.Sequences.clear()
        self.nbrEvents,self.nbrTasks,self.nbrGateways,self.nbrSequences=0,0,0,0
        for c in range(1,7):
                self.btn[c].state(['disabled'])
        self.btn[0].state(['!disabled'])
        self.typBPMN = -1        
        for i in range(7):
                self.btn[i].config(style='I.TButton')
        self.grid()
    def btnClear(self):
        if self.redmenu(): return        
        msg = messagebox.askyesnocancel('Info','Clear all BPMN elements')
        if msg == None:
            return
        elif msg == True:
            self.Clear()        
    def btnSelect(self):
        if self.redmenu(): return        
        self.typBPMN = 5
        self.btn[6].config(style='A.TButton')
        for i in range(6):
                self.btn[i].config(style='I.TButton')
    def FrmGauche(self):    
        self.frmGauche = Frame(root, style='H.TFrame')
        self.btnGauche={0:['Event',PhotoImage(file="images/event1.gif"),self.btnEvent],
                        1:['Task',PhotoImage(file="images/task1.gif"),self.btnTask],
                        2:['Gateway',PhotoImage(file="images/gateway.gif"),self.btnGateway],
                        3:['Sequence',PhotoImage(file="images/sequence.gif"),self.btnSequence],
                        4:['Default Sequence',PhotoImage(file="images/sequenced.gif"),self.btnSequenced],
                        5:['Clear All',PhotoImage(file="images/clear.gif"),self.btnClear],
                        6:['Select',PhotoImage(file="images/select4.gif"),self.btnSelect]}
        self.btn=[]
        for c in self.btnGauche:
            if c == 0 :
                st = '!disabled'
            else :
                st = 'disabled'
            self.btn += [Button(self.frmGauche,state=st,text=self.btnGauche[c][0],
                                image=self.btnGauche[c][1],
                                command=self.btnGauche[c][2],width=10)]
            self.btn[c].pack()
        self.frmGauche.pack(side=LEFT, fill=Y)
#--------------------début Frame new elt de BPMN
    def activerOk(self,event):
        if self.txtTypelt.get()=='Intermediate Event' or self.txtTypelt.get()=='Sub process' or self.txtTypelt.get()=='Loop' or self.txtNamelt.get()=='':
            self.btnOk.state(['disabled'])
        else :
            self.btnOk.state(['!disabled'])
            self.otherFrame.bind('<Return>', self.dessiner)
    def btnAnnuler(self):      
        self.otherFrame.destroy()
    def editerRa(self):
        for elt in self.vo2:
            self.vo2[elt].set(0)
    def editerCh(self):
        if len(self.lo)==0 : return
        t = 0
        for elt in self.vo2:
            if self.vo2[elt].get()==0:
                t+=1
        if t == len(self.vo2):
            self.vo1.set(self.lo[len(self.lo)-1])
            return True
        else:
            self.vo1.set(None)
            return False        
    def editer(self):
        D[self.eltc][4] = self.txtNamelt.get()
        if self.eltc[0] == 'E':
            self.Events[self.eltc][4] = self.txtNamelt.get()
            self.Canevas.itemconfig(self.Events[self.eltc][3], text=self.txtNamelt.get())
        elif self.eltc[0] == 'T':
            self.Tasks[self.eltc][4] = self.txtNamelt.get()
            self.Canevas.itemconfig(self.Tasks[self.eltc][3], text=self.txtNamelt.get())
        elif self.eltc[0] == 'G':
            self.Gateways[self.eltc][4] = self.txtNamelt.get()
            self.Canevas.itemconfig(self.Gateways[self.eltc][3], text=self.txtNamelt.get())
            if len(D[self.eltc][2])==1:
                for elt in self.lo:
                    if elt==self.vo1.get():
                        self.Sequences[(self.eltc,elt)][1]=True
                    else:
                        self.Sequences[(self.eltc,elt)][1]=False
            elif len(D[self.eltc][2])==2 or len(D[self.eltc][2])==5:
                for elt in self.vo2:
                    if self.vo2[elt].get()==1:
                        self.Sequences[(self.eltc,elt)][1]=True
                    else:
                        self.Sequences[(self.eltc,elt)][1]=False
                if self.editerCh()==True and self.a!=-1:
                    self.Sequences[(self.eltc,self.vo1.get())][1]=True
            if len(D[self.eltc][2])==5:
                self.spvv[self.eltc]=int(self.spv.get()[7:])
                self.spv.set('Tokens:'+str(self.spvv[self.eltc]))
        self.otherFrame.destroy()        
    def dessiner(self,event=None):
        r = 10
        if self.xml == 0:
            self.txtTypelt.get()
            Typelt = self.txtTypelt.get()
            Namelt = self.txtNamelt.get()
        else:
            Typelt = self.type
            Namelt = self.id
            if Typelt=='Start Event':
                self.nbrEvents = 0
            elif Typelt=='End Event':
                self.nbrEvents = 1
        if self.typBPMN == 0:# on dessine Event
            if Typelt=='Start Event':
                color,line = 'pale green','medium sea green'
                mx = 1
            else:
                color,line = 'pink','indian red'
                mx = -1
            Ev = self.Canevas.create_oval(self.X-r, self.Y-r, self.X+r,
                                          self.Y+r, outline=line,width=2,
                                          fill=color)
            Te = self.Canevas.create_text(self.X, self.Y-15, text=Namelt)
            
            self.Events['E'+str(self.nbrEvents)] = [self.X, self.Y, Ev, Te, Namelt]
            D.update(self.Events)
            C['E'+str(self.nbrEvents)] = mx
            self.nbrEvents+=1
            if self.nbrEvents == 2:
                self.typBPMN = 5
                self.btn[6].config(style='A.TButton')
        elif self.typBPMN == 1:# on dessine Task
            Ta = self.Canevas.create_rectangle(self.X-r, self.Y-r, self.X+r,
                                               self.Y+r,
                                               outline='cornflower blue',
                                               fill='LightBlue1',width=2)
            Te = self.Canevas.create_text(self.X, self.Y-15,
                                          text=Namelt)
            self.Tasks['T'+str(self.nbrTasks)] = [self.X, self.Y, Ta, Te, Namelt]
            D.update(self.Tasks)
            C['T'+str(self.nbrTasks)] = -1
            self.nbrTasks+=1
        elif self.typBPMN == 2:# on dessine Gateway
            Ga=[]
            Ga += [self.Canevas.create_polygon(self.X-r*1.3,self.Y,self.X,
                                             self.Y-r*1.3, self.X+r*1.3,
                                             self.Y,self.X,self.Y+r*1.3,
                                             outline='yellow green',
                                             fill='lemon chiffon',width=2)]
            if Typelt=='Inclusive gateway':
                Ga += [self.Canevas.create_oval(self.X-r+3,self.Y-r+3,
                                              self.X+r-3, self.Y+r-3,
                                              outline='yellow green',
                                              fill='lemon chiffon')]
            elif Typelt=='Parallel gateway':
                Ga += [self.Canevas.create_line(self.X,self.Y-r+3,self.X,
                                              self.Y+r-3,
                                              fill='yellow green')]
                Ga += [self.Canevas.create_line(self.X-r+3,self.Y,self.X+r-3,
                                              self.Y, fill='yellow green')]
            elif Typelt=='Complex gateway':
                Ga += [self.Canevas.create_line(self.X,self.Y-r+3,self.X,
                                         self.Y+r-3, fill='yellow green')]
                Ga += [self.Canevas.create_line(self.X-r+3,self.Y,self.X+r-3,
                                         self.Y, fill='yellow green')]
                Ga += [self.Canevas.create_line(self.X-r+3,self.Y-r+3,self.X+r-3,
                                         self.Y+r-3, fill='yellow green')]
                Ga += [self.Canevas.create_line(self.X-r+3,self.Y+r-3,self.X+r-3,
                                         self.Y-r+3, fill='yellow green')]
            Te = self.Canevas.create_text(self.X, self.Y-15,
                                          text=Namelt)
            self.Gateways['G'+str(self.nbrGateways)] = [self.X, self.Y, Ga, Te, Namelt]
            D.update(self.Gateways)
            C['G'+str(self.nbrGateways)] = -1
            if self.xml==0:
                self.spvv['G'+str(self.nbrGateways)] = 0
            self.nbrGateways+=1            
        # activer ou bien désactiver les bouttons gauche
        for c in self.btnGauche:
            if c!=3 and c!=4:
                self.btn[c].state(['!disabled'])
        if self.nbrEvents+self.nbrTasks+self.nbrGateways>=2:
            self.btn[3].state(['!disabled'])
            self.btn[4].state(['!disabled'])
        if self.nbrEvents>=2:
            self.btn[0].state(['disabled'])
        if self.xml == 0:
            self.otherFrame.destroy()
    #event pour changer le text de newElt
    def generateOnChange(self,obj):
        obj.tk.eval('''
            proc widget_proxy {widget widget_command args} {

                # call the real tk widget command with the real args
                set result [uplevel [linsert $args 0 $widget_command]]

                # generate the event for certain types of commands
                if {([lindex $args 0] in {insert replace delete}) ||
                    ([lrange $args 0 2] == {mark set insert}) || 
                    ([lrange $args 0 1] == {xview moveto}) ||
                    ([lrange $args 0 1] == {xview scroll}) ||
                    ([lrange $args 0 1] == {yview moveto}) ||
                    ([lrange $args 0 1] == {yview scroll})} {

                    event generate  $widget <<Change>> -when tail
                }

                # return the result from the real widget command
                return $result
            }
            ''')
        obj.tk.eval('''
            rename {widget} _{widget}
            interp alias {{}} ::{widget} {{}} widget_proxy {widget} _{widget}
        '''.format(widget=str(obj)))
    def close1(self,event):
        self.otherFrame.destroy()
    def newElt(self):
        global s
        global d
        if self.typBPMN == -1 : return
        self.otherFrame = Toplevel()
        #self.otherFrame.resizable(0,0)
        self.otherFrame.bind('<Escape>', self.close1)
        w, h = root.winfo_screenwidth()*0.20, root.winfo_screenheight()*0.1
        x11, y11 = root.winfo_screenwidth()*0.3, root.winfo_screenheight()*0.3
        self.otherFrame.geometry("%dx%d+%d+%d" % (w, h, x11, y11))
        self.otherFrame.title("New Elt")
        self.frmNewElt = Frame(self.otherFrame)        
        labelName = Label(self.frmNewElt, text="Name")
        labelName.grid(row=0,column=1)
        labelType = Label(self.frmNewElt, text="Type")
        labelType.grid(row=1,column=1)        
        self.txtNamelt = Entry(self.frmNewElt,width=22)
        self.txtNamelt.focus_set()
        self.generateOnChange(self.txtNamelt)
        self.txtNamelt.bind('<<Change>>', self.activerOk)
        self.txtNamelt.grid(row=0,column=2)
        self.txtTypelt = Combobox(self.frmNewElt , state='readonly',width=20)
        self.txtTypelt.bind("<<ComboboxSelected>>", self.activerOk)        
        if self.typBPMN == 0 and self.nbrEvents==0 :
            self.txtTypelt['values'] = ('Start Event',)
        if self.typBPMN == 0 and self.nbrEvents==1 :
            self.txtTypelt['values'] = ('End Event','Intermediate Event')            
        if self.typBPMN == 1 :
            self.txtTypelt['values'] = ('Task','Sub process', 'Loop')
        if self.typBPMN == 2 :
            self.txtTypelt['values'] = ('Exclusive gateway',
                                        'Inclusive gateway',
                                        'Parallel gateway',
                                        'Complex gateway')   
        self.txtTypelt.current(0)
        self.txtTypelt.grid(row=1, column=2)
        self.btnOk = Button(self.frmNewElt, text='Ok', state='disabled',
                            command=self.dessiner)
        self.btnOk.grid(row=2, column=1)
        btnCancel = Button(self.frmNewElt, text='Cancel', command=self.btnAnnuler)
        btnCancel.grid(row=2, column=2)
        self.frmNewElt.pack(fill=Y)
        self.otherFrame.transient(root)
        self.otherFrame.update_idletasks()
        self.otherFrame.grab_set()
        s = d = None
        root.wait_window(self.otherFrame)
        return
    def countSequences(self,g):
        i,o = 0,0
        li,lo=[],[]
        for elt in self.Sequences:
            if elt[0]==g:
                o+=1
                lo.append(elt[1])
            elif elt[1]==g:
                i+=1
                li.append(elt[0])
        return i,o,li,lo
    def editElt(self):
        self.otherFrame = Toplevel()
        #self.otherFrame.resizable(0,0)
        self.otherFrame.bind('<Escape>', self.close1)
        w, h = root.winfo_screenwidth()*0.3, root.winfo_screenheight()*0.3
        x11, y11 = root.winfo_screenwidth()*0.3, root.winfo_screenheight()*0.3
        self.otherFrame.geometry("%dx%d+%d+%d" % (w, h, x11, y11))
        self.otherFrame.title("Edit")
        self.frmNewElt = Frame(self.otherFrame)
        labelName = Label(self.frmNewElt, text="Name")
        labelName.grid(row=0,column=1)
        labelType = Label(self.frmNewElt, text="Type")
        labelType.grid(row=1,column=1)
        v = StringVar(self.otherFrame, value=D[self.eltc][4])
        self.txtNamelt = Entry(self.frmNewElt,width=22,textvariable=v)
        self.generateOnChange(self.txtNamelt)
        self.txtNamelt.bind('<<Change>>', self.activerOk)
        self.txtNamelt.grid(row=0,column=2)
        self.txtTypelt = Combobox(self.frmNewElt ,state='readonly',width=20)
        self.txtTypelt.bind("<<ComboboxSelected>>", self.activerOk)
        l= Label(self.frmNewElt)
        l.grid(row=2,column=1)
        i=0
        if self.eltc=='E0':
            self.txtTypelt['values'] = ('Start Event',)
            img = PhotoImage(file ='images/event1.gif')
            txt = "     Event     "
        elif self.eltc=='E1':
            self.txtTypelt['values'] = ('End Event',)
            img = PhotoImage(file ='images/event2.gif')
            txt = "     Event     "
        elif self.eltc[0]=='T':
            self.txtTypelt['values'] = ('Task',)
            img = PhotoImage(file ='images/task1.gif')
            txt = "     Task     "
        elif self.eltc[0]=='G':
            txt = "     Gateway     "
            if len(D[self.eltc][2])==1:
                self.txtTypelt['values'] = ('Exclusive gateway',)
                img = PhotoImage(file ='images/gateway11.gif')
            elif len(D[self.eltc][2])==2:
                self.txtTypelt['values'] = ('Inclusive gateway',)
                img = PhotoImage(file ='images/gateway22.gif')            
            elif len(D[self.eltc][2])==3:
                self.txtTypelt['values'] = ('Parallel gateway',)
                img = PhotoImage(file ='images/gateway33.gif')
            else :
                self.txtTypelt['values'] = ('Complex gateway',)
                img = PhotoImage(file ='images/gateway44.gif')
        lf = Labelframe(self.frmNewElt, text='Sequence flows:')        
        l1 = Label(lf, text="Incoming sequences")
        l1.grid(row=0, column=0)        
        l2 = Label(lf, text=txt)
        l2.grid(row=0, column=1)
        lg = Label(lf, image=img)
        lg.grid(row=1, column=1)            
        l3 = Label(lf, text="Outgoing sequences     ")
        l3.grid(row=0, column=2)
        i,o,li,self.lo = self.countSequences(self.eltc)
        self.vo1,self.vo2=StringVar(),{}
        self.ro=[]
        self.co=[]
        self.rd=[]
        imgss = PhotoImage(file ='images/sequence11.gif')
        imgsd = PhotoImage(file ='images/sequence111.gif')
        self.a=-1
        for j in range(i):
            lsi = Label(lf, image=imgss,compound="right",text=D[li[j]][4],)
            lsi.grid(row=1+j, column=0,sticky='e')
        for j in range(o):
            if self.eltc[0]=='G' and len(D[self.eltc][2])==1:
                if self.Sequences[self.eltc,self.lo[j]][2]==False:
                    imgs = imgss
                elif self.Sequences[self.eltc,self.lo[j]][2]==True:
                    imgs = imgsd
                    self.a = j
                self.ro.append(Radiobutton(lf,compound="left",text=D[self.lo[j]][4],
                                           variable=self.vo1,value=self.lo[j],
                                           state=s, image= imgs,))    
            elif self.eltc[0]=='G' and (len(D[self.eltc][2])==2 or len(D[self.eltc][2])==5):
                if self.Sequences[self.eltc,self.lo[j]][2]==False:
                    self.vo2[self.lo[j]]=IntVar()
                    imgs = imgss
                    aux = Checkbutton(lf, onvalue=1, offvalue=0,
                                      variable=self.vo2[self.lo[j]],
                                      compound="left",text=D[self.lo[j]][4],
                                      image= imgs,
                                      command=self.editerCh)
                elif self.Sequences[self.eltc,self.lo[j]][2]==True:
                    imgs = imgsd
                    self.a = j
                    aux = Radiobutton(lf,compound="left",
                                      variable=self.vo1,
                                      value=self.lo[j],text=D[self.lo[j]][4],
                                      state=s, image= imgs,
                                      command=self.editerRa)
                self.ro.append(aux)
            else:
                lso = Label(lf, image=imgss,compound="left",text=D[self.lo[j]][4])
                lso.grid(row=1+j, column=2,sticky='w')
        if self.eltc[0]=='G':
            if (len(D[self.eltc][2])<=2 or len(D[self.eltc][2])==5):
                if self.a!=-1:
                    self.ro.append(self.ro.pop(self.a))
                    self.lo.append(self.lo.pop(self.a))                    
                for e in range(len(self.ro)):
                    self.ro[e].grid(row=1+e, column=2,sticky='w')
            if len(D[self.eltc][2])==5:
                nbr=[]
                for i in range(len(li)+1):
                    nbr.append('Tokens:'+str(i))
                spBox = Spinbox(lf, values = sorted(nbr),
                                textvariable=self.spv,state='readonly',width=7)
                spBox.grid(row=2, column=1)
        if self.eltc[0]=='G' and (len(D[self.eltc][2])<=2 or len(D[self.eltc][2])==5):            
            for elt in self.lo:
                if self.Sequences[(self.eltc,elt)][1]==True:
                    self.vo1.set(elt)
                    break
            if len(D[self.eltc][2])==2 or len(D[self.eltc][2])==5:
                for elt in self.vo2:
                    if self.Sequences[(self.eltc,elt)][1]==True:
                        self.vo2[elt].set(1)
                    else:
                        self.vo2[elt].set(0)
            if len(D[self.eltc][2])==5:
                if self.eltc in self.spvv:
                    if self.spvv[self.eltc]!=0:
                        self.spv.set('Tokens:'+str(self.spvv[self.eltc]))
        lf.grid(row=3, column=0, columnspan=4,sticky='nsew')            
        self.txtTypelt.current(0)
        self.txtTypelt.grid(row=1, column=2)
        self.btnOk = Button(self.frmNewElt, text='Ok', command=self.editer)
        self.btnOk.grid(row=4, column=1,sticky='nsew')
        btnCancel = Button(self.frmNewElt, text='Cancel', command=self.btnAnnuler)
        btnCancel.grid(row=4, column=3,sticky='nsew')
        self.frmNewElt.pack(fill=Y)        
        self.otherFrame.transient(root)
        self.otherFrame.update_idletasks()
        self.otherFrame.grab_set()
        root.wait_window(self.otherFrame)
#--------------------début clic button gauche
    def Clic(self,event):
        elt = None
        self.cl = 1
        self.SqMenu.unpost()
        self.ctMenu.unpost()
        self.p,self.q = 0,0
        global s
        global d
        """ Gestion de l'événement Clic gauche sur la zone graphique """
        # position du pointeur de la souris
        self.X = self.Canevas.canvasx(event.x)#event.x
        self.Y = self.Canevas.canvasx(event.y)#event.y
        D.update(self.Events)
        D.update(self.Tasks)
        D.update(self.Gateways)
        for elt in D:
                if(self.X-40<=D[elt][0]<=self.X+40 and self.Y-40<=D[elt][1]<=self.Y+40):
                    if s==None :
                        s=elt
                    else: d=elt
                    break
        #creer sequence
        if (self.typBPMN == 3 or self.typBPMN == 4) and s!=None:
            if d == None:
                pass
            else:
                if self.redLine != None:
                    self.Canevas.delete(self.redLine)
                    self.redLine = None
                if self.typBPMN == 3:
                    col = 'orange'
                else:
                    col = 'chartreuse'                    
                l = self.Canevas.create_line(D[s][0]+10,D[s][1],
                                                 #(D[s][0]+D[d][0])//2-50,
                                                 #(D[s][1]+D[d][1])//2+50,                    
                                                 D[d][0]-10,D[d][1], width=3,
                                                 arrow='last',capstyle='round',
                                                 smooth=1, fill=col,)
                                             #dash=(4, 4))
                td = False
                for elt in self.Sequences:
                    if elt[0]==s and (col=='chartreuse' and self.Sequences[s,elt[1]][2]==True):
                            td=True
                            break
                tt = 1
                if s[0]=='T':    
                    for elt in self.Sequences:
                        if elt[0]==s:
                            tt+=1
                if d[0]=='T':    
                    for elt in self.Sequences:
                        if elt[1]==d:
                            tt+=1      
                if tt>1 or (s,d) in self.Sequences or (d,s) in self.Sequences or s==d or d=='E0' or s=='E1' or (s=='E0' and d=='E1') or (col=='chartreuse' and (s[0]=='E' or s[0]=='T' or (s[0]=='G' and 5>len(D[s][2])>2))) or td==True:
                    self.Canevas.delete(l)
                else:
                    cs,ds=True,False
                    if s[0]=='G' and (len(D[s][2])<=2 or len(D[s][2])==5):
                        if col=='orange':
                            cs,ds=False,False
                            m=0
                            for elt in self.Sequences:
                                if elt[0]==s:
                                    m+=1
                            if m==0:cs=True
                        else:
                            for elt in self.Sequences:
                                if elt[0]==s and self.Sequences[s,elt[1]][1]==True:
                                    cs=False
                                    break
                            ds=True
                    self.Sequences[s,d]=[l,cs,ds]#l=ligne,cs=condition, ds=defalt
                s = d = None
        #new elt bpmn
        if self.typBPMN in range(0,3):    
            self.newElt()
            return        
        #glisser elt bpmn
        if self.typBPMN == 5:
            self.Object=[]
            if d!=None : x1=d
            elif s!=None: x1=s
            else: return            
            self.Object.append(D[x1][2])
            self.Object.append(D[x1][3])
    def StopMove(self, event):
        global s
        global d
        if self.typBPMN == 5:
            s = None
    def Drag(self,event):
        global s
        global d
        if self.typBPMN == 5:
            X = event.x
            Y = event.y
            r=10
            if d!=None : x1=d
            elif s!=None : x1=s
            else: return
            # mise à jour de la position de l'elt
            if x1[0]=='E':
                self.Canevas.coords(self.Object[0],X-r,Y-r,X+r,Y+r)
                self.Events[x1][0],self.Events[x1][1] = X, Y
                D.update(self.Events)
            elif x1[0]=='T':
                self.Canevas.coords(self.Object[0],X-r,Y-r,X+r,Y+r)
                self.Tasks[x1][0],self.Tasks[x1][1] = X, Y
                D.update(self.Tasks)
            else:
                self.Canevas.coords(self.Object[0][0],X-r*1.3,Y,X,Y-r*1.3,X+r*1.3,Y,X,Y+r*1.3)
                self.Gateways[x1][0],self.Gateways[x1][1] = X, Y
                D.update(self.Gateways)
                if len(self.Gateways[x1][2])==2:
                    self.Canevas.coords(self.Object[0][1],X-r+3,Y-r+3,X+r-3,Y+r-3)
                elif len(self.Gateways[x1][2])==3:
                    self.Canevas.coords(self.Object[0][1],X,Y-r+3,X,Y+r-3)
                    self.Canevas.coords(self.Object[0][2],X-r+3,Y,X+r-3,Y)
                elif len(self.Gateways[x1][2])==5:
                    self.Canevas.coords(self.Object[0][1],X,Y-r+3,X,Y+r-3)
                    self.Canevas.coords(self.Object[0][2],X-r+3,Y,X+r-3,Y)
                    self.Canevas.coords(self.Object[0][3],X-r+3,Y-r+3,X+r-3,Y+r-3)
                    self.Canevas.coords(self.Object[0][4],X-r+3,Y+r-3,X+r-3,Y-r+3)
            #déplasser le nom de l'elt
            self.Canevas.coords(self.Object[1],X,Y-15)
            #déplasser les séquences
            for key in self.Sequences:
                xy=[]
                xy=self.Canevas.coords(self.Sequences[key[0],key[1]][0])
                if key[0]==x1:
                    self.Canevas.coords(self.Sequences[key[0],key[1]][0],
                                        X+10,Y,xy[2],xy[3])
                elif key[1]==x1 :
                    self.Canevas.coords(self.Sequences[key[0],key[1]][0],
                                        xy[0],xy[1],X-10,Y)
    def escape1(self,event):
        global s
        global d
        d = s = None
        self.Canevas.delete(self.redLine)
        self.redLine = None
    def mouseMoved(self, event):
        global s
        global d
        if self.typBPMN == 3 or self.typBPMN == 4:
            if s != None and d == None :
                if self.redLine != None:
                    self.Canevas.delete(self.redLine)
                self.redLine = self.Canevas.create_line(D[s][0],D[s][1],
                                            event.x-40,event.y-40,event.x,
                                            event.y, width=3,
                                            arrow='last',capstyle='round',
                                            smooth=1,fill='magenta')
                root.bind('<Escape>', self.escape1)
#--------------------début menu contextuel    
    def doubleClic(self,event):
        self.xc = event.x
        self.yc = event.y
        k=0
        for elt in D:
            if(event.x-40<=D[elt][0]<=event.x+40 and event.y-40<=D[elt][1]<=event.y+40):
                self.eltc = elt
                k=1
                break
        if k == 0:
            return
        self.editElt()
    def ContextEditName(self):
        self.editElt()
    def ContextClearSq(self):
        self.p,self.q = 0,0
        self.objectToBeDeleted = self.tuple_objects[0]
        del self.dictID[self.objectToBeDeleted]
        self.Canevas.delete(self.objectToBeDeleted)
        sq=[]
        for elt in self.Sequences:
            if self.Sequences[elt][0] == self.objectToBeDeleted:
                sq+=[elt]
        for elt in sq:
            del self.Sequences[elt]
        return
    def ContextClearElt(self): #supprimer elt de menu contextuel
        self.p,self.q = 0,0
        if self.eltc[0] == 'E':
            self.Canevas.delete(self.Events[self.eltc][2])
            self.Canevas.delete(self.Events[self.eltc][3])
            del self.Events[self.eltc]
            if self.eltc == 'E0':
                self.nbrEvents = 0
            elif self.eltc == 'E1':
                self.nbrEvents = 1
            self.btn[0].state(['!disabled'])
        elif self.eltc[0] == 'T':
            self.Canevas.delete(self.Tasks[self.eltc][2])
            self.Canevas.delete(self.Tasks[self.eltc][3])
            del self.Tasks[self.eltc]
        elif self.eltc[0] == 'G':
            for i in range(len(self.Gateways[self.eltc][2])):
                self.Canevas.delete(self.Gateways[self.eltc][2][i])
            self.Canevas.delete(self.Gateways[self.eltc][3])
            del self.Gateways[self.eltc]
        del D[self.eltc]
        del C[self.eltc]
        sq=[]
        for elt in self.Sequences:
            if self.eltc == elt[0] or self.eltc == elt[1]:
                self.Canevas.delete(self.Sequences[elt][0])
                sq+=[elt]
        for elt in sq:
            del self.Sequences[elt]
    def popup(self, event):        
        self.xc = event.x
        self.yc = event.y
        self.SqMenu.unpost()
        self.ctMenu.unpost()
        self.cl = 1
        for elt in D:
            if(event.x-40<=D[elt][0]<=event.x+40 and event.y-40<=D[elt][1]<=event.y+40):
                self.eltc = elt
                if self.redLine != None:
                    return
                self.p = 1
                self.ctMenu.post(event.x_root, event.y_root)
                break            
        for elt in self.Sequences:
            self.tuple_objects = self.Canevas.find_closest(self.xc, self.yc, start=(D[elt[0]][2],self.Sequences[elt][0]))
            self.dictID[self.Sequences[elt][0]] = self.Canevas.coords(self.Sequences[elt][0])
            if len(self.tuple_objects) > 0 and self.tuple_objects[0] in self.dictID:
                if self.redLine != None:
                    return
                self.q = 1
                self.SqMenu.post(event.x_root, event.y_root)
#--------------------fin menu contextuel
    def Chb(self):
        if self.redmenu():
            if self.checkCmd.get()==0:
                self.checkCmd.set(1)
            else:
                self.checkCmd.set(0)
            return
        if self.checkCmd.get() == 0:
            for x in range(len(self.gx)):
                self.Canevas.itemconfig(self.gx[x],state='hidden')
            for y in range(len(self.gy)):
                self.Canevas.itemconfig(self.gy[y],state='hidden')
        else:
            for x in range(len(self.gx)):
                self.Canevas.itemconfig(self.gx[x],state='normal')
            for y in range(len(self.gy)):
                self.Canevas.itemconfig(self.gy[y],state='normal')
    def grid(self):
        #debut grid
        # vertical lines at an interval of "line_distance" pixel
        self.gx = []
        for x in range(10,1200,50):
            self.gx+=[self.Canevas.create_line(x, 0, x, 1200, fill="#b0b0b0")]
        # horizontal lines at an interval of "line_distance" pixel
        self.gy = []
        for y in range(10,1200,50):
            self.gy+=[self.Canevas.create_line(0, y, 1200, y, fill="#b0b0b0")]
        #fin grid
    def FrmMain(self):    
        self.FrmMain = Frame(root)
        self.Canevas = Canvas(self.FrmMain, width=1200, height=1200,
                              bg='white', scrollregion=(0, 0, 1150, 550))
        self.grid()#grid
        self.bdv =Scrollbar(self.FrmMain, orient =VERTICAL, 
                       command =self.Canevas.yview)#, bd =1)
        self.bdh =Scrollbar(self.FrmMain, orient =HORIZONTAL,
                       command =self.Canevas.xview)#, bd =1)
        self.Canevas.configure(xscrollcommand =self.bdh.set,
                               yscrollcommand =self.bdv.set)
        self.bdv.pack(side = RIGHT,fill=Y,expand=1, pady=5)#.grid(row =0, column =1, sticky = NS)
        self.bdh.pack(side = BOTTOM, fill=X,expand=1, pady=5)#.grid(row =1, column =0, sticky = EW)
        self.Canevas.bind('<Button-1>', self.Clic)
        self.Canevas.bind('<Motion>',self.mouseMoved)
        self.Canevas.bind('<B1-Motion>',self.Drag)
        self.Canevas.bind("<ButtonRelease-1>", self.StopMove)
        self.Canevas.bind('<Double-Button-1>', self.doubleClic)
        self.Canevas.bind("<Button-3>", self.popup)
        self.Canevas.pack(side=LEFT,fill=BOTH,expand=1, pady =5)
        # create a click context menu
        self.SqMenu = Menu(self.Canevas, tearoff=0)
        self.SqMenu.add_command(label="Clear Sequence", command=self.ContextClearSq)
        self.SqMenu.add_separator()
        self.SqMenu.add_command(label="Properties", state = 'disabled')
        self.ctMenu = Menu(self.Canevas, tearoff=0)
        self.ctMenu.add_command(label="Clear", command=self.ContextClearElt)
        self.ctMenu.add_separator()
        self.ctMenu.add_command(label="Properties", command=self.ContextEditName)
        self.FrmMain.pack(fill=BOTH, expand=1)
    def FrmBas(self):    
        self.FrmBas = Frame(root, style='B.TFrame')
        self.lbStat = Label(self.FrmBas, text="bas")
        self.lbStat.pack(side=LEFT, padx=0, pady=0)
        self.FrmBas.pack(side=BOTTOM, fill=X)  
#-------------------------------------------------------------------
root = Tk()
w, h = root.winfo_screenwidth()*0.75, root.winfo_screenheight()*0.75
x1, y1 = w*0.125, h*0.125
root.geometry("%dx%d+%d+%d" % (w, h, x1, y1))
#root.overrideredirect(1)
    #root.attributes('-fullscreen', True)
app = BPVSL(root)
#root.resizable(0,0)
root.mainloop()
