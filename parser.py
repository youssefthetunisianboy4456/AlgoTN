from lexer import tokenize
from errors import AlgoTNError

standardvalues = {
            "int": 0,
            "bool": True,
            "reel": 0.0,
            "string": ""
        }

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.node_lines = {}
    def line_number(self):
        return 1 + sum(
            1 for token in self.tokens[:self.pos]
            if token[0] == "NEWLINE"
        )

    def error(self, message):
        raise AlgoTNError(message, self.line_number())
    def first_token(self):
        return self.tokens[self.pos]

    def removefirst(self, expected):
        current = self.first_token()

        if current[0] != expected:
            self.error(f"Jeton {expected} attendu, reçu {current}")
        self.pos += 1
        return current
    #---------------------------------math-------------------------------------------------
    def factor(self):
        current = self.first_token()

        if current[0] == "NUMBER":
            self.removefirst("NUMBER")
            return ("number", current[1])
        
        if current[0] == "FLOAT":
                    self.removefirst("FLOAT")
                    return ("float", current[1])

        elif current[0] == "IDENTIFIER":
                name = self.removefirst("IDENTIFIER")[1]
                if self.first_token()[0]!="LMO" :
                    if self.first_token()[0] == "LPAR":
                        self.removefirst("LPAR")
                        params = []
                        if self.first_token()[0] != "RPAR":
                            while True:
                                params.append(self.logic())
                                if self.first_token()[0] != "COMMA":
                                    break
                                self.removefirst("COMMA")
                        self.removefirst("RPAR")
                        return ("call", name, params)
                    return ("variable", name)
                else :
                    self.removefirst("LMO")
                    pos=self.logic()
                    self.removefirst("RMO")
                    if self.first_token()[0] !="ASSIGN" :
                        return("subs",name,pos)
        elif current[0] == "STRING":
            self.removefirst("STRING")
            return ("string", current[1])

        elif current[0] == "BOOLEAN":
            self.removefirst("BOOLEAN")
            return ("boolean", current[1])

        elif current[0] == "LPAR":
            self.removefirst("LPAR")

            node = self.logic()
            self.removefirst("RPAR")
            return node
        elif current[0] == "REDUCE":
            self.removefirst("REDUCE")
            return ("negative", self.factor())

        else:
            raise SyntaxError( f"Jeton inattendu: {current}"  )
    def term(self):
        node = self.factor()

        while self.first_token()[0] in ("MULTIPLY", "DIVIDE","MOD","DIV"):
            operator = self.first_token()[0]
            self.removefirst(operator)

            right = self.factor()

            node = ("binary", operator, node, right)

        return node
    def expression(self):
        node = self.term()

        while self.first_token()[0] in ("PLUS", "REDUCE"):
            operator = self.first_token()[0]
            self.removefirst(operator)

            right = self.term()

            node = ("binary", operator, node, right)

        return node
    def assignment(self) :
        var_name = self.removefirst("IDENTIFIER")[1]
        self.removefirst("APPEND")

        if self.first_token()[0] == "LMO":
            self.removefirst("LMO")
            parts = []

            if self.first_token()[0] != "RMO":
                while True:
                    parts.append(self.logic())

                    if self.first_token()[0] != "COMMA":
                        break

                    self.removefirst("COMMA")

            self.removefirst("RMO")
            return ("tab", var_name, parts)
        return ("assign", var_name, self.logic())
    def comparison(self) :
        node=self.expression()

        compareOperators=["MOREQ","LOREQ","NEQ","MORE","LESS","EQ"]

        if self.first_token()[0] in compareOperators:
            #node=("compare", self.removefirst(self.first_token()[0])[1],node,self.expression())
            left=self.removefirst(self.first_token()[0])[1]
            node
            middle=self.expression()
            if self.first_token()[0] in compareOperators :
                node=("triplecompare", node,left,middle,self.removefirst(self.first_token()[0])[1],self.expression())
            else :
                node=("compare", left,node,middle)
        return node
    #--------------------logic------------------------------------------------------------
    def logic(self):
        node = self.logic_and()
        while self.first_token() == ["LOGIC", "or"]:
            self.removefirst("LOGIC")   
            node = ("logic", "or", node, self.logic_and())
        return node
    def logic_and(self):
        node = self.logic_not()
        while self.first_token() == ["LOGIC", "and"]:
            self.removefirst("LOGIC")
            node = ("logic", "and", node, self.logic_not())
        return node
    def logic_not(self):
        if self.first_token() == ["LOGIC", "not"]:
            self.removefirst("LOGIC")
            return ("not", self.logic_not())
        return self.comparison()
    #-------------------------end-math------------------------------------------
    def statement(self) :
        if self.first_token() == ["KEYWORD", "if"]:
            return self.parse_if()
        if self.first_token() == ["KEYWORD", "func"]:
                return self.parse_func()
        if self.first_token() == ["KEYWORD", "procedure"]:
                return self.parse_procedure()
        elif self.first_token() == ["KEYWORD", "while"]:
            return self.parse_while()
        elif self.first_token() == ["KEYWORD", "repeat"]:
            return self.parse_repeat()
        elif self.first_token() == ["KEYWORD", "for"]:
            return self.parse_for()
        elif self.first_token() == ["KEYWORD", "return"]:
            return self.parse_return()
        elif self.first_token() ==["KEYWORD","nt"] :
            self.removekeyword("nt")
            name=self.removefirst("IDENTIFIER")[1]
            self.removefirst("EQ")
            self.removekeyword("tableau")
            self.removekeyword("from")
            number=self.logic()
            typeout=self.removefirst("TYPE")[1]
            return ("nt",name,number,typeout)
        elif self.first_token()[0]== "IDENTIFIER" and self.tokens[self.pos+1][0]=="APPEND" :
            return self.assignment()
        else :
            expr = self.logic()

            if expr[0] == "subs" and self.first_token()[0] == "APPEND":
                self.removefirst("APPEND")
                return ("assigntab", expr[1], expr[2], self.logic())

            return expr
    def removekeyword(self,expected) :
        current=self.first_token()
        kre = {
            "if": "SI",
            "else": "SINON",
            "end": "FIN",
            "repeat": "REPETER",
            "func": "FONCTION",
            "procedure": "PROCEDURE",
            "return": "RETOURNER",
            "then": "ALORS",
            "procede": "FAIRE",
            "for": "POUR",
            "from": "DE",
            "pas": "PAS",
            "start": "DEBUT",
            "tableau": "TABLEAU",
            "nt": "NOUVEAU_TYPE",
            "to": "à",
            "until": "JUSQU'A",
            "while": "TANT QUE",
            "pa": "@",
            "tdol":"TDOL"
        }
        if current!=["KEYWORD",expected] :
             self.error( f"Mot-clé {kre[expected]}, reçu {current}" )
        self.removefirst("KEYWORD")
    #-----------------------------nests------------------------------------------------
    def parse_if(self) :
        self.removekeyword("if")

        condition = self.logic()

        self.removekeyword("then")
        self.removefirst("NEWLINE")

        insideif=self.parse_block({"else","end"})
        conditions=[]
        executions=[]
        while self.first_token()==["KEYWORD","else"] :
            self.removekeyword("else")
            if self.first_token()==["KEYWORD","if"] :
                self.removekeyword("if")
                conditions.append(self.logic())
                self.removekeyword("then")
                self.removefirst("NEWLINE")
                executions.append(self.parse_block({"else","end"}))
            else : 
                self.removefirst("NEWLINE")
                conditions.append("else_condition")
                executions.append(self.parse_block({"end"}))
        self.removekeyword("end")
        self.removekeyword("if")

        return("if",condition,insideif,conditions,executions)
    def parse_while(self) :
        self.removekeyword("while")

        condition = self.logic()

        self.removekeyword("procede")
        self.removefirst("NEWLINE")

        insidewhile=self.parse_block({"end"})

        
        self.removekeyword("end")
        self.removekeyword("while")

        return("while",condition,insidewhile)
    def parse_repeat(self) :
        self.removekeyword("repeat")
        self.removefirst("NEWLINE")

        insiderepeat=self.parse_block({"until"})
        
        self.removekeyword("until")
        condition = self.logic()
        

        return("repeat",condition,insiderepeat)
    def parse_for(self):
        self.removekeyword("for")

        counter = self.removefirst("IDENTIFIER")[1]

        self.removekeyword("from")
        start = self.expression()

        self.removekeyword("to")
        end = self.expression()

        params = [start, end]

        if self.first_token() == ["KEYWORD", "pas"]:
            self.removekeyword("pas")
            params.append(self.expression())

        self.removekeyword("procede")
        self.removefirst("NEWLINE")

        insidefor = self.parse_block({"end"})

        self.removekeyword("end")
        self.removekeyword("for")

        return ("for", ("variable",counter) , params, insidefor)
    #--------------------------end-nests--------------------------------------
    def parse_return(self):
        self.removekeyword("return")
        expression=self.logic()
        return ("return",expression)
    def parse_func(self) :
        self.removekeyword("func")
        name=self.removefirst("IDENTIFIER")[1]
        self.removefirst("LPAR") 
        localvars=[]

        if self.first_token()[0] != "RPAR":
            while True:
                lovalvarname = self.removefirst("IDENTIFIER")[1]
                self.removefirst("COLON")
                if self.first_token()[0]=="TYPE" :
                    localvartype = self.removefirst("TYPE")[1]
                elif self.first_token()[0]=="IDENTIFIER" :
                    localvartype = self.removefirst("IDENTIFIER")[1]
                localvars.append((lovalvarname, localvartype))
                if self.first_token()[0] != "COMMA":
                    break
                self.removefirst("COMMA")

        self.removefirst("RPAR")
        self.removefirst("COLON")
        outputype=self.removefirst("TYPE")[1]
        self.removefirst("NEWLINE")
        self.removekeyword("start")
        self.removefirst("NEWLINE")
        func_body=self.parse_block({"end"})
        self.removekeyword("end")
        if self.first_token()!=["KEYWORD","tdol"] :
            return ("function",name,localvars,outputype,func_body,"####notdol####")
        else :
             self.removefirst("NEWLINE")
             self.removekeyword("tdol")
             self.removefirst("NEWLINE")
             tdolvars={}
             while True:
                tdolvarname = self.removefirst("IDENTIFIER")[1]
                self.removefirst("COLON")
                if self.first_token()[0]=="TYPE" :
                    tdolvartype = self.removefirst("TYPE")[1]
                elif self.first_token()[0]=="IDENTIFIER" :
                    tdolvartype = self.removefirst("IDENTIFIER")[1]
                tdolvars[tdolvarname]= tdolvartype
                if self.first_token()[0] != "NEWLINE":
                    break
                self.removefirst("NEWLINE")
                return ("function",name,localvars,outputype,func_body,tdolvars)
    def parse_procedure(self):
        self.removekeyword("procedure")
        name = self.removefirst("IDENTIFIER")[1]
        self.removefirst("LPAR")
        parameters = []
        if self.first_token()[0] != "RPAR":
            while True:
                mode = "value"
                if self.first_token() == ["KEYWORD", "pa"]:
                    self.removekeyword("pa")
                    mode = "reference"
                param_name = self.removefirst("IDENTIFIER")[1]
                self.removefirst("COLON")
                if self.first_token()[0]=="TYPE" :
                    param_type = self.removefirst("TYPE")[1]
                elif self.first_token()[0]=="IDENTIFIER" :
                    param_type = self.removefirst("IDENTIFIER")[1]
                parameters.append((mode, param_name, param_type))
                if self.first_token()[0] != "COMMA":
                    break
                self.removefirst("COMMA")
        self.removefirst("RPAR")
        self.removefirst("NEWLINE")
        self.removekeyword("start")
        self.removefirst("NEWLINE")
        body = self.parse_block({"end"})
        self.removekeyword("end")
        self.removefirst("NEWLINE")
        if self.first_token()!=["KEYWORD","tdol"] :
            return ("procedure", name, parameters, body,"####notdol####")
        else :
            self.removekeyword("tdol")
            self.removefirst("NEWLINE")
            tdolvars={}
            while True:
                tdolvarname = self.removefirst("IDENTIFIER")[1]
                self.removefirst("COLON")
                if self.first_token()[0]=="TYPE" :
                    tdolvartype = self.removefirst("TYPE")[1]
                elif self.first_token()[0]=="IDENTIFIER" :
                    tdolvartype = self.removefirst("IDENTIFIER")[1]
                tdolvars[tdolvarname]= tdolvartype
                if self.first_token()[0] != "COMMA":
                    break
                self.removefirst("COMMA")
            return ("procedure",name,parameters,body,tdolvars)
    #----------------------------parse-block-----------------------------------------------
    def parse_block(self,stoppers) :
        statements=[]
        while self.first_token()[0]!="EOF" :
            current=self.first_token()
            if current[0]=="NEWLINE" : 
                self.removefirst("NEWLINE")
                continue
            if current[0]=="KEYWORD" and current[1] in stoppers : 
                break
            line = self.line_number()
            statement = self.statement()

            self.node_lines[id(statement)] = line
            statements.append(statement)
            if self.first_token()[0] not in ["EOF","NEWLINE"] :
                self.error(f"Supposé fin de ligne mais a reçu {self.first_token()}")
        return statements
    def parse(self):
        statements = self.parse_block(set())

        self.removefirst("EOF")

        return ("program", statements)
if __name__ == "__main__":
    with open("programme.mini.txt", encoding="utf-8") as file:
        code = file.read()

    tokens = tokenize(code)
    parser = Parser(tokens)

    tree = parser.parse()
    print(tree)