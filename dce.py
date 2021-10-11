import json
import sys


def remove_reassigned_variables(instructions):
    var_map = {}
    unused = set()
    remove = set()
    for i, instruction in enumerate(instructions):
        if "args" in instruction:
            for var in instruction["args"]:
                if var in var_map:
                    i = var_map[var]
                    unused.discard(i)
        if "dest" in instruction:
            var = instruction["dest"]
            if var in var_map:
                i = var_map[var] 
                if i in unused:
                    remove.add(i)
            var_map[var] = i
            unused.add(i)
    modified_instructions = []
    for i, instruction in enumerate(instructions):
        if i not in remove:
            modified_instructions.append(instruction)
    return modified_instructions

                 
def remove_dead_code(instructions):
    has_changed = True
    while has_changed:
        has_changed = False
        used = set()
        for instruction in instructions:
            if "args" in instruction:
                used |= set(instruction["args"])
        remove = set()
        for i, instruction in enumerate(instructions):
            if "dest" in instruction and instruction["dest"] not in used:
                remove.add(i)
                has_changed |= True
        if has_changed:
            modified_instructions = []
            for i, instruction in enumerate(instructions):
                if i not in remove:
                    modified_instructions.append(instruction)
        instructions = modified_instructions
    return instructions


def simple_dead_code_elimination(instructions):
    instructions = remove_dead_code(instructions)
    instructions = remove_reassigned_variables(instructions)
    return instructions


if __name__ == "__main__":
    prog = json.load(sys.stdin)
    functions = prog["functions"]
    for function in functions:
        instructions = function["instrs"]
        function["instrs"] = simple_dead_code_elimination(instructions)
    print(repr(prog).replace('\'', '"'))
