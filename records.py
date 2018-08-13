from collections import deque
from utils import show,to_latex,ttracing,substitute,reduce_path,latex_path

class Rec(object):
    def __init__(self,d={}):
        for item in d.items():
            if isinstance(item[1], dict):
                self.addfield(item[0], Rec(item[1]))
            else:
                self.addfield(item[0], item[1])
            
    def show(self):
        s = ""
        for kvp in self.fields():
            if s == "":
                s = s + reduce_path(kvp[0]) + " = "
            else:
                s = s + ", "+ reduce_path(kvp[0]) + " = "
            
            if(isinstance(kvp[1], Rec)):
                 s = s + kvp[1].show()                
            else:
                s = s + show(kvp[1]) 
        return "{"+s+"}"
        
    def to_latex(self):
        kvps = []
        for k, v in self.fields():
            kvps.append(latex_path(k, True) + ' &=& ' + to_latex(v))
        return "\\left[\\begin{array}{rcl}\n" + '\\\\\n'.join(kvps) + "\n\\end{array}\\right]"

    def fields(self):
        """Returns the fields as a list of label-value tuples."""
        return list(self.__dict__.items())

    def labels(self):
        """Returns the labels as a list."""
        return list(self.__dict__.keys())

    def addfield(self, label, value):
        if label in self.labels():
            print("\"" +label + "\"" + " is already a label in " +show(self))
        else: 
            self.__setattr__(label, value)
            return self

    def addpath(self, path, value):
        pathl = path.split(".")
        return self.addpathl(pathl, value)

    def addpathl(self, pathl, value):
        if len(pathl) == 1:
            return self.addfield(pathl[0],value)
        elif pathl[0] in self.labels():
            val = self.__getattribute__(pathl[0])
            if isinstance(val, Rec):
                val.addpathl(pathl[1:], value)
            else:
                print(val + ' is not a record.')
            return self
        else:
            self.addfield(pathl[0], Rec().addpathl(pathl[1:],value))
            return self
            
    
    # def pathvalue(self,path):
    #     if len(path) == 1: 
    #         return self.__getattribute__(str(path[0]))
    #     else: 
    #         return Rec.pathvalue(self.__getattribute__(path[0]), path[1:])
            
    def pathvalue(self, path):
        splits=deque(path.split("."))
        if (len(splits) == 1):
            if splits[0] in dir(self):
                return self.__getattribute__(splits[0])
            else:
                if ttracing('pathvalue'):
                    print(splits[0]+' not a label in '+self.show())
                return None
        else:
            addr = splits.popleft()
            if addr not in dir(self):
                if ttracing('pathvalue'):
                    print('No attribute '+addr+' in '+show(self))
                return None
            elif 'pathvalue' not in dir(self.__getattribute__(addr)):
                if ttracing('pathvalue'):
                    print('No paths into '+show(self.__getattribute__(addr)))
                return None
            else:
                return self.__getattribute__(addr).pathvalue(".".join(splits))
    
    #Recursive for future use
    #Needs redefining so as not to be destructive?
    def relabel(self, oldlabel, newlabel):
        newrec = self.subst(oldlabel, newlabel)
        if oldlabel in newrec.labels():
            value = newrec.__dict__[oldlabel]
            newrec.__delattr__(oldlabel)
            newrec.__setattr__(newlabel, value)
        return newrec
    
    def subst(self,v,a):
        res = Rec()
        for l, lval in self.fields():
            if lval == v:
                res.addfield(l,a)
            elif isinstance(lval,str):
                res.addfield(l,lval)
            else: 
                res.addfield(l,substitute(lval,v,a))
        return res

    def eval(self):
        for l, lval in self.fields():
            if 'eval' in dir(lval):
                self.__setattr__(l,lval.eval())
        return self
                
    def flatten(self):
        res = Rec()
        for l, lval in self.fields():
            if isinstance(lval,Rec):
                rec1 = lval.flatten()
                for k2 in list(rec1.labels()):
                    rec1 = rec1.relabel(k2, l + '.' + k2)
                for l1, val in rec1.fields():
                    res.addfield(l1,val)
            else:
                res.addfield(l,lval)
        return res

    def unflatten(self):
        res = Rec()
        for l, v in self.fields():
            res.addpath(l, v)
        return res
                



    
