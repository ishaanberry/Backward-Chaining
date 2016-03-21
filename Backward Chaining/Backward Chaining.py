import sys
from copy import deepcopy
index = 0
outputFile = open("output.txt","w+")
def parseInputFile(inputFile):
    queryList = []
    myFile = open(inputFile, "r")
    #Find the initial query that has to be solved and the number of clauses in KB
    query =  stringToExpression(myFile.readline().strip('\n'))
    numberOfClauses = myFile.readline().strip('\n')

    #Create a list of clauses
    n = 1
    KB = []
    while n <= int(numberOfClauses):
        sentence = myFile.readline().strip('\n')
        KB.append(stringToExpression(sentence))
        n = n + 1
    return (KB, query)


class Expression(object):
    def __init__(self, op, args=[], printed=False):
        self.op= op
        self.args = args
        self.printed = printed

    def __eq__(self, other):
        if self is other:
            return True
        elif isinstance(other, Expression):
            return (self.op == other.op and self.args == other.args)
        else:
            return False

    def __hash__(self):
        return hash(self.op) ^ hash(tuple(self.args))

    def getStringRepresentation(self, fuzz=False):
        if(self.isVariable()):
            return "_"
        elif(self.isConstant()):
            return self.op
        else:
            argStrings = []
            for arg in self.args:
                argString = arg.getStringRepresentation()
                argStrings.append(argString)

            if self.isAnd():
                return " && ".join(argStrings)
            elif self.isImplication():
                return " => ".join(argStrings)
            else:
                return str(self.op) + "(" + ", ".join(argStrings) + ")"

    def getOperator(self):
        return self.op

    def getArg(self):
        for i in range(len(self.args)):
            print i

    def isConstant(self):
        return (not self.args and self.op[0].isupper())

    def isVariable(self):
        return (not self.args and self.op[0].islower())


    def isPredicate(self):
        if self.args and self.op:
            return True
        else:
            return False

    def isAnd(self):
        return self.op == "&&"

    def isImplication(self):
        return self.op == "=>"

    def isPrint(self):
        return self.op == "print"


def standardizeApart(sentence, d):
    if(sentence.isVariable()):
        global index
        key = sentence.op
        if key not in d:
            index += 1
            d[sentence.op] = sentence.op + str(index)
        return Expression(d[sentence.op])
    elif(sentence.isConstant()):
        return Expression(sentence.op)
    else:
        standardizedArgs = []
        for arg in sentence.args:
            standardizedArg = standardizeApart(arg, d)
            standardizedArgs.append(standardizedArg)
        return Expression(sentence.op, standardizedArgs)

def stringToExpression(sentence):
    implicationOpArgs = sentence.split(" => ")
    andOperatorArgs = sentence.split(" && ")
    if (len(implicationOpArgs) > 1):
        lhsExp = stringToExpression(implicationOpArgs[0])
        rhsExp = stringToExpression(implicationOpArgs[1])

        return Expression("=>", [lhsExp, rhsExp])
    elif (len(andOperatorArgs) > 1):
        #Multiple predicates
        op = "&&"
        args = []
        for andOperatorArg in andOperatorArgs:
            arg = stringToExpression(andOperatorArg)
            args.append(arg)

        return Expression(op, args)
    else:
        #Single predicate, constant or variable
        temp = andOperatorArgs[0]
        tempParts = temp.split('(')
        op = tempParts[0]
        if len(tempParts) > 1:
            tempParts = tempParts[1].split(')')
            argsString = tempParts[0]
        else:
            argsString = None

        args = []
        if argsString:
            argStrings = argsString.split(', ')
            for argString in argStrings:
                arg = stringToExpression(argString)
                args.append(arg)

        return Expression(op, args)


def unify(p, q, theta):
    if theta is None:
        return None
    elif(p == q):
        return theta
    elif(p.isVariable()):
        return unifyVar(p, q, theta)
    elif(q.isVariable()):
        return unifyVar(q, p, theta)
    elif(p.isPredicate() and q.isPredicate):
        if p.op == q.op:
            if(len(p.args) != len(q.args)):
                return None
            for i in range(len(p.args)):
                theta = unify(p.args[i], q.args[i], theta)
            return theta
        elif p.isImplication():
            return unify(p.args[1], q, theta)
        elif q.isImplication():
            return unify(p, q.args[1], theta)
        else:
            return None
    else:
        return None


def unifyVar(var, x, theta):
    if var in theta:
        return unify(theta[var], x, theta)
    elif x in theta:
        return unify(var, theta[x], theta)
    elif occurCheck(var, x):
        return None
    else:
        theta[var] = x
        return theta


def occurCheck(p, q):
    if(p == q):
        return True
    elif isinstance(q, list):
        for item in q:
            if occurCheck(p, item):
                return True
        return False
    else:
        return occurCheck(p, q.args)

def substitute(theta, p):
    if p.isPredicate():
        substitutedArgs = []
        for arg in p.args:
            substitutedArgs.append(substitute(theta, arg))
        return Expression(p.op, substitutedArgs)
    elif p.isConstant():
        return p
    else:
        if p in theta:
            if theta[p].isVariable():
                return substitute(theta, theta[p])
            else:
                return theta[p]
        else:
            return p

def compose(thetaA, thetaB):
    thetaC = dict()
    thetaC.update(thetaA)
    thetaC.update(thetaB)
    return thetaC
def backwardChaining(KB, goals, theta):
    if not goals:
        return theta
    firstGoal = goals[0]
    if firstGoal.isPrint():
        firstGoal.args[0].printed = True
        outputFile.write("True: "+(substitute(theta, firstGoal.args[0])).getStringRepresentation()+'\n')
        return backwardChaining(KB, goals[1:], theta)
    elif firstGoal.isAnd():
        expandedGoals = []
        expandedGoals.extend(firstGoal.args)
        expandedGoals.extend(goals[1:])
        return backwardChaining(KB, expandedGoals, theta)
    qPrime = substitute(theta, firstGoal)
    outputFile.write("Ask: "+qPrime.getStringRepresentation()+'\n')
    firstSearch = True
    for clause in KB:
        r = standardizeApart(clause, {})
        thetaPrime = deepcopy(theta)
        thetaPrime = unify(r, qPrime, thetaPrime)

        if thetaPrime is not None:
            if not firstSearch:
                outputFile.write("Ask: "+qPrime.getStringRepresentation()+'\n')
            firstSearch = False
            if not r.isImplication():
                qPrime.printed = True
                outputFile.write("True: " +(substitute(thetaPrime, qPrime)).getStringRepresentation()+'\n')
            newGoals = []
            if r.isImplication():
                newGoals.append(r.args[0])
                newGoals.append(Expression("print", [qPrime]))
            newGoals.extend(goals[1:])
            thetaPrime = backwardChaining(KB, newGoals, compose(theta, thetaPrime))
            if thetaPrime is not None:
                return thetaPrime

    if not qPrime.printed:
        outputFile.write("False: "+qPrime.getStringRepresentation()+'\n')
    return None

def main():
    inputFile = "input.txt";
    (KB, query) = parseInputFile(inputFile)
    theta = {}

    if query.isAnd():
        for arg in query.args:
            theta = backwardChaining(KB, [arg], theta)
            breakOut = theta is None
            if breakOut:
                outputFile.write(str(False))
                break
        if not breakOut:
            outputFile.write(str(True))
    else:
        theta = backwardChaining(KB, [query], theta)
        if(theta is not None):
            value = True
        else:
            value = False
        outputFile.write(str(value))

    outputFile.close()

if __name__ == '__main__':
    main()


