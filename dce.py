import json
import sys
import cfg

def remove_reassigned_variables(basic_block):
    var_map = {}
    unused = set()
    remove = set()
    for i, instruction in enumerate(basic_block):
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
    modified_basic_block = []
    for i, instruction in enumerate(basic_block):
        if i not in remove:
            modified_basic_block.append(instruction)
    return modified_basic_block

                 
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


def sdce(instructions):
    instructions = remove_dead_code(instructions)
    labeled_blocks = cfg.make_labeled_blocks(instructions)
    basic_blocks = []
    for (label, block) in labeled_blocks:
        basic_blocks.append([{"label": label}])
        basic_blocks.append(block)
    modified_instructions = []
    for block in basic_blocks:
        modified_block = remove_reassigned_variables(block)
        modified_instructions.extend(modified_block)
    return modified_instructions


if __name__ == "__main__":
    prog = json.load(sys.stdin)
    functions = prog["functions"]
    for function in functions:
        instructions = function["instrs"]
        function["instrs"] = sdce(instructions)
    print(json.dumps(prog, indent=4, sort_keys=True))
