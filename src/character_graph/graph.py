"""Отрисовка графа персонажей в PNG."""

import io

import networkx as nx
from matplotlib.figure import Figure

from character_graph.analyzer import Graph


def draw_graph(result: Graph) -> bytes:
    """Рисует граф: размер вершины — число упоминаний, толщина ребра — вес."""

    graph = nx.Graph()
    graph.add_nodes_from(result.mentions)
    for (source, target), weight in result.links.items():
        graph.add_edge(source, target, weight=weight)

    max_mentions = max(result.mentions.values(), default=1)
    max_weight = max(result.links.values(), default=1)
    sizes = [300 + 2700 * result.mentions[n] / max_mentions for n in graph]
    widths = [
        1 + 5 * graph.edges[edge]["weight"] / max_weight
        for edge in graph.edges
    ]

    figure = Figure(figsize=(8, 6), facecolor="#fffdf8")
    axes = figure.subplots()
    nx.draw_networkx(
        graph,
        pos=nx.spring_layout(graph, seed=42),
        ax=axes,
        node_size=sizes,
        width=widths,
        node_color="#a8c8e8",
        edge_color="#8a8a8a",
        font_size=11,
    )
    axes.axis("off")

    buffer = io.BytesIO()
    figure.savefig(buffer, format="png", bbox_inches="tight")
    return buffer.getvalue()
