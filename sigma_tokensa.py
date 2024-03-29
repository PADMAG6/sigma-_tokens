import re
from exceptions import SigmaParseError,AggregationsNotImplemented
from sigma.baseparser import BaseParser

COND_NONE = 0
COND_AND  = 1
COND_OR   = 2
COND_NOT  = 3
COND_NULL = 4



# Condition Tokenizer
class SigmaConditionToken:
    """Token of a Sigma condition expression"""
    TOKEN_AND    = 1
    TOKEN_OR     = 2
    TOKEN_NOT    = 3
    TOKEN_ID     = 4
    TOKEN_LPAR   = 5
    TOKEN_RPAR   = 6
    TOKEN_PIPE   = 7
    TOKEN_ONE    = 8
    TOKEN_ALL    = 9
    TOKEN_AGG    = 10
    TOKEN_EQ     = 11
    TOKEN_LT     = 12
    TOKEN_LTE    = 13
    TOKEN_GT     = 14
    TOKEN_GTE    = 15
    TOKEN_BY     = 16
    TOKEN_NEAR   = 17

    tokenstr = [
            "INVALID",
            "AND",
            "OR",
            "NOT",
            "ID",
            "LPAR",
            "RPAR",
            "PIPE",
            "ONE",
            "ALL",
            "AGG",
            "EQ",
            "LT",
            "LTE",
            "GT",
            "GTE",
            "BY",
            "NEAR",
            ]

    def __init__(self, tokendef, match, pos):
        self.type = tokendef[0]
        self.matched = match.group()
        self.pos = pos

    def __eq__(self, other):
        if type(other) == int:      # match against type
            return self.type == other
        if type(other) == str:      # match against content
            return self.matched == other
        else:
            raise NotImplementedError("SigmaConditionToken can only be compared against token type constants")

    def __str__(self):
        return "[ Token: %s: '%s' ]" % (self.tokenstr[self.type], self.matched)

class SigmaConditionTokenizer:
    """Tokenize condition string into token sequence"""
    tokendefs = [      # list of tokens, preferred recognition in given order, (token identifier, matching regular expression). Ignored if token id == None
            (SigmaConditionToken.TOKEN_ONE,    re.compile("1 of", re.IGNORECASE)),
            (SigmaConditionToken.TOKEN_ALL,    re.compile("all of", re.IGNORECASE)),
            (None,       re.compile("[\\s\\r\\n]+")),
            (SigmaConditionToken.TOKEN_AGG,    re.compile("count|min|max|avg|sum", re.IGNORECASE)),
            (SigmaConditionToken.TOKEN_NEAR,   re.compile("near", re.IGNORECASE)),
            (SigmaConditionToken.TOKEN_BY,     re.compile("by", re.IGNORECASE)),
            (SigmaConditionToken.TOKEN_EQ,     re.compile("==")),
            (SigmaConditionToken.TOKEN_LT,     re.compile("<")),
            (SigmaConditionToken.TOKEN_LTE,    re.compile("<=")),
            (SigmaConditionToken.TOKEN_GT,     re.compile(">")),
            (SigmaConditionToken.TOKEN_GTE,    re.compile(">=")),
            (SigmaConditionToken.TOKEN_PIPE,   re.compile("\\|")),
            (SigmaConditionToken.TOKEN_AND,    re.compile("and", re.IGNORECASE)),
            (SigmaConditionToken.TOKEN_OR,     re.compile("or", re.IGNORECASE)),
            (SigmaConditionToken.TOKEN_NOT,    re.compile("not", re.IGNORECASE)),
            (SigmaConditionToken.TOKEN_ID,     re.compile("[\\w*]+")),
            (SigmaConditionToken.TOKEN_LPAR,   re.compile("\\(")),
            (SigmaConditionToken.TOKEN_RPAR,   re.compile("\\)")),
            ]

    def __init__(self, condition):
        if type(condition) == str:          # String that is parsed
            self.tokens = list()
            pos = 1

            while len(condition) > 0:
                for tokendef in self.tokendefs:     # iterate over defined tokens and try to recognize the next one
                    match = tokendef[1].match(condition)
                    if match:
                        if tokendef[0] != None:
                            self.tokens.append(SigmaConditionToken(tokendef, match, pos + match.start()))
                        pos += match.end()      # increase position and cut matched prefix from condition
                        condition = condition[match.end():]
                        break
                else:   # no valid token identified
                    raise SigmaParseError("Unexpected token in condition at position %s" % condition)
        elif type(condition) == list:       # List of tokens to be converted into SigmaConditionTokenizer class
            self.tokens = condition
        else:
            raise TypeError("SigmaConditionTokenizer constructor expects string or list, got %s" % (type(condition)))

    def __str__(self):
        return " ".join([str(token) for token in self.tokens])

    def __iter__(self):
        return iter(self.tokens)

    def __len__(self):
        return len(self.tokens)

    def __getitem__(self, i):
        print(i)
        if type(i) == int:
            return self.tokens[i]
        elif type(i) == slice:
            return SigmaConditionTokenizer(self.tokens[i])
        else:
            raise IndexError("Expected index or slice")

    def __add__(self, other):
        if isinstance(other, SigmaConditionTokenizer):
            return SigmaConditionTokenizer(self.tokens + other.tokens)
        elif isinstance(other, (SigmaConditionToken, ParseTreeNode)):
            return SigmaConditionTokenizer(self.tokens + [ other ])
        else:
            raise TypeError("+ operator expects SigmaConditionTokenizer or token type, got %s: %s" % (type(other), str(other)))

    def index(self, item):
        #print(item)
        return self.tokens.index(item)
        
    def range(self,n,m):
        self.n=n
        self.m=m
        return self.tokens.range(0,len(tokens))
        
