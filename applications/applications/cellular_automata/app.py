from fasthtml.common import *
from starlette.responses import Response

app, rt = fast_app()

explanation = Div(
    P("This is an implementation of a 1D cellular automaton. The user can input a rule number, the number of generations to run, and the width of the grid."),
    Ul(
        Li("The rule number is used to determine the next state of a cell based on the current state of the cell and its neighbors."),
        Li("The automaton runs for the specified number of generations using the rule number to determine the next state of each cell."),
        Li("The automaton is initialized with a single black cell in the center and white cells on either side based on the width value."),
    ))

generator = None
bindict = {
    (1,1,1):0,
    (1,1,0):1,
    (1,0,1):2,
    (1,0,0):3,
    (0,1,1):4,
    (0,1,0):5,
    (0,0,1):6,
    (0,0,0):7}
initial_row = [0]*50 + [1] + [0]*50
color_map = {0:"white", 1:"black"}

def mk_box(color,size=5):
    return Div(cls="box", style=f"background-color:{color_map[color]};height:{size}px;width:{size}px;margin:0;display:inline-block;")

def mk_row(colors,font_size=0,size=5):
    return Div(*[mk_box(color,size) for color in colors], cls="row",style=f"font-size:{font_size}px;")

@app.get('/')
def homepage():
    return Div(
        Div(P(explanation,id="explanations")),
        Form(Group(
            Div(
                Label("Rule Number", cls="form-label"),
                Input(name="rule_number", id='rule_set', value="30", style="width: 340px;")
            ),
            Div(
                Label("Number of Generations", cls="form-label"),
                Input(name="generations", id='generations_set',  value="100",style="width: 340px;")
            ),
            Div(
                Label("Width", cls="form-label"),
                Input(name="width", id='width_set',  value="100", style="width: 340px;")
            ),    
            Button("Run",cls="btn btn-active btn-primary", type="submit", hx_get="/run", 
                   hx_target="#grid", hx_include="[name='rule_number'],[name='generations'],[name='width']", hx_swap="outerHTML")
            )),
        Button("Show Rule",cls="btn btn-active btn-primary", type="submit", hx_get="/show_rule",hx_target="#rule", hx_include="[name='rule_number']"),
        
        Group(Div(id="grid"), Div(id="rule")))

@rt('/show_rule')
def get(rule_number: int):
    rule = [int(x) for x in f'{rule_number:08b}']
    res = []
    for k in [(1,1,1),(1,1,0),(1,0,1),(1,0,0),(0,1,1),(0,1,0),(0,0,1),(0,0,0)]:
        v = rule[bindict[k]]
        res.append(
            Group(
                Div(mk_row(list(k),font_size=10,size=20),style="max-width:100px"), 
                Div(P(" -> "),style="max-width:100px"), 
                Div(mk_box(v,size=20),style="max-width:100px")))
    return Div(*res)


def run(rule=30, start = initial_row, generations = 100):
    rule = [int(x) for x in f'{rule:08b}']
    yield start
    old_row = [0] + start + [0]
    new_row = []
    for _ in range(generations):
        for i in range(1,len(old_row)-1):
            key=tuple(old_row[i-1:i+2])
            new_row.append(rule[bindict[key]])
        yield new_row
        old_row = [0] + new_row + [0]
        new_row = []


@rt('/run')
def get(rule_number: int, generations: int, width: int):
    start = [0]*(width//2) + [1] + [0]*(width//2)
    global generator 
    generator = run(rule=rule_number,generations=generations,start=start)
    return Div(
        Div(mk_row(next(generator)),
        Div(id="next",hx_trigger="every .1s", hx_get="/next", hx_target="#grid",hx_swap="beforeend")),id="grid")

@rt('/next')
def get():
    val = next(generator,False)
    if val:
        return mk_row(val)
    else: 
        return Response(status_code=286)