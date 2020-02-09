grepyAst
=======

line command tool wich allows to find ast exprexions in python files:

The next example show all the methods in a class in this proyect:
```
$ python grepyAst/analysis.py -e class/def -f ./grepyAst/ -a 1 -b 1

('class/def', './analysis/', 1, 1)
(0.0005740000000000016, './analysis/analysis.py')
===================>./analysis/analysis.py<=================
class recursive_info(object):
    def __init__(self):
========================================{60}

    def BASE(self, _ast):
========================================{65}

    def REC(self, _ast):
========================================{68}
class aux():
    def __init__(self, data):
========================================{81}

    def __contains__(self, x):
========================================{104}

    def __call__(self, node, v):
========================================{107}

```

Where :
    -a: lines show after the init of selected expresion
    -b: lines show before the init of selected expresion
    -e: expression of looking for:
            E := e | e/E 
            e := class | def | Assign | Loop |e?se
            se := name:value:..: | name=value
    -f: file looking for, if finished in / traited as directory looking for
         every line.


