#with open("programme.mini.txt", "r", encoding="utf-8") as file:
 #   code = file.read()
from errors import AlgoTNError
def tokenize(code) :
    def error(message, position):
        line = code.count("\n", 0, position) + 1
        raise AlgoTNError(message, line)
    pos=0
    token=[]
    while pos<len(code) :
        if code[pos].isdigit() :
            nnum=""
            while pos < len(code) and (code[pos].isdigit() or code[pos]==".") :
                nnum+=code[pos]
                pos+=1
            if nnum.find('.')==-1 :    
                token.append(["NUMBER",int(nnum)])
            elif nnum.find('.')<len(nnum)-1 and nnum[nnum.find('.')+1:].find(".")==-1 :
                token.append(["FLOAT",float(nnum)])
            else :
                raise error(f"Nombre invalide : {nnum}", pos)
        #elif code[pos]==" ":
           # token.append(["BLANK","."])
           # pos+=1
        elif code[pos].isspace() and code[pos] != "\n":
            pos += 1
        elif code[pos]=="\n" :
            token.append(["NEWLINE","\n"])
            pos+=1
        elif code[pos:pos+8].upper() == "TANT QUE" and (pos+8 == len(code) or not (code[pos+8].isalnum() or code[pos+8] == "_")):
            token.append(["KEYWORD", "while"])
            pos+=8
        elif code[pos:pos+7].lower() in {"jusqu'a","jusqu'à"} and (pos+7 == len(code) or not (code[pos+7].isalnum() or code[pos+7] == "_")):
            token.append(["KEYWORD", "until"])
            pos+=7
        elif code[pos].isalpha() or code[pos] == "_":
            name = ""
            while pos < len(code) and (code[pos].isalnum() or code[pos] == "_"):
                name += code[pos]
                pos += 1
            keywords = {
                "SI": "if",
                "SINON": "else",
                "FIN": "end",
                "REPETER": "repeat",
                "FONCTION": "func",
                "PROCEDURE" : "procedure",
                "RETOURNER": "return",
                "ALORS": "then",
                "FAIRE": "procede",
                "POUR" : "for",
                "DE" : "from",
                "PAS" : "pas",
                "DEBUT": "start",
                "TABLEAU" : "tableau",
                "NOUVEAU_TYPE" : "nt",
                "PROCÉDURE" : "procedure",
                "DÉBUT":"start",
                "RÉPÉTER":"repeat",
                "RÉPETER":"repeat",
                "REPÉTER":"repeat",
                "TDOL":"tdol",
                "TDOG":"tdog"
            }
            logicops={
                "ET" : "and",
                "OU" : "or",
                "NON" : "not"
            }
            types={
                "ENTIER": "int",
                "BOOLEAN": "bool",
                "REEL": "reel",
                "CHAINE": "string",
                "ENTIERS": "int",
                "BOOLEANS": "bool",
                "REELS": "reel",
                "RÉELS": "reel",
                "REÉLS": "reel",
                "RÉÉLS": "reel",
                "CHAINES": "string"
            }
            arith={
                "MOD":"mod",
                "DIV":"div"
            }
            if name.upper() == "VRAI":
                token.append(["BOOLEAN", True])
            elif name.upper() == "FAUX":
                token.append(["BOOLEAN", False])
            elif name.upper() in keywords:
                token.append(["KEYWORD", keywords[name.upper()]])
            elif name.upper() in types:
                token.append(["TYPE", types[name.upper()]])
            elif name.upper() in arith:
                token.append([name.upper(), arith[name.upper()]])
            elif name.upper() in logicops:
                token.append(["LOGIC", logicops[name.upper()]])
            elif name.lower()=="à" :
                token.append(["KEYWORD","to"])
            else:
                token.append(["IDENTIFIER", name.upper()])
        elif code[pos]=="\"" :
            s=code.find("\"",pos+1)
            if s==-1 :
                raise error("Guillemet fermant manquant", pos)
            else :
                token.append(["STRING",code[pos+1:s]])
                pos=s+1
        elif code[pos] == "@":
            token.append(["KEYWORD", "pa"])
            pos += 1
        elif code[pos] == ":":
            token.append(["COLON", ":"])
            pos += 1
        elif code[pos:pos+2]=="<-":
            token.append(["APPEND","<-"])
            pos+=2
        elif code[pos]=="+" :
            token.append(["PLUS","+"])
            pos+=1
        elif code[pos]=="-" :
            token.append(["REDUCE","-"])
            pos+=1
        elif code[pos]=="*" :
            token.append(["MULTIPLY","*"])
            pos+=1
        elif code[pos]=="/" :
            token.append(["DIVIDE","/"])
            pos+=1
        elif code[pos]=="(" :
            token.append(["LPAR","("])
            pos+=1
        elif code[pos]==")" :
            token.append(["RPAR",")"])
            pos+=1
        elif code[pos]=="[" :
            token.append(["LMO","["])
            pos+=1
        elif code[pos]=="]" :
            token.append(["RMO","]"])
            pos+=1
        elif code[pos]=="," :
            token.append(["COMMA",","])
            pos+=1
        elif pos<len(code)-2 and code[pos:pos+3].upper()=="MOD" :
                    token.append(["MOD","%"])
                    pos+=3
        elif pos<len(code)-2 and code[pos:pos+3]=="DIV" :
                    token.append(["DIV","div"])
                    pos+=3
        elif pos<len(code)-1 and code[pos:pos+2]==">=" :
            token.append(["MOREQ",">="])
            pos+=2
        elif pos<len(code)-1 and code[pos:pos+2]=="<=" :
            token.append(["LOREQ","<="])
            pos+=2
        elif pos<len(code)-1 and code[pos:pos+2]=="!=" :
            token.append(["NEQ","!="])
            pos+=2
        elif code[pos]=="=" :
            token.append(["EQ","="])
            pos+=1
        elif code[pos]=="<" :
            token.append(["LESS","<"])
            pos+=1
        elif code[pos]==">" :
            token.append(["MORE",">"])
            pos+=1
        #elif pos<len(code)-3 and code[pos:pos+4]=="Vrai" :
         #   token.append(["BOOLEAN","True"])
          #  pos+=4
        #elif pos<len(code)-3 and code[pos:pos+4]=="Faux" :
         #   token.append(["BOOLEAN","False"])
          #  pos+=4
        else :
            error(f"Caractère inconnu : {code[pos]!r}", pos)
    token.append(["EOF", None])
    return token
if __name__ == "__main__":
    with open("programme.mini.txt", encoding="utf-8") as file:
        code = file.read()
    print(tokenize(code))