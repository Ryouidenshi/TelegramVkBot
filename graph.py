import networkx as nx
import numpy
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Agg')


class Graph:
    def __init__(self, groupsCount, groupsIntersection, requestNumberGroup):
        self.groupsCount = groupsCount
        self.groupsIntersection = groupsIntersection
        self.requestNumberGroup = requestNumberGroup

    # Метод создания графа

    def makeGraph(self):
        graph = nx.Graph()

        groups_node = list(self.groupsCount.items())
        groups_edge = self.groupsIntersection

        for node_group in range(len(groups_node)):
            graph.add_node(groups_node[node_group][0], size=groups_node[node_group][1])
        for edge_group in range(len(groups_edge)):
            graph.add_edge(groups_edge[edge_group][0], groups_edge[edge_group][1], weight=groups_edge[edge_group][2])
        return graph

    def makePlotGraph(self):
        graph = self.makeGraph()
        self.getGraph(graph)

    # Метод визуализации графа
    def getGraph(self, graph):
        node_size_max = []
        node_size = []

        # Настройка размеров вершин графа. Ориентируемся на максимально большую группу.
        # Максимально большую группу приводим к размеру 10000
        for i in graph.nodes():
            node_size_max.append(graph.nodes[i]["size"])
        coefficient_node = max(node_size_max) / 10000
        for i in graph.nodes():
            node_size.append(graph.nodes[i]["size"] / coefficient_node)

        # Задать размер картинки в дюймах
        plt.figure(figsize=(10, 6))

        # Надписи могут выходить за пределы полей, автоматически они не исправляются, поэтому расширяем
        pos = nx.circular_layout(graph)
        x_values, y_values = zip(*pos.values())

        # Расширяем по ширине
        x_max = max(x_values)
        x_min = min(x_values)
        x_margin = (x_max - x_min) * 0.2
        plt.xlim(x_min - x_margin, x_max + x_margin)

        # Расширяем по высоте
        y_max = max(y_values)
        y_min = min(y_values)
        y_margin = (y_max - y_min) * 0.2
        plt.ylim(y_min - y_margin, y_max + y_margin)

        # Рисуем ноды
        node_color = ['g']
        for i in range(len(node_size) - 1):
            node_color.append('y')
        nx.draw_networkx_nodes(graph, pos, node_size=node_size, node_color=node_color, alpha=0.6)

        # Если грань всего 1 или их нет вовсе, то и смысла нормализовывать их толщину нет
        if len(graph.edges()) > 1:
            # Средняя ширина всех ребёр графа
            edge_mean = numpy.mean([graph.get_edge_data(i[0], i[1])["weight"] for i in graph.edges()])
            # Стандартное отклонение ширины рёбер графа
            edge_std_dev = numpy.std([graph.get_edge_data(i[0], i[1])["weight"] for i in graph.edges()])
            # Если вдруг ширина у всех рёбер одинаковая (отчего стандартное отклонение становится нулём), то это
            # приведёт к делению на ноль (оно не упадёт, но будет в консоли слать warning-и), поэтому делаем проверку
            # прежде чем совершать нормализацию
            if edge_std_dev != 0:
                edge_width = [((graph.get_edge_data(i[0], i[1])["weight"] - edge_mean) / edge_std_dev)
                              for i in graph.edges()]
                nx.draw_networkx_edges(graph, pos, width=edge_width, edge_color='b')
            else:
                nx.draw_networkx_edges(graph, pos, edge_color='b')
        elif len(graph.edges()) == 1:
            nx.draw_networkx_edges(graph, pos, edge_color='b')
        # Рисуем надписи
        nx.draw_networkx_labels(graph, pos, font_size=10)
        # Убираем огромнейшее пустое пространство вокруг графа
        plt.tight_layout()

        plt.savefig('graphsUsers/' + str(self.requestNumberGroup) + '.png')
        plt.close()

    def __del__(self):
        print('DeletedGraphUser')
