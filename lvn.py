import json
import sys


def local_ssa(basic_block):
    
    def is_inverse(var):
        return dest_to_var[var_to_dest[var]] == var

    # should probably implement or use a bidict
    var_to_dest = {}    # var => dest
    dest_to_var = {}    # dest => var
    # create a new basic block with new variable names while maintaining the semantics of the basic block
    # the new variable names are of the form lvn.x where x is a non-negative integer.
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
    # change back some of the new variable names back to the old variable names if they are never reassigned
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
    env = {}                # new variable => value number
    table = {}              # value IR => value number
    number_to_variable = [] # index/value number => new variable
    modified_block = []
    for instruction in basic_block:
        # make value ir for hashing purposes
        value_ir = [ instruction["op"] ]
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
            # set the instruction to reference a prior variable with the same value
            instruction["op"] = "id"
            instruction["args"] = [variable]
            if "value" in instruction:
                del instruction["value"]

        # hash isn't in the table
        elif value_ir not in table:
            # create new value number associated with this hash
            value_number = len(number_to_variable)
            # get an unique variable name to associate with the hash
            variable = instruction["dest"] if "dest" in instruction else f"lvn.{value_number}"
            # link the value number and variable names
            number_to_variable.append(variable) 
            # for every argument, check the environment to see which value number the argument references
            # change the argument to the variable name associated with that value number
            if "args" in instruction:
                modified_args = []
                for arg in args:
                    value = number_to_variable[env[arg]] if arg in env else arg
                    modified_args.append(value)
                instruction["args"] = modified_args
            # link the hash with the value number
            table[value_ir] = (value_number)
        # point the variable in the environment to the correct value number
        env[variable] = (value_number)
        modified_block.append(instruction)
    return basic_block


if __name__ == "__main__":
    prog = json.load(sys.stdin)
    functions = prog["functions"]
    for function in functions:
        instructions = function["instrs"]
        function["instrs"] = lvn(local_ssa(instructions)))
    print(json.dumps(prog, indent=4, sort_keys=True))