### Parse Tree Node Classes ###
class ParseTreeNode:
    """Parse Tree Node Base Class"""
    def __init__(self):
        raise NotImplementedError("ConditionBase is no usable class")

    def __str__(self):
        return "[ %s: %s ]" % (self.__doc__, str([str(item) for item in self.items]))

class ConditionBase(ParseTreeNode):
    """Base class for conditional operations"""
    op = COND_NONE
    items = None

    def __init__(self):
        raise NotImplementedError("ConditionBase is no usable class")

    def add(self, item):
        self.items.append(item)

    def __iter__(self):
        return iter(self.items)

    def __len__(self):
        return len(self.items)

class ConditionAND(ConditionBase):
    """AND Condition"""
    op = COND_AND

    def __init__(self, sigma=None, op=None, val1=None, val2=None):
        if sigma == None and op == None and val1 == None and val2 == None:    # no parameters given - initialize empty
            self.items = list()
        else:       # called by parser, use given values
            self.items = [ val1, val2 ]

class ConditionOR(ConditionAND):
    """OR Condition"""
    op = COND_OR

class ConditionNOT(ConditionBase):
    """NOT Condition"""
    op = COND_NOT

    def __init__(self, sigma=None, op=None, val=None):
        if sigma == None and op == None and val == None:    # no parameters given - initialize empty
            self.items = list()
        else:       # called by parser, use given values
            self.items = [ val ]

    def add(self, item):
        if len(self.items) == 0:
            super.add(item)
        else:
            raise ValueError("Only one element allowed")

    @property
    def item(self):
        try:
            return self.items[0]
        except IndexError:
            return None

class ConditionNULLValue(ConditionNOT):
    """Condition: Field value is empty or doesn't exists"""
    pass

class ConditionNotNULLValue(ConditionNULLValue):
    """Condition: Field value is not empty"""
    pass

class NodeSubexpression(ParseTreeNode):
    """Subexpression"""
    def __init__(self, subexpr):
        self.items = subexpr

# Parse tree generators: generate parse tree nodes from extended conditions
def generateXOf(sigma, val, condclass):
    """
    Generic implementation of (1|all) of x expressions.
        
    * condclass across all list items if x is name of definition
    * condclass across all definitions if x is keyword 'them'
    * condclass across all matching definition if x is wildcard expression, e.g. 'selection*'
    """
    if val.matched == "them":           # OR across all definitions
        cond = condclass()
        for definition in sigma.definitions.values():
            cond.add(NodeSubexpression(sigma.parse_definition(definition)))
        return NodeSubexpression(cond)
    elif val.matched.find("*") > 0:     # OR across all matching definitions
        cond = condclass()
        reDefPat = re.compile("^" + val.matched.replace("*", ".*") + "$")
        for name, definition in sigma.definitions.items():
            if reDefPat.match(name):
                cond.add(NodeSubexpression(sigma.parse_definition(definition)))
        return NodeSubexpression(cond)
    else:                               # OR across all items of definition
        return NodeSubexpression(sigma.parse_definition_byname(val.matched, condclass))

def generateAllOf(sigma, op, val):
    """Convert 'all of x' expressions into ConditionAND"""
    return generateXOf(sigma, val, ConditionAND)

