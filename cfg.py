import json
import sys


TERMINATORS = ["jmp", "br", "ret"]


def make_basic_blocks(instructions):
    basic_blocks = []
    block = []
    label = None
    for instruction in instructions:
        if "op" in instruction:
            op = instruction["op"]
            block.append(instruction)
        if op and op in TERMINATORS or "label" in instruction:
            if not label:
                label = "block" + str(len(basic_blocks))
            if block:
                basic_blocks.append((label, block))
                label = None
            if "label" in instruction:
                label = instruction["label"]
            block = []            
    if not label:
        label = "block" + str(len(basic_blocks))
    if block:
        basic_blocks.append((label, block))
    return basic_blocks


def make_cfg(basic_blocks):
    cfg = {}
    for i, (source, block) in enumerate(basic_blocks):
        last_instr = block[-1]
        if last_instr["op"] in ["jmp", "br"]:
            destinations = last_instr["labels"]
        elif last_instr["op"] == "ret" or i == len(basic_blocks)-1:
            destinations = []
        else:
            next_label, _ = basic_blocks[i+1]
            destinations = [next_label]
        cfg[source] = destinations
    return cfg


def print_graphviz(cfg):
    nodes = set(cfg.keys())
    for destinations in cfg.values():
        nodes |= set(destinations)
    print("digraph {")
    for node in nodes:
        print(f"    {node};")
    for source, destinations in cfg.items():
        for destination in destinations:
            print(f"    {source}->{destination};")
    print("}")


if __name__ == "__main__":
    prog = json.load(sys.stdin)
    functions = prog["functions"]
    for function in functions:
        instructions = function["instrs"]
        basic_blocks = make_basic_blocks(instructions)
        cfg = make_cfg(basic_blocks)
        print_graphviz(cfg)
