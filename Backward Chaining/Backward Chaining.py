from copy import deepcopy
import sys

def read_file(input_file):
    query = input_file.readline()
    query = query[:len(query)-1]
    number = int(input_file.readline())
    clauses = []
    for i in range(0, number):
        clause = input_file.readline()
        clause = clause[:len(clause)-1]
        clauses.append(clause)

    return query, clauses


def find_query(query_list, claus_list, output_file, args_dict):
    old_argument = []
    new_argument = []
    for query in query_list:
        clauses_list = deepcopy(claus_list)
        bool_val = False
        predicate = convert_to_dict(query)
        if predicate["function"] != "and":
            query_print = "Ask: "
            print_output(output_file, query_print, query)
            flag_match = 0
            bool_val_prev = True
            for clause in clauses_list:
                bool_val = False
                if clause[len(clause)-1][:clause[len(clause)-1].find("(")] == predicate["function"]:
                    pred_clause = convert_to_dict(clause[len(clause)-1])
                    if len(clause) == 1:
                        predicate_args = predicate["args"]
                        pred_clause_args = pred_clause["args"]
                        for i in range(0, len(predicate_args)):
                            if predicate_args[i][0].isupper() and pred_clause_args[i][0].isupper():
                                flag_match = 1
                                if predicate_args[i] != pred_clause_args[i]:
                                    flag_match = 0
                                    bool_val = False
                                    break
                            elif predicate_args[i][0].islower() and pred_clause_args[i][0].isupper():
                                old_argument.append(predicate_args[i])
                                for bol in range(0,len(args_dict["args"])):
                                    if args_dict["args"][bol] == predicate_args[i]:
                                       args_dict[predicate_args[i]] = pred_clause_args[i]
                                predicate_args[i] = pred_clause_args[i]
                                new_argument.append(pred_clause_args[i])
                                flag_match = 1
                            else:
                                flag_match = 0
                        if flag_match == 1:
                            bool_val = True
                    else:
                        if clause[len(clause)-2] == "=>":
                            if not bool_val_prev:
                                query_print = "Ask: "
                                print_output(output_file, query_print , convert_to_string(predicate))
                            temp_arg = 0
                            for ijkl in range(0, len(predicate["args"])):
                                if predicate["args"][ijkl][0].islower():
                                    if pred_clause["args"][ijkl][0].isupper():
                                        temp_arg = predicate["args"][ijkl]
                                        temp_new_arg = pred_clause["args"][ijkl]
                                        predicate["args"][ijkl] = pred_clause["args"][ijkl]
                                    else:
                                        temp_arg = predicate["args"][ijkl]
                                        predicate["args"][ijkl] += "0"
                                        temp_new_arg = predicate["args"][ijkl]

                            for abc in range(0, len(query_list)):
                                pred_abc = convert_to_dict(query_list[abc])
                                if pred_abc["function"] != "and":
                                    for intk in range(0, len(pred_abc["args"])):
                                        if pred_abc["args"][intk] == temp_arg:
                                            pred_abc["args"][intk] = temp_new_arg
                                query_list[abc] = convert_to_string(pred_abc)

                            temp_query = clause[:len(clause)-2]
                            temp_query = swap_arguments(temp_query, pred_clause, predicate)
                            for abcd in range(0, len(predicate["args"])):
                                if pred_clause["args"][abcd][0].islower():
                                    pred_clause["args"][abcd] = predicate["args"][abcd]
                                    args_dict["args"].append(predicate["args"][abcd])
                            bool_val, old_argument, new_argument, args_dict = find_query(temp_query, clauses_list, output_file, args_dict)
                            if not bool_val :
                                bool_val_prev = False

                    if len(new_argument) != 0:
                        for items in range(0, len(new_argument)):
                            for item in range(0, len(predicate["args"])):
                                if predicate["args"][item] == old_argument[items]:
                                    predicate["args"][item] = new_argument[items]
                            clause[len(clause)-1] = convert_to_string(predicate)
                        for items in range(0, len(new_argument)):
                            for quet in range(0, len(query_list)):
                                predicator = convert_to_dict(query_list[quet])
                                if predicator["function"] != "and":
                                    for item in range(0, len(predicator["args"])):
                                        if predicator["args"][item] == old_argument[items]:
                                            predicator["args"][item] = new_argument[items]
                                query_list[quet] = convert_to_string(predicator)
                    if bool_val:
                        for mld in range(0,len(predicate["args"])):
                            if predicate["args"][mld][0].islower():
                                predicate["args"][mld] = args_dict[predicate["args"][mld]]
                        query_print = "True: "
                        print_output(output_file, query_print, convert_to_string(predicate))
                        break
            if not bool_val:
                query_print = "False: "
                print_output(output_file, query_print, convert_to_string(predicate))
                break
    return bool_val, old_argument, new_argument, args_dict


