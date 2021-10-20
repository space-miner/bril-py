import json
import sys


def local_ssa(basic_block):
    
    def is_inverse(var):
        return dest_to_var[var_to_dest[var]] == var

    # should probably implement a bidict
    var_to_dest = {}    # var => dest
    dest_to_var = {}    # dest => var
    modified_block = []
    for instruction in basic_block:
        if "args" in instruction:
            args = instruction["args"]
            instruction["args"] = [dest_to_var.get(arg, arg) for arg in args]
        if "dest" in instruction:
            dest = instruction["dest"]
            var = f"lvn.{len(var_to_dest)}"
            var_to_dest[var] = dest
            dest_to_var[dest] = var
            instruction["dest"] = var
        modified_block.append(instruction)
    for instruction in modified_block:
        if "dest" in instruction:
            var = instruction["dest"]
            if is_inverse(var):
                instruction["dest"] = var_to_dest[var]
        if "args" in instruction:
            args = instruction["args"]
            modified_args = [var_to_dest[arg] if is_inverse(arg) else arg for arg in args]
            instruction["args"] = modified_args
    return modified_block


def lvn(basic_block):
    env = {}                # new variable => value_number
    table = {}              # value IR => value_number
    number_to_variable = [] # index/value_number => new variable
    modified_block = []
    for instruction in basic_block:
        # make value ir for hashing purposes
        value_ir = [ instruction["op"] ]    # every bril instruction has an op
        if "args" in instruction:
            args = instruction["args"]
            for arg in args:
                value = env[arg] if arg in env else arg
                value_ir.append(value)
        if "value" in instruction:
            value_ir.append(instruction["value"])
        value_ir = tuple(value_ir)
        # check to see if the hash is in the table
        if value_ir in table:
            value_number = table[value_ir] 
            variable = number_to_variable[value_number]
            # set this instruction to dest := id var
            instruction["op"] = "id"
            instruction["args"] = [variable]
            # remove value if it was there
            if "value" in instruction:
                del instruction["value"]
        # hash not in table
        elif value_ir not in table:
            value_number = len(number_to_variable)
            variable = instruction["dest"] if "dest" in instruction else f"lvn.{value_number}"
            number_to_variable.append(variable) 
            if "args" in instruction:
                modified_args = []
                for arg in args:
                    value = number_to_variable[env[arg]] if arg in env else arg
                    modified_args.append(value)
                instruction["args"] = modified_args
            table[value_ir] = (value_number)
        env[variable] = (value_number)
        modified_block.append(instruction)
    return basic_block


if __name__ == "__main__":
    prog = json.load(sys.stdin)
    functions = prog["functions"]
    for function in functions:
        instructions = function["instrs"]
        function["instrs"] = lvn(local_ssa(instructions))
    print(json.dumps(prog, indent=4, sort_keys=True))
