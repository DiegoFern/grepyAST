import ast
import itertools

def rec_list(xs):
    try:
        x = next(xs)
    except StopIteration:
        return ()
    return (x, rec_list(xs))


def iterate_ast(root, filter_):
    filter_ = rec_list(iter(filter_))
    to_cover = [(0, root, filter_)]
    while to_cover:
        d, node, filter_ = to_cover.pop()
        for (a, b) in ast.iter_fields(node):
            if filter_ == ():
                yield(d, a, b)
            print(filter_)
            print(a)
            if filter_ != () and a == filter_[0]:

                if type(b) is list:
                    to_cover.extend(map(lambda x: (d+1, x, filter_[1]), b))
                elif issubclass(type(b), ast.stmt):
                    to_cover.append((d+1, b, filter_[1]))
            if type(b) is list:
                to_cover.extend(map(lambda x: (d+1, x, filter_), b))
            elif issubclass(type(b), ast.stmt):
                to_cover.append((d+1, b, filter_))


def iter_children(s, n=0, select=(), rec=True):
    if type(select) is tuple:
        select = select+(None,)
    return _iter_children(s, n=n, select=select, rec=rec)


def _iter_children(s, n=0, select=(), rec=True):

    for i in (ast.iter_child_nodes(s)):
        select2 = select
        if select is ():
            yield (n, str(i))
        elif select is None:
            yield (n, i)
        elif len(select) and type(i) == select[0]:
            select2 = select[1:]
            if select2 == (None,):
                yield (n, i)
        for x in _iter_children(i, n+1, select2):
            yield x
        if select is not None and rec and (len(select) != len(select2)):
            for x in _iter_children(i, n+1, select):
                yield x


class recursive_info(object):
    def __init__(self):
        for val in filter(lambda x: x[0] != '_', dir(ast)):
            if val not in self.__class__.__dict__:
                self.__dict__[val] = self.REC

    def BASE(self, _ast):
        return _ast

    def REC(self, _ast):
        try:
            ans={(type(_ast), a): [
                        self.REC(b) for b in bs
                    ] if type(bs) is list else self.REC(bs)
                    for (a, bs) in _ast.__dict__.items()}
            ans['self'] = _ast
            return ans
        except:
            return _ast


class aux():
    def __init__(self, data):
        self.v = data.split('?')[0]
        def parse_block(block):
            if '=' in block:
                def f(node, v):
                    return node.get((v, f.a)) != f.b
                f.a, f.b = block.split('=')
                return f
            elif ':' in block:
                def f(node, v):
                    stack = f.a[::-1]
                    while stack:
                        if (v, stack.pop()) in node:
                            v = type(node['self'])
                        else:
                            return False
                    return True
                f.a = block.split(':')
                return f

        self.filter = [parse_block(i) for i in data.split('?')[1:]]
        self.types = found.ast[self.v]

    def __contains__(self, x):
        return x in self.types

    def __call__(self, node, v):
        for f in self.filter:
            if f(node, v):
                return False
        return True


def found(expr, parse, rec=True, n=0, A=5, B=5, ast_symbol=False):
    parseCode = parse.split('\n')
    expr = [[aux(a) for a in name.split('|')] for name in expr.split('/')]
    parse = recursive_info().REC(ast.parse(parse))[(ast.Module, 'body')]
    nodes = [(p, expr,None) for p in parse]
    points = []
    while nodes:
        
        node, expr, pather = nodes.pop()
        v = type(node['self'])
        if (len(expr) == 1) and any( ((v in x) and x(node, v) for x in expr[0])):
            chain =[node]
            while pather is not None:
                chain.append(pather[0])
                pather = pather[1]
            if not ast_symbol:
                v = type(node['self'])
                
                points.append([node[(type(node['self']), 'lineno')] for node in chain])
            else:
                points.append(chain[0])

        if expr and any( ((v in x) and x(node, v) for x in expr[0])):
            nodes.extend(map(lambda x: (x, expr[1:], (node,pather)), node.get((v, 'body'), ())))
    for p in sorted(points):
        if ast_symbol:
            yield (ast.dump(p['self']))
            yield ('='*40)
        else:
            yield ('\n'.join('\n'.join(
                parseCode[max(0, pn-1-B):min(len(parseCode)-1, pn-1+A)])
                for pn in p[::-1]))
            yield ('='*40+'{'+str(p)+'}')


found.ast = {
            'import': (ast.Import, ast.ImportFrom),
            'class': (ast.ClassDef,),
            'def': (ast.FunctionDef,),
            'It': (ast.Tuple, ast.List),
            'Expr': (ast.Expr,),
            'if': (ast.If,),
            'Assign': (ast.Assign,),
            'Loop': (ast.For, ast.While)
            }

def main():
    import argparse
    parser = argparse.ArgumentParser(description='astgrep')

    parser.add_argument('-e', help='expr', type=str)
    parser.add_argument('-f', help='file', type=str, default='./')
    parser.add_argument('-a', help='file', type=int, default=1)
    parser.add_argument('-b', help='file', type=int, default=0)
    parser.add_argument('--ast', action='store_true')
    args = parser.parse_args()
    print(args.e, args.f, args.b, args.a)
    if not args.f.endswith('/'):
        for a in found(
                args.e,
                open(args.f, 'r').read(),
                B=args.b,
                A=args.a,
                ast_symbol=args.ast):
            print(a)
    else:
        import os

        def walk(root):
            for path, subdirs, files in os.walk(root):
                for name in files:
                    yield os.path.join(path, name)

        import time
        a = time.clock()
        for f in filter(lambda x: x.endswith('.py'), walk(args.f)):
            b = time.clock()
            print(b-a, f)
            a = b
            sol = found(
                    args.e,
                    open(f, 'r').read(),
                    B=args.b,
                    A=args.a,
                    ast_symbol=args.ast)
            try:
                it1 = next(sol)
                print('===================>{}<================='.format(f))
                print(it1)
            except StopIteration:
                continue
            for it in sol:
                print(it)


if __name__ == '__main__':
    main()
