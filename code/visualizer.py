import graphviz
import json

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
        passes = component['score'][c]['tests_passed']
        total = component['score'][c]['total_tests']
        if total == 0:
            continue
        sc.append(f" {{ {c} |  {passes} / {total} | {round((passes/total)*100,2)}% }}")
    
    score += " | ".join(sc) + " }"
    create_box_node(g, id, [score])
    return id

def show_checks(g, id, component):
    parent_id = id
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
        g.edge(parent_id, id_c)
    return id_c

def create_component_node(g, component, i):
    
    # remove forbidden characters
    fields = ["name", "identifier", "type", "tool-used"]
    for field in fields:
        if component[field]:
            component[field] = component[field].replace(":","").replace("|","")
            
    id = str(i) + str(component["name"]) 
    name = " Name | " + str(component["name"])
    identifier = " Identifier | " + str(component["identifier"])
    component_type = " Type | " + component["type"]   if type(component["type"]) == str else ", ".join(component["type"])
    tool_used = " Tool used | " + component["tool-used"]
    # calculate overall score of a component. average of their parts
    scores = []
    for cat in component["score"]:
        cat = component["score"][cat]
        if int(cat["total_tests"]) == 0:
            continue
        scores.append(round((cat["tests_passed"] / cat["total_tests"]) * 100 , 2))
    
    score = f" Score | {round(sum(scores)/len(scores),2)}% | <here>  Average of the parts "

    create_box_node(g, id, [name, identifier, component_type, tool_used, score])
    return id

def generate_visual_graph(output_file):

    with open(output_file) as f:
        output = json.load(f)
    dot_filename = "visual-" + output_file.rsplit('.', 1)[0]
    g = graphviz.Digraph('G', filename=dot_filename)
    g.graph_attr['rankdir'] = 'LR' 

    # add root element
    percentaje = str(round (output["overall_score"]["score"], 2)) + "%"
    description = output["overall_score"]["description"]
    texts = ["Final aggregation", percentaje]
    create_node(g, "ROOT",  texts + description.split("."))

    # create subcomponents nodes
    for i, component in enumerate(output["components"]):
        component_id = create_component_node(g, component, i)
        g.edge("ROOT", component_id)
        score_id = show_component_score(g, component_id, component)
        g.edge(component_id+":here", score_id)
        # its a mess 
        # check_id = show_checks(g, score_id, component)
        
    # g.view() this open the pdf file
