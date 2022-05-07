from attr import attributes
import graphviz
import json
from graphviz import nohtml


def create_node(g, id, texts: list):
    texts.insert(0, "<")
    texts.append(">")
    g.node(id, "<BR />".join(texts))

def create_box_node(g, id, texts:list):
    rows = [f'{{ <f{count}> {text} }}' for count, text in enumerate(texts)]
    g.node(id, " | ".join(rows), {'shape': 'record'} )

def show_component_score(g, id, component):
    id += "-score"
    score = " Score | {"
    sc = []
    cat = ["Findable", "Accessible", "Interoperable", "Reusable"]
    
    for c in cat:   
        passes = component['score'][c]['earned']
        total = component['score'][c]['total']
        if total == 0:
            continue
        sc.append(f" {{ {c} |  {passes} / {total} | {round((passes/total)*100,2)}% }}")
    
    score += " | ".join(sc) + " }"
    create_box_node(g, id, [score])
    return id

def show_checks(g, id, component):
    id2 = id
    id += "-check"

    cat = ["Findable", "Accessible", "Interoperable", "Reusable"]
    for c in cat:  
        id_c = id + "-" + c 
        checks = []
        score = f" {c} | {{"
        
        for check in component["checks"]:
            if check["category_id"] == c:
                passed = check["total_passed_tests"]
                total = check["total_tests_run"]
                
                checks.append(f" {{ {check['principle_id']} |  {check['explanation']} | {round((passed/total)*100,2)}% }}")

        score += " | ".join(checks) + " }"
        create_box_node(g, id_c, [score])
        g.edge(id2, id_c)
    return id_c

def create_component_node(g, component, i):
    id = str(i) + str(component["name"]) 
    name = " Name | " + str(component["name"])
    identifier = " Identifier | " + str(component["identifier"])
    type = " Type | " + component["type"]
   
    score = " Score | <here>  XXX% "
    print(score)
    create_box_node(g, id, [name, identifier, type, score])
    return id

def generate_visual_graph(output):

    with open(output) as f:
        output = json.load(f)

    g = graphviz.Digraph('G', filename='visual-RO-FAIRnes')
    g.graph_attr['rankdir'] = 'LR' 

    # add root element
    percentaje = str(round (output["overall_score"]["score"] * 100, 2)) + "%"
    create_node(g, "ROOT", ["Final aggregation", percentaje])

    # create subcomponents nodes
    for i, component in enumerate(output["components"]):
        component_id = create_component_node(g, component, i)
        g.edge("ROOT", component_id)
        score_id = show_component_score(g, component_id, component)
        g.edge(component_id+":here", score_id)
        # its a mess 
        # check_id = show_checks(g, score_id, component)
        
    g.view()

generate_visual_graph("ro-full-fairness.json")