def generateOneOf(sigma, op, val):
    """Convert '1 of x' expressions into ConditionOR"""
    return generateXOf(sigma, val, ConditionOR)

def convertId(sigma, op):
    """Convert search identifiers (lists or maps) into condition nodes according to spec defaults"""
    return NodeSubexpression(sigma.parse_definition_byname(op.matched))

# Condition parser
class SigmaConditionParser:
    """Parser for Sigma condition expression"""
    searchOperators = [     # description of operators: (token id, number of operands, parse tree node class) - order == precedence
            (SigmaConditionToken.TOKEN_ALL, 1, generateAllOf),
            (SigmaConditionToken.TOKEN_ONE, 1, generateOneOf),
            (SigmaConditionToken.TOKEN_ID,  0, convertId),
            (SigmaConditionToken.TOKEN_NOT, 1, ConditionNOT),
            (SigmaConditionToken.TOKEN_AND, 2, ConditionAND),
            (SigmaConditionToken.TOKEN_OR,  2, ConditionOR),
            ]

    def __init__(self, sigmaParser, tokens):
        self.sigmaParser = sigmaParser

        if SigmaConditionToken.TOKEN_PIPE in tokens:    # Condition contains atr least one aggregation expression
            pipepos = tokens.index(SigmaConditionToken.TOKEN_PIPE)
            self.parsedSearch = self.parseSearch(tokens[:pipepos])
            self.parsedAgg = SigmaAggregationParser(tokens[pipepos + 1:], self.sigmaParser)
        else:
            self.parsedSearch = self.parseSearch(tokens)
            self.parsedAgg = None

    def parseSearch(self, tokens):
        print(tokens)
        global rPos,lPos
        """
        Iterative parsing of search expression.
        """
        # 1. Identify subexpressions with parentheses around them and parse them like a separate search expression
        while SigmaConditionToken.TOKEN_LPAR in tokens:
             lPos = tokens.index(SigmaConditionToken.TOKEN_LPAR)
             #print(lPos)
             lTok = tokens[lPos]              
             if SigmaConditionToken.TOKEN_RPAR in tokens:                
                try:
                    rPos = tokens.index(SigmaConditionToken.TOKEN_RPAR)
                    #print(rPos)
                    rTok = tokens[rPos]                                      
                except ValueError as e:
                   raise SigmaParseError("Missing matching closing parentheses") from e
             if lPos + 1 == rPos:
                   raise SigmaParseError("Empty subexpression at " + str(lTok.pos))
             if lPos > rPos:
                   raise SigmaParseError("Closing parentheses at position " + str(rTok.pos) + " precedes opening at position " + str(lTok.pos))
             subparsed = self.parseSearch(tokens[lPos + 1:rPos])
             tokens = tokens[:lPos] + NodeSubexpression(subparsed) + tokens[rPos + 1:]   # replace parentheses + expression with group node that contains parsed subexpression
        
        # 2. Iterate over all known operators in given precedence
        for operator in self.searchOperators:
            # 3. reduce all occurrences into corresponding parse tree nodes
            while operator[0] in tokens:
                #print(operator[0])
                pos_op = tokens.index(operator[0])
                #print(pos_op)
                tok_op = tokens[pos_op]
                #print(tok_op)
                if operator[1] == 0:    # operator
                    treenode = operator[2](self.sigmaParser, tok_op)
                    #print(treenode)
                    tokens = tokens[:pos_op] + treenode + tokens[pos_op + 1:]
                elif operator[1] == 1:    # operator value
                    pos_val = pos_op + 1
                    tok_val = tokens[pos_val]
                    treenode = operator[2](self.sigmaParser, tok_op, tok_val)
                    tokens = tokens[:pos_op] + treenode + tokens[pos_val + 1:]
                elif operator[1] == 2:    # value1 operator value2
                    pos_val1 = pos_op - 1
                    pos_val2 = pos_op + 1
                    tok_val1 = tokens[pos_val1]
                    tok_val2 = tokens[pos_val2]
                    treenode = operator[2](self.sigmaParser, tok_op, tok_val1, tok_val2)
                    tokens = tokens[:pos_val1] + treenode + tokens[pos_val2 + 1:]
                    print(tokens)
                    

        if len(tokens) != 1:     # parse tree must begin with exactly one node
            raise ValueError("Parse tree must have exactly one start node!")
        querycond = tokens[0]

        # logsource = self.sigmaParser.get_logsource()
        #if logsource != None:
            # 4. Integrate conditions from configuration
            # RKG - Not handling conditions
            #if logsource.conditions != None:
            #    cond = ConditionAND()
            #    cond.add(logsource.conditions)
            #    cond.add(querycond)
            #    querycond = cond

            # 5. Integrate index conditions if applicable for backend
            #indexcond = logsource.get_indexcond()
            #if indexcond != None:
            #    cond = ConditionAND()
            #    cond.add(indexcond)
            #    cond.add(querycond)
            #    querycond = cond

        return querycond

    def __str__(self):
        return str(self.parsedSearch)

    def __len__(self):
        return len(self.parsedSearch)
 