def swap_arguments(temp_query, pred_clause, predicate):
    for que in range(0, len(temp_query)):
        temp = convert_to_dict(temp_query[que])
        if temp["function"] != "and":
            for o in range(0, len(pred_clause["args"])):
                for m in range(0, len(temp["args"])):
                    if pred_clause["args"][o] == temp["args"][m]:
                        if temp["args"][m][0].islower():
                            temp["args"][m] = predicate["args"][o]
        temp_query[que] = convert_to_string(temp)
    return temp_query


def convert_arguments(predicate):
    for i in range(0, len(predicate["args"])):
        if predicate["args"][i][0].islower():
            predicate["args"][i] = "x" + str(i)
    return predicate


def backward_chaining(query, clauses, output_file):
    query_list = convert_to_list(query)
    clause_list = []
    args_dict = {
        "args": []
    }
    for clause in clauses:
        clause_list.append(convert_to_list(clause))
    bool_value, blah1, blah2, blah3 = find_query(query_list, clause_list, output_file, args_dict)
    if bool_value:
        print_output(output_file, "True", " ")
    else:
        print_output(output_file, "False", " ")


def convert_to_dict(predicate):
    pred = {}
    k = predicate.find("(")
    if k != -1:
        func = predicate[:k]
        l = predicate.index(")")
        args = predicate[k+1:l]
        list_arg = args.split(", ")

        pred["function"] = func
        pred["args"] = list_arg
    else:
        pred["function"] = "and"
    return pred


def convert_to_string(predicate):
    if predicate["function"] != "and":
        str_pred = predicate["function"] + "("
        str_pred += ", ".join(predicate["args"])
        str_pred += ")"
    else:
        str_pred = "&&"
    return str_pred


def convert_to_list(claused):
    clause_list = []
    i = claused.index(")")
    if i == len(claused)-1:
        clause_list.append(claused)
    else:
        temp_clause = claused[:i+1]
        clause_list.append(temp_clause)
        temp_2_clause = list(claused[i+2:])
        for i in range(0, len(temp_2_clause)):
            if temp_2_clause[i] == ',':
                temp_2_clause[i+1] = '+'
        temp_2_clause = "".join(temp_2_clause)
        temp_2_list = temp_2_clause.split(" ")
        for wal in range(0, len(temp_2_list)):
            while temp_2_list[wal].find("+") != -1:
                pos = temp_2_list[wal].find("+")
                m = list(temp_2_list[wal])
                m[pos] = " "
                m = "".join(m)
                temp_2_list[wal] = m
            clause_list.append(temp_2_list[wal])
    return clause_list


def print_output(filename, val, qval):
    if qval != " ":
        qpred = convert_to_dict(qval)
        predq =deepcopy(qpred)
        for i in range(0, len(predq["args"])):
            if predq["args"][i][0].islower():
                predq["args"][i] = "_"
        val_to_print = val + convert_to_string(predq)
        filename.write(val_to_print + "\n")
    else:
        filename.write(val + "\n")


def main():
    #input_file = open(sys.argv[2], "r")
    input_file = open("input.txt", "r")
    query, clauses = read_file(input_file)
    input_file.close()
    output_file = open("output.txt", "w")
    backward_chaining(query, clauses, output_file)
    output_file.close()


main()
