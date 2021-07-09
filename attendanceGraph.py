#!/usr/bin/env python3
# vim: set ai et ts=4 sw=4:

import matplotlib as mpl
import matplotlib.pyplot as plt


class AttendanceGraph:
    def __init__(self, data):
        self.data = data

    def get_graph_unique_users(self):
        data_values = []
        data_names = []
        for item in self.data:
            data_names.append(item['date'])
            data_values.append(item['counts'])

        dpi = 80
        fig = plt.figure(dpi=dpi, figsize=(512 / dpi, 384 / dpi))
        mpl.rcParams.update({'font.size': 10})

        plt.title = 'Количество уникальных пользователей.'
        ax = plt.axes()
        ax.yaxis.grid(True, zorder=1)

        xs = range(len(data_names))

        plt.bar([x + 0.05 for x in xs], [d for d in data_values],
                width=0.2, color='red', alpha=0.7, zorder=2)
        plt.xticks(xs, data_names)

        fig.autofmt_xdate(rotation=25)

        plt.legend(loc='upper right')
        fig.savefig('data/countUniqueUsers.png')
        plt.close()

    def get_graph_counts_starts(self):
        data_values = []
        data_names = []
        for item in self.data:
            data_names.append(item['date'])
            data_values.append(item['counts'])

        dpi = 80
        fig = plt.figure(dpi=dpi, figsize=(512 / dpi, 384 / dpi))
        mpl.rcParams.update({'font.size': 10})

        ax = plt.axes()
        ax.yaxis.grid(True, zorder=1)

        xs = range(len(data_names))

        plt.bar([x + 0.05 for x in xs], [d for d in data_values],
                width=0.2, color='red', alpha=0.7, zorder=2)
        plt.xticks(xs, data_names)

        fig.autofmt_xdate(rotation=25)

        plt.legend(loc='upper right')
        fig.savefig('data/countsStarts.png')
        plt.close()
