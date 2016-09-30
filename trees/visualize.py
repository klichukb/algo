import plotly.offline as ply
import plotly.graph_objs as go

BLACK = 0
RED = 1


def get_heights(node, level=0):
    if node.left is not None:
        yield from get_heights(node.left, level + 1)

    yield level

    if node.right is not None:
        yield from get_heights(node.right, level + 1)


def get_all_nodes(node, widths, offset=0, level=0):
    if node.left is not None:
        yield from get_all_nodes(node.left, widths, offset - widths[level], level + 1)

    yield (node, (offset, level, node.color))

    if node.right is not None:
        yield from get_all_nodes(node.right, widths, offset + widths[level], level + 1)


def get_edges(node):
    if node.parent:
        yield (id(node.parent), id(node))
    else:
        yield None

    if node.left is not None:
        yield from get_edges(node.left)

    if node.right is not None:
        yield from get_edges(node.right)



def make_annotations(positions, labels, max_y, font_size=10, font_color='rgb(250,250,250)'):
    annotations = go.Annotations()
    for k in positions:
        annotations.append(
            go.Annotation(
                text=labels[k], # or replace labels with a different list for the text within the circle
                x=positions[k][0], y=2 * max_y - positions[k][1],
                xref='x1', yref='y1',
                font=dict(color=font_color, size=font_size),
                showarrow=False)
        )
    return annotations


def create_node_dots(xn, yn, node_color, labels):
    return go.Scatter(x=xn, y=yn,
                      mode='markers', name='',
                      marker=dict(symbol='dot',
                                  size=20,
                                  color='#444' if node_color == BLACK else '#c22',
                                  line=dict(color='rgb(50,50,50)', width=1)
                     ),
                    text=labels, hoverinfo='text', opacity=1
    )

def create_visuals(positions, edges, labels, title):
    Y = [positions[k][1] for k in positions]
    max_y = max(Y)
    xe = []
    ye = []

    for edge in edges:
        xe += [positions[edge[0]][0], positions[edge[1]][0], None]
        ye += [2 * max_y - positions[edge[0]][1], 2 * max_y - positions[edge[1]][1], None]

    lines = go.Scatter(x=xe, y=ye,
                       mode='lines', hoverinfo='none',
                       line=dict(color='rgb(110,110,110)', width=3),
    )
    axis = dict(showline=False, # hide axis line, grid, ticklabels and  title
                zeroline=False, showgrid=False, showticklabels=False)

    layout = dict(title=title,
                  annotations=make_annotations(positions, labels, max_y), font=dict(size=24),
                  showlegend=False,
                  xaxis=go.XAxis(axis),
                  yaxis=go.YAxis(axis),
                  margin=dict(l=40, r=40, b=85, t=100),
                  hovermode='closest',
                  plot_bgcolor='rgb(248,248,248)',
    )

    # create nodes
    # 0 - BLACK
    # 1 - RED
    black_xn = [positions[k][0] for k in positions if positions[k][2] == BLACK]
    black_yn = [2 * max_y - positions[k][1] for k in positions if positions[k][2] == BLACK]
    black_labels = ['Level {}'.format(positions[k][1])
                    for k in positions if positions[k][2] == BLACK]

    red_xn = [positions[k][0] for k in positions if positions[k][2] == RED]
    red_yn = [2 * max_y - positions[k][1] for k in positions if positions[k][2] == RED]
    red_labels = ['Level {}'.format(positions[k][1])
                  for k in positions if positions[k][2] == RED]

    black_dots = create_node_dots(black_xn, black_yn, BLACK, black_labels)
    red_dots = create_node_dots(red_xn, red_yn, RED, red_labels)

    data = go.Data([lines, black_dots, red_dots])
    fig = dict(data=data, layout=layout)
    fig['layout'].update(annotations=make_annotations(positions, labels, max_y))
    return fig


def get_width_steps(height):
    k = 1.5
    k2 = 3
    init = [k2, k, 1]
    if height < k2:
        return init[2 - height:]
    return [k2 << i for i in range(height - 1, 0, -1)] + init

def generate_draw_data(tree, title):
    height = max(get_heights(tree.root))
    widths = get_width_steps(height)
    nodes = list(get_all_nodes(tree.root, widths))
    positions = dict(
        (id(node), data) for (node, data) in nodes
    )
    labels = {id(node): node.value for (node, data) in nodes}
    edges = list(get_edges(tree.root))[1:]
    data = create_visuals(positions, edges, labels, title)
    return data

def plot_tree(tree, name=''):
    data = generate_draw_data(tree, name)
    ply.plot(data, filename=name + '.html', auto_open=True)
