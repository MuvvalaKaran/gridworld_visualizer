from itertools import product

import svgwrite


BOARD_SIZE = ("200", "200")
CSS_STYLES = """
    .background { fill: white; }
    .line { stroke: firebrick; stroke-width: .1mm; }
    .lava { fill: #ff8b8b; }
    .dry { fill: #f4a460; }
    .water { fill: #afafff; }
    .recharge {fill: #ffff00; }
    .normal {fill: white; }
    rect {
       stroke: black;
       stroke-width: 1;
    }

    .agent {
      r: 10%;
      fill: black;
      stroke-width: 2;
      stroke: grey;
      animation: blinker 4s linear infinite;
      animation: move 3s ease forwards;
    }
    @keyframes blinker {
       50% {
         opacity: 0.5;
       }
    }
"""

def create_arrow_marker(dwg):
    #   <defs>
    #     <marker id="arrow" markerWidth="10" markerHeight="10" refX="0" refY="3" orient="auto" markerUnits="strokeWidth">
    #       <path d="M0,0 L0,6 L9,3 z" fill="#f00" />
    #     </marker>
    #   </defs>
    arrow = dwg.marker(id='arrow', insert=(0, 3), size=(10, 10), orient='auto', markerUnits='strokeWidth')
    arrow.add(dwg.path(d='M0,0 L0,6 L9,3 z', fill='#f00'))
    dwg.defs.add(arrow)
    return arrow


def draw_board(n=3, tile2classes=None):
    dwg = svgwrite.Drawing(size=(f"{n+0.05}cm", f"{n+0.05}cm"))

    dwg.add(dwg.rect(size=('100%','100%'), class_='background'))

    def group(classname):
        return dwg.add(dwg.g(class_=classname))
    
    # draw squares
    for x, y in product(range(n), range(n)):
        kwargs = {
            'insert': (f"{x+0.1}cm", f"{y+0.1}cm"), 
            'size': (f"0.9cm", f"0.9cm"),
        }
        if tile2classes is not None and tile2classes(x, y):
            kwargs["class_"] = tile2classes(x, n - y - 1)

        dwg.add(dwg.rect(**kwargs))

        # Label this box #1
        # dwg.add(dwg.text(f'l{n**2 - (n*x + y)}',
        #     insert=(f"{x+ 0.55}cm",f"{y + 0.55}cm"),
        #     stroke='none',
        #     # fill=svgwrite.rgb(15, 15, 15, '%'),
        #     font_size='15px',
        #     # font_weight="bold"
        #     ))

    return dwg


N = (0, -1)
S = (0, 1)
W = (-1, 0)
E = (1, 0)


def gen_offsets(actions):
    dx, dy = 0, 0
    for ax, ay in actions:
        dx += ax
        dy += ay
        yield dx, dy


def move_keyframe(dx, dy, ratio):
    return f"""{ratio*100}% {{
    transform: translate({dx}cm, {dy}cm);
}}"""


def gridworld(n=10, actions=None, tile2classes=None, extra_css="", init_pos: tuple=(2, 3)):
    # Draw the Square board
    dwg = draw_board(n=n, tile2classes=tile2classes)

    css_styles = CSS_STYLES
    if actions is not None:
        # Add agent.
        x, y = init_pos  # start position.
        cx, cy = x + 0.55, (n - y - 1) + 0.55
        dwg.add(svgwrite.shapes.Circle(
            r="0.3cm",
            center=(f"{cx}cm", f"{cy}cm"), 
            class_="agent",
        ))

        offsets = gen_offsets(actions)
        # for x, y in offsets:
        #     dwg.add(dwg.path(d=f'M{x + 0.55},{(n - y - 1) + 0.55}, {x},{y}',
        #                     stroke="#000",
        #                     fill="none",
        #                     stroke_width=1))

        keyframes = [move_keyframe(x, y, (i+1)/len(actions)) for i, (x, y)
                     in enumerate(offsets)]
        move_css = "\n@keyframes move {\n" + '\n'.join(keyframes) + "\n}"
        css_styles += move_css
    
    dwg.defs.add(dwg.style(css_styles + extra_css))
    return dwg


if __name__== '__main__':
    def tile2classes(x, y):
        if (3 <= x <= 4) and (2 <= y <= 5):
            return "water"
        elif (x in (0, 7)) and (y in (0, 7)):
            return "recharge"
        elif (2 <= x <= 5) and y in (0, 7):
            return "dry"
        elif x in (1, 6) and (y in (4, 5) or y <= 1):
            return "lava"
        elif (x in (0, 7)) and (y in (1, 4, 5)):
            return "lava"

        return "normal"

    actions = [E, N, N, N, N, W, W, W]
    dwg = gridworld(n=8, tile2classes=tile2classes, actions=actions)
    dwg.saveas("./example.svg", pretty=True)
