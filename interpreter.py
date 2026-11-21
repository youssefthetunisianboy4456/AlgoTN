from lexer import tokenize
from parser import Parser
from copy import deepcopy
from random import randint
from math import sqrt
from errors import AlgoTNError
import get_tabs
# print(get_tabs.all_tabs)


class Interpreter:
    def __init__(self):
        self.initialvars = {}
        self.initialtabs = {}
        self.initialfuncs = {}
        self.initialprocedures = {}
        self.variables = {}
        self.functions = {}
        self.procedures = {}
        self.tabs = {}
        self.types = {}
        self.node_lines = {}
        self.cc = "----------SUPERSUPERSPECIALNOWHEREITHASENDED"

    def construct(self, tdos):  # "TDOL de x"
        tdog = {}
        tdols = {}
        for part in tdos:
            if part["name"] == "TDOG":
                tdog = part["data"]
            elif part["name"] == "TDNT":
                tdnt = part["data"]
            elif part["name"].startswith("TDOL de "):
                tdols[part["name"][8:]] = part["data"]
            else:
                raise AlgoTNError(f"C quoi ce tableau: {part}")
        types = {
            "CARACTERE": "strshort",
            "ENTIER": "int",
            "BOOLEAN": "bool",
            "REEL": "reel",
            "CHAINE": "string",
            "ENTIERS": "int",
            "BOOLEANS": "bool",
            "BOOLEEN":"bool",
            "REELS": "reel",
            "RÉELS": "reel",
            "REÉLS": "reel",
            "RÉÉLS": "reel",
            "CHAINES": "string",
        }
        firstvals = {
            "int": 0,
            "bool": True,
            "reel": 0.0,
            "string": "",
            "strshort": self.cc
        }
        # for tabtype,contenu in tdnt.items() :
        #     x=contenu.split()
        #     #NPO : detialed errors
        #     if not (len(x)==4 and x[0].upper()=="TABLEAU" and x[1].upper()=="DE" and x[2].isdigit() and x[3].upper() in types  ) :
        #         raise SyntaxError("\" TABLEAU \" ou \" DE \" ou nombre des cases ou type oubliés")
        #     self.types[tabtype]=[x[2],x[3]]
        # for var,type in tdog.items() :
        #     if type.upper() in types :
        #         self.initialvars[var]=firstvals[types[type.upper()]]
        #     elif type.upper() in self.types :
        #         self.create_tab(type.upper(),var)
        for var, type in tdog.items():
            if type.upper() in types:
                self.initialvars[var.upper()] = firstvals[types[type.upper()]]
            elif type.lower() in {"procédure", "procedure"}:
                self.initialprocedures[var.upper()] = "intdog"
            elif type.lower() in {"fonction", "function"}:
                self.initialfuncs[var.upper()] = "intdog"

    class ReturnSignal(Exception):
        def __init__(self, value):
            self.value = value

    def doall(self, x):
        for i in (x):
            self.execute(i)
    # Continue dealing with caracs

    def verifc(self, x):
        return type(x) is str and len(x) in {55, 54} and x.endswith(self.cc)

    def create_tab(self, typename, tabname):
        standardvalues = {
            "int": 0,
            "bool": True,
            "reel": 0.0,
            "string": ""
        }
        x = self.types[typename].copy()
        fresh = []
        num = x[0]
        type = x[1]
        standard = standardvalues[type]
        for i in range(num):
            fresh.append(standard)
        self.tabs[tabname] = fresh
        return fresh

    def execute_if(self, conditions, statements):
        for i in range(len(conditions)):
            if conditions[i] == "else_condition" or self.evaluate(conditions[i]):
                self.doall(statements[i])
                return None

    def check_index(self, tab, index):
        if type(index) is not int:
            raise AlgoTNError("L'indice doit être un entier")

        if index < 0 or index >= len(tab):
            raise AlgoTNError(
                f"Indice {index} hors limites pour un tableau de taille {len(tab)}"
            )

        return index

    def evaluate(self, node):
        kind = node[0]
        if kind in {"number", "float", "boolean"}:
            return node[1]
        elif kind == "string":
            if self.verifc(node[1]):
                return node[1]
            else:
                return node[1]
        elif kind == "variable":
            name = node[1]
            if name in self.tabs:
                return self.tabs[name]
            elif name not in self.variables:
                raise AlgoTNError(f"Variable non définie : {name}")
            elif self.verifc(self.variables[name]):
                return self.variables[name][0]
            else:
                return self.variables[name]
        elif kind == "binary":
            left = self.evaluate(node[2])
            right = self.evaluate(node[3])
            operator = node[1]
            if operator == "PLUS":
                return left + right
            elif operator == "REDUCE":
                return left - right
            elif operator == "MULTIPLY":
                return left * right
            elif operator == "DIVIDE":
                if right == 0:
                    raise AlgoTNError("Division par zéro")
                return left / right
            elif operator == "MOD":
                if right == 0:
                    raise AlgoTNError("Modulo par zéro")
                return left % right

            elif operator == "DIV":
                if right == 0:
                    raise AlgoTNError("Division entière par zéro")
                return left // right
            else:
                raise AlgoTNError(f"Opérateur {operator} inconnu")
        elif kind == "compare":
            left = self.evaluate(node[2])
            right = self.evaluate(node[3])
            operator = node[1]
            if operator == "≤":
                return left <= right
            elif operator == "≥":
                return left >= right
            elif operator == "<":
                return left < right
            elif operator == ">":
                return left > right
            elif operator == "=":
                return left == right
            elif operator == "≠":
                return left != right
            else:
                raise AlgoTNError(f"Opérateur {operator} inconnu")
        elif kind == "triplecompare":
            left = self.evaluate(node[1])
            operator1 = node[2]
            middle = self.evaluate(node[3])
            operator2 = node[4]
            right = self.evaluate(node[5])

            def comp(op, x, y):
                if op == "≤":
                    return x <= y
                elif op == "≥":
                    return x >= y
                elif op == "<":
                    return x < y
                elif op == ">":
                    return x > y
                elif op == "=":
                    return x == y
                elif op == "≠":
                    return x != y
                else:
                    raise AlgoTNError(f"Opérateur {op} inconnu")
            return comp(operator1, left, middle) and comp(operator2, middle, right)
        elif kind=="in" :
            tocheck=self.evaluate(node[1])
            listrec=node[2]
            checklist=[]
            for i in listrec :
                checklist.append(self.evaluate(i))
            return tocheck in checklist
        elif kind == "logic":
            left = self.evaluate(node[2])
            operator = node[1]
            if operator == "and":
                return bool(left) and bool(self.evaluate(node[3]))
            elif operator == "or":
                return bool(left) or bool(self.evaluate(node[3]))
            else:
                raise AlgoTNError(f"Opérateur {operator} inconnu")
        elif kind == "subs":
            name = node[1]
            if name in self.variables:
                x = self.variables[name]
            elif name in self.tabs:
                x = self.tabs[name]
            else:
                raise AlgoTNError(f"Pas de tableau ou chaine du caractères du nom : {name}")
            index = self.check_index(x, self.evaluate(node[2]))
            return x[index]
        elif kind == "not":
            return not(bool(self.evaluate(node[1])))
        elif kind == "negative":
            return -self.evaluate(node[1])
        elif kind == "call":
            name = node[1]
            if name.lower() in {"ecrire", "écrire"}:
                output = ""
                for argument in node[2]:
                    if type(self.evaluate(argument)) is bool:
                        if self.evaluate(argument)==True:
                            output+="Vrai"
                        else :
                            output+="Faux"
                    else:
                        output += str(self.evaluate(argument))
                print(output)
                return None
            elif name.upper() in {"ALEA", "ALÉA"}:
                if len(node[2]) != 2:
                    raise AlgoTNError("la fonction ALEA accepte exacetement 3 paramètres")
                start = self.evaluate(node[2][0])
                finish = self.evaluate(node[2][1])
                return randint(start, finish)
            elif name.upper() == "ABS":
                if len(node[2]) != 1:
                    raise AlgoTNError("La fonction ABS accepte exactement 1 paramètre")
                return abs(self.evaluate(node[2][0]))
            elif name.upper() in {"RACINE_CARREE", "RACINE_CARRÉE"}:
                if len(node[2]) != 1:
                    raise AlgoTNError("La fonction Racine_Carrée accepte exactement 1 paramètre")
                return sqrt(self.evaluate(node[2][0]))
            elif name.upper() == "CONVCH":
                if len(node[2]) != 1:
                    raise AlgoTNError("La fonction CONVCH accepte exactement 1 paramètre")
                argument = self.evaluate(node[2][0])
                return str(argument)
            elif name.upper() == "ORD":
                if len(node[2]) != 1:
                    raise AlgoTNError("La fonction ORD accepte exactement 1 paramètre")
                argument = self.evaluate(node[2][0])
                if len(argument) != 1:
                    raise AlgoTNError(f"Pour ORD, il faut avoir un caractère")
                return ord(argument)
            elif name.upper() == "CHR":
                if len(node[2]) != 1:
                    raise AlgoTNError("La fonction CHR accepte exactement 1 paramètre")
                argument = self.evaluate(node[2][0])
                return chr(argument)
            elif name.upper() == "VALEUR":
                if len(node[2]) != 1:
                    raise AlgoTNError("La fonction VALEUR accepte exactement 1 paramètre")
                argument = self.evaluate(node[2][0])
                return int(argument)
            elif name.upper() == "SOUS_CHAINE":
                if len(node[2]) != 3:
                    raise AlgoTNError("La fonction SOUS_CHAINE accepte exactement trois paramètres")
                val = self.evaluate(node[2][0])
                start = self.evaluate(node[2][1])
                fin = self.evaluate(node[2][2])
                if type(val) is str:
                    return val[start:fin]
                else:
                    raise AlgoTNError("La fonction SOUS_CHAINE nécessite une chaine des caractères")
            elif name.upper() in {"EFFACER", "ÉFFACER"}:
                if len(node[2]) != 3:
                    raise TypeError("La fonction EFFACER accepte exactement trois paramètres")
                val = self.evaluate(node[2][0])
                start = self.evaluate(node[2][1])
                fin = self.evaluate(node[2][2])
                if type(val) is str:
                    return val[:start] + val[fin:]
                else:
                    raise AlgoTNError("La fonction EFFACER attend un caractère ou une chaine des caratères")
            elif name.upper() == "POS":
                if len(node[2]) != 2:
                    raise AlgoTNError("La fonction POS accepte exactement deux paramètres")
                tofind = self.evaluate(node[2][0])
                tofindin = self.evaluate(node[2][1])
                if (type(tofind) is str) and (type(tofindin) is str):
                    return tofindin.find(tofind)
                else:
                    raise AlgoTNError("La fonction POS attend un caractère ou une chaine des caratères")
            elif name.upper() == "LONG":
                if len(node[2]) != 1:
                    raise AlgoTNError("La fonction LONG accepte exactement un paramètre")
                argument = self.evaluate(node[2][0])
                if not (type(argument) is str):
                    raise AlgoTNError("La fonction long attend un caractère ou une chaine de caractères")
                return len(argument)
            elif name.upper() =="MAJUS":
                if len(node[2])!=1:
                    raise AlgoTNError("La fonction MAJUS accepte exactement un paramètre")
                argument =self.evaluate(node[2][0])
                if not (type(argument) is str):
                    raise AlgoTNError("La fonction majus attend un caractère ou une chaine de caractères")
                return argument.upper()
            elif name.upper()=="ESTNUM" :
                if len(node[2])!=1:
                    raise AlgoTNError("La fonction ESTNUM accepte exactement un paramètre")
                argument =self.evaluate(node[2][0])
                if not (type(argument) is str):
                    raise AlgoTNError("La fonction majus attend un caractère ou une chaine de caractères")
                return argument.isdigit()
            elif name.upper() =="ENT":
                if len(node[2])!=1:
                    raise AlgoTNError("La fonction ENT accepte exactement un paramètre")
                argument = self.evaluate(node[2][0])
                if not (type(argument) is float):
                    raise AlgoTNError("La fonction ent attend un réel")
                return argument//1
            elif name.upper() =="ARRONDI":
                if len(node[2])!=1:
                    raise AlgoTNError("La fonction ARRONDI accepte exactement un paramètre")
                argument = self.evaluate(node[2][0])
                if not (type(argument) is float):
                    raise AlgoTNError("La fonction arrondi attend un réel")
                return round(argument)
            elif name.lower() == "ecrire_fin**special":
                output = ""
                x = len(node[2])
                for i in range(x - 1):
                    output += str(self.evaluate(node[2][i]))
                print(output, end=self.evaluate(node[2][x - 1]))
                #print(node[2][x-2])
                return None
            elif name[0:5] == "LIRE_I":
                if len(node[2]) == 0:
                    raise AlgoTNError("LIRE n'a reçue aucune variable")
                toprint = ""
                if len(node[2]) > 1:
                    for i in range(1, len(node[2])):
                        toprint += str(self.evaluate(node[2][i]))
                argument = node[2][0]
                if argument[0] not in {"variable", "subs"}:
                    raise AlgoTNError("La fonction LIRE attend une variable")
                elif argument[0] == "variable":
                    varname = argument[1]
                    if name[5:] == "ENTIER":
                        self.variables[varname] = int(input(toprint))
                    elif name[5:] == "BOOLEEN":
                        value = input(toprint).strip().upper()
                        if value == "VRAI":
                            self.variables[varname] = True
                        elif value == "FAUX":
                            self.variables[varname] = False
                        else:
                            raise AlgoTNError("VRAI ou FAUX attendus")
                    elif name[5:] == "CHAINE":
                        self.variables[varname] = str(input(toprint))
                    elif name[5:] == "REEL":
                        self.variables[varname] = float(input(toprint))
                    else:
                        raise AlgoTNError(f"Type {name[5:]} invalide à extraire")
                    return None
                elif argument[0] == "subs":
                    tabname = argument[1]
                    tabpos = argument[2]
                    if name[5:] == "ENTIER":
                        pos = self.check_index(self.tabs[tabname], self.evaluate(tabpos))
                        self.tabs[tabname][pos] = int(input(toprint))
                    elif name[5:] == "BOOLEEN":
                        pos = self.check_index(self.tabs[tabname], self.evaluate(tabpos))
                        value = input(toprint).strip().upper()
                        if value == "VRAI":
                            self.tabs[tabname][pos] = True
                        elif value == "FAUX":
                            self.tabs[tabname][pos] = False
                        else:
                            raise AlgoTNError("VRAI ou FAUX attendus")
                    elif name[5:] == "CHAINE":
                        pos = self.check_index(self.tabs[tabname], self.evaluate(tabpos))
                        self.tabs[tabname][pos] = str(input(toprint))
                    elif name[5:] == "REEL":
                        pos = self.check_index(self.tabs[tabname], self.evaluate(tabpos))
                        self.tabs[tabname][pos] = float(input(toprint))
                    else:
                        raise AlgoTNError(f"Type {name[5:]} invalide à extraire")
                    return None
            elif name == "LIRE":
                if len(node[2]) == 0:
                    raise AlgoTNError("LIRE n'a reçue aucune variable")
                toprint = ""
                if len(node[2]) > 1:
                    for i in range(1, len(node[2])):
                        toprint += str(self.evaluate(node[2][i]))
                argument = node[2][0]
                if argument[0] not in {"variable", "subs"}:
                    raise AlgoTNError("La fonction LIRE attend une variable")
                elif argument[0] == "variable":
                    varname = argument[1]
                    if varname not in self.variables:
                        if varname in self.initialvars:
                            var = self.initialvars[varname]
                        else:
                            raise AlgoTNError(f"Cette variable ne figure pas dans le TDO")
                    else :
                        var=self.variables[varname]
                    if self.verifc(var):
                        x = input(toprint)
                        if len(x) == 1:
                            self.variables[varname] = x + self.cc
                        else:
                            raise AlgoTNError("Saisie fausse")
                    elif type(var) is int:
                        try:
                            self.variables[varname] = int(input(toprint))
                        except:
                            raise AlgoTNError("Saisie fausse")
                    elif type(var) is bool:
                        try:
                            value = input(toprint).strip().upper()
                            if value == "VRAI":
                                self.variables[varname] = True
                            elif value == "FAUX":
                                self.variables[varname] = False
                            else:
                                raise AlgoTNError("VRAI ou FAUX attendus")
                        except:
                            raise AlgoTNError("Saisie fausse")
                    elif type(var) is str:
                        self.variables[varname] = str(input(toprint))
                    elif type(var) is float:
                        try:
                            self.variables[varname] = float(input(toprint))
                        except:
                            raise AlgoTNError("Saisire fausse")
                    else:
                        raise AlgoTNError(f"Type {name[5:]} invalide à extraire")
                    return None
            elif name in self.functions:
                params = []
                for i in range(len(node[2])):
                    params.append(self.evaluate(node[2][i]))
                func = self.functions[name]
                vars = func[2]
                out = func[3]
                body = func[4]
                types = {
                    "int": int,
                    "bool": bool,
                    "reel": float,
                    "string": str,
                    "list": list
                }

                if len(params) != len(vars):
                    raise AlgoTNError(
                        "Pramètres non-nécessaires ou manquants : vérifiez l'ordre et le nombre des paramères")

                old_variables = self.variables
                old_tabs = self.tabs
                self.variables = old_variables.copy()
                self.tabs = deepcopy(old_tabs)

                try:
                    for i in range(len(params)):
                        currentvar = vars[i][0]
                        currentvalue = params[i]
                        currenttype = vars[i][1]

                        if not((currenttype == "int" and (type(currentvalue) is int)) or
                               (currenttype == "bool" and (type(currentvalue) is bool)) or
                               (currenttype == "reel" and (type(currentvalue) is float)) or
                               (currenttype == "string" and (type(currentvalue) is str)) or
                                (currenttype == "list" and (type(currentvalue) is list))):
                            raise TypeError(f"Expected {currenttype} got {type(currentvalue)}")
                        if currenttype in {"int", "bool", "reel", "string"}:
                            self.variables[currentvar] = currentvalue
                        else:
                            self.tabs[currentvar] = currentvalue

                    try:
                        self.doall(body)
                    except self.ReturnSignal as signal:
                        result = signal.value

                        if type(result) is not types[out]:
                            raise AlgoTNError(f"Type de retour inconnu: {out}")

                        return result

                    raise AlgoTNError(f"La fonction {name} n'a pas une valeur de retour")

                finally:
                    self.variables = old_variables
                    self.tabs = old_tabs
            elif name in self.procedures:
                procedure = self.procedures[name]
                vars = procedure[2]
                body = procedure[3]
                types = {
                    "int": int,
                    "bool": bool,
                    "reel": float,
                    "string": str
                }

                standardvalues = {
                    "int": 0,
                    "bool": True,
                    "reel": 0.0,
                    "string": ""
                }

                if len(node[2]) != len(vars):
                    raise AlgoTNError(
                        "Pramatère non-nécessaire ou manquant : vérifiez l'ordre et le nombre des paramères")

                params = []
                references = []

                for i in range(len(vars)):
                    currentpassage = vars[i][0]
                    currentvar = vars[i][1]
                    currenttype = vars[i][2]
                    argument = node[2][i]

                    if currentpassage == "reference":
                        if argument[0] != "variable":
                            raise AlgoTNError("Passage par Reference nécessite une variable")

                        originalname = argument[1]

                        if originalname in self.variables:
                            currentvalue = self.variables[originalname]
                        elif originalname in self.tabs:
                            currentvalue = self.tabs[originalname]
                        elif currenttype in standardvalues:
                            currentvalue = standardvalues[currenttype]
                        elif currenttype in self.types:
                            currentvalue = self.create_tab(currenttype, originalname)
                        else:
                            raise AlgoTNError(f"Type inconnu: {currenttype}")

                        references.append((currentvar, originalname, currenttype))

                    elif currentpassage == "value":
                        currentvalue = self.evaluate(argument)

                    else:
                        raise RuntimeError("Unknown parameter mode")

                    if currenttype in types:
                        if type(currentvalue) is not types[currenttype]:
                            raise TypeError(f"Expected {currenttype}, got {type(currentvalue)}")
                    elif currenttype in self.types:
                        if type(currentvalue) is not list:
                            raise TypeError(f"Expected {currenttype}, got {type(currentvalue)}")
                    else:
                        raise AlgoTNError(f"Type inconnu: {currenttype}")

                    params.append((currentvar, currentvalue))

                old_variables = self.variables
                old_tabs = self.tabs
                self.variables = old_variables.copy()
                self.tabs = deepcopy(old_tabs)

                try:
                    for i in range(len(params)):
                        currentvar, currentvalue = params[i]
                        currenttype = vars[i][2]
                        if currenttype in types:
                            self.variables[currentvar] = currentvalue
                        elif currenttype in self.types:
                            self.tabs[currentvar] = deepcopy(currentvalue)
                        else:
                            raise AlgoTNError(f"Type inconnu: {currenttype}")
                    try:
                        self.doall(body)
                    except self.ReturnSignal:
                        raise AlgoTNError("Ne pas mettre \" RETOURNER \" dans une procédure")

                    updatesvar = {}
                    updatestab = {}
                    for currentvar, originalname, currenttype in references:
                        if currenttype in types:
                            value = self.variables[currentvar]
                        elif currenttype in self.types:
                            value = self.tabs[currentvar]
                        else:
                            raise AlgoTNError(f"Type inconnue: {currenttype}")

                        if currenttype in types:
                            if type(value) is not types[currenttype]:
                                raise TypeError(f"Expected {currenttype}")
                        elif currenttype in self.types:
                            if type(value) is not list:
                                raise TypeError(f"Expected {currenttype}")
                        else:
                            raise AlgoTNError(f"Type inconnue: {currenttype}")
                        if currenttype in {"int", "bool", "reel", "string"}:
                            updatesvar[originalname] = value
                        else:
                            updatestab[originalname] = value

                    old_variables.update(updatesvar)
                    old_tabs.update(updatestab)

                finally:
                    self.variables = old_variables
                    self.tabs = old_tabs

                return None
            else:
                raise AlgoTNError(f"Fonction ou procédure inconnue: {name}")
        else:
            raise AlgoTNError(f"Expression inconnue: {kind}")

    def _execute_node(self, node):
        kind = node[0]
        if kind == "assign":
            if node[1] in self.variables:
                if self.verifc(self.variables[node[1]]):
                    if type(self.evaluate(node[2])) is str and len(self.evaluate(node[2])) != 1:
                        raise AlgoTNError("Cractère pas plus que longeur 1")
                    else:
                        self.variables[node[1]] = self.evaluate(node[2]) + self.cc
                elif type(self.evaluate(node[2])) != type(self.variables[node[1]]):
                    raise AlgoTNError("Il est impossible de changer le type d'une vaibale dans un algorithme")
                else:
                    self.variables[node[1]] = self.evaluate(node[2])
            elif node[1] in self.initialvars:
                inival = self.initialvars[node[1]]
                value = self.evaluate(node[2])
                if self.verifc(inival):
                    if len(value) == 1:
                        self.variables[node[1]] = value + self.cc
                    else:
                        raise AlgoTNError("La longeur d'un caractère ne peut pas dépasser 1")
                elif type(value) != type(inival):
                    raise AlgoTNError(f"Le type de {node[1]} dans le TDO est différent que celui dans l'appel")
                else:
                    self.variables[node[1]] = value
            else:
                # print(initial.vars)
                raise AlgoTNError(f"Cette variable n'est pas dans le TDO")
        elif kind == "nt":
            self.types[node[1]] = [self.evaluate(node[2]), node[3]]
        elif kind == "assigntab":
            name = node[1]
            pos = self.evaluate(node[2])
            newval = self.evaluate(node[3])
            if name in self.tabs:
                pos = self.check_index(self.tabs[name], pos)
                self.tabs[name][pos] = newval

            else:
                raise AlgoTNError(f"Pas de tableau de nom: {name}")
        elif kind == "tab":
            fresh = []
            for part in node[2]:
                fresh.append(self.evaluate(part))
            self.tabs[node[1]] = fresh
        elif kind == "tabfresh":
            standardvalues = {
                "int": 0,
                "bool": True,
                "reel": 0.0,
                "string": ""
            }
            fresh = []
            type_in = node[3]
            default = standardvalues[type_in]
            for i in range(self.evaluate(node[2])):
                fresh.append(default)
            self.tabs[node[1]] = fresh
        elif kind == "return":
            value = self.evaluate(node[1])
            raise self.ReturnSignal(value)
        elif kind == "if":
            self.execute_if([node[1], *node[3]], [node[2], *node[4]])
        elif kind == "while":
            while self.evaluate(node[1]):
                for i in (node[2]):
                    self.execute(i)
        elif kind == "repeat":
            self.doall(node[2])
            while not(self.evaluate(node[1])):
                self.doall(node[2])
        elif kind == "for":
            params = node[2]
            a = self.evaluate(params[0])
            b = self.evaluate(params[1])
            name = node[1][1]
            self.variables[name] = a
            if len(params) == 3:
                x = self.evaluate(params[2])
                if x != 0:
                    pas = x
                else:
                    raise AlgoTNError("Pas égal à 0")
            else:
                pas = 1
            if name in self.initialvars:
                if type(a) is int and type(b) is int:
                    if type(self.initialvars[name]) is int:
                        for SUPERSUPERSPECIALSUPERSUPERCOUNTER in range(a, b + (1 if pas > 0 else -1), pas):
                            self.variables[name] = SUPERSUPERSPECIALSUPERSUPERCOUNTER
                            self.doall(node[3])
                        # self.variables.pop(name)
                    else:
                        raise AlgoTNError("Un compteur d'entiers c un entier dans le TDO")
                elif self.verifc(a) and self.verifc(b):
                    if self.verifc(self.initialvars[name]):
                        a = ord(a[0])
                        b = ord(b[0])
                        for SUPERSUPERSPECIALSUPERSUPERCOUNTER in range(a, b + (1 if pas > 0 else -1), pas):
                            self.variables[name] = chr(SUPERSUPERSPECIALSUPERSUPERCOUNTER)
                            self.doall(node[3])
                        # self.variables.pop(name)
                    else:
                        raise AlgoTNError("Un compteur de caractères est un caractères dans le TDO")
                else:
                    raise AlgoTNError(
                        f"Le début et la fin de pour ne sont ni des entiers ni des caractères ou sont de types différents")
            else:
                raise AlgoTNError(f"Le compteur {name.lower()} n'est pas encore initialisé dans le TDOG")
        elif kind == "function":
            self.functions[node[1]] = node
        elif kind == "procedure":
            self.procedures[node[1]] = node
        elif kind == "call":
            self.evaluate(node)
        else:
            raise AlgoTNError(f"Phrase inconnue {kind}")

    def execute(self, node):
        try:
            # print(get_tabs.all_tabs)
            return self._execute_node(node)

        except AlgoTNError as error:
            if error.line is None:
                line = self.node_lines.get(id(node))

                raise AlgoTNError(
                    error.message,
                    line
                ) from None

            raise

    def run(self, tree):
        if tree[0] != "program":
            raise AlgoTNError("Programme atteundu")
        #print(self.verifc("A----------SUPERSUPERSPECIALNOWHEREITHASENDED"))
        self.construct(get_tabs.all_tabs)

        for statement in tree[1]:
            self.execute(statement)
            # print(get_tabs.all_tabs)
        #print("x", self.initialvars)


if __name__ == "__main__":
    try:
        with open("programme.mini.txt", encoding="utf-8") as file:
            code = file.read()

        tokens = tokenize(code)

        parser = Parser(tokens)
        tree = parser.parse()

        interpreter = Interpreter()
        interpreter.node_lines = parser.node_lines

        interpreter.run(tree)

    except AlgoTNError as error:
        print(f"ERREUR : {error}")
        raise SystemExit(1)

    #print("Variables:", interpreter.variables)
    #print("Tabs:", list(interpreter.tabs))
    #print("Types:", interpreter.types)