# Aggregation parser
class SigmaAggregationParser(BaseParser):
    """Parse Sigma aggregation expression and provide parsed data"""
    parsingrules = [
            {   # State 0
                SigmaConditionToken.TOKEN_AGG:  ("aggfunc", "trans_aggfunc", 1),
                SigmaConditionToken.TOKEN_NEAR: ("aggfunc", "init_near_parsing", 8),
            },
            {   # State 1
                SigmaConditionToken.TOKEN_LPAR: (None, None, 2)
            },
            {   # State 2
                SigmaConditionToken.TOKEN_RPAR: (None, None, 4),
                SigmaConditionToken.TOKEN_ID: ("aggfield", "trans_fieldname", 3),
            },
            {   # State 3
                SigmaConditionToken.TOKEN_RPAR: (None, None, 4)
            },
            {   # State 4
                SigmaConditionToken.TOKEN_BY: ("cond_op", None, 5),
                SigmaConditionToken.TOKEN_EQ: ("cond_op", None, 7),
                SigmaConditionToken.TOKEN_LT: ("cond_op", None, 7),
                SigmaConditionToken.TOKEN_LTE: ("cond_op", None, 7),
                SigmaConditionToken.TOKEN_GT: ("cond_op", None, 7),
                SigmaConditionToken.TOKEN_GTE: ("cond_op", None, 7),
            },
            {   # State 5
                SigmaConditionToken.TOKEN_ID: ("groupfield", "trans_fieldname", 6)
            },
            {   # State 6
                SigmaConditionToken.TOKEN_EQ: ("cond_op", None, 7),
                SigmaConditionToken.TOKEN_LT: ("cond_op", None, 7),
                SigmaConditionToken.TOKEN_LTE: ("cond_op", None, 7),
                SigmaConditionToken.TOKEN_GT: ("cond_op", None, 7),
                SigmaConditionToken.TOKEN_GTE: ("cond_op", None, 7),
            },
            {   # State 7
                SigmaConditionToken.TOKEN_ID: ("condition", None, -1)
            },
            {   # State 8
                SigmaConditionToken.TOKEN_ID: (None, "store_search_id", 9)
            },
            {   # State 9
                SigmaConditionToken.TOKEN_AND: (None, "set_include", 10),
            },
            {   # State 10
                SigmaConditionToken.TOKEN_NOT: (None, "set_exclude", 8),
                SigmaConditionToken.TOKEN_ID: (None, "store_search_id", 9),
            },
            ]
    finalstates = { -1, 9 }

    # Aggregation functions
    AGGFUNC_COUNT = 1
    AGGFUNC_MIN   = 2
    AGGFUNC_MAX   = 3
    AGGFUNC_AVG   = 4
    AGGFUNC_SUM   = 5
    AGGFUNC_NEAR  = 6
    aggfuncmap = {
            "count": AGGFUNC_COUNT,
            "min":   AGGFUNC_MIN,
            "max":   AGGFUNC_MAX,
            "avg":   AGGFUNC_AVG,
            "sum":   AGGFUNC_SUM,
            "near":  AGGFUNC_NEAR,
            }

    def __init__(self, tokens, parser):
        self.parser = parser
        self.aggfield = None
        self.groupfield = None
        super().__init__(tokens)

    def trans_aggfunc(self, name):
        """Translate aggregation function name into constant"""
        try:
            return self.aggfuncmap[name]
        except KeyError:
            raise SigmaParseError("Unknown aggregation function '%s'" % (name))

    def trans_fieldname(self, fieldname):
        #raise AggregationsNotImplemented("Field mappings in aggregations must be single valued")
        return fieldname

    def init_near_parsing(self, name):
        """Initialize data structures for 'near" aggregation operator parsing"""
        self.include = list()
        self.exclude = list()
        self.current = self.include
        return self.trans_aggfunc(name)

    def store_search_id(self, name):
        self.current.append(name)
        return name

    def set_include(self, name):
        self.current = self.include

    def set_exclude(self, name):
        self.current = self.exclude
