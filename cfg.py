import json
import sys


TERMINATORS = ["jmp", "br", "ret"]


def make_labeled_blocks(instructions):
    labeled_blocks = []
    block = []
    label = None
    for instruction in instructions:
        if "op" in instruction:
            op = instruction["op"]
            block.append(instruction)
        if op and op in TERMINATORS or "label" in instruction:
            if not label:
                label = "block" + str(len(labeled_blocks))
            if block:
                labeled_blocks.append((label, block))
                label = None
            if "label" in instruction:
                label = instruction["label"]
            block = []            
    if not label:
        label = "block" + str(len(labeled_blocks))
    if block:
        labeled_blocks.append((label, block))
    return labeled_blocks


def make_cfg(labeled_blocks):
    cfg = {}
    for i, (label, block) in enumerate(labeled_blocks):
        last_instr = block[-1]
        if last_instr["op"] in ["jmp", "br"]:
            destinations = last_instr["labels"]
        elif last_instr["op"] == "ret" or i == len(labeled_blocks)-1:
            destinations = []
        else:
            next_label, _ = labeled_blocks[i+1]
            destinations = [next_label]
        cfg[label] = destinations
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
        labeled_blocks = make_labeled_blocks(instructions)
        cfg = make_cfg(labeled_blocks)
        print_graphviz(cfg)
