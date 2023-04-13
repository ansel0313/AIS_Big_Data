#!/usr/bin/env python

"""
Title: danish_graph_tracks.py
Objective: Graph Danish Data
Creator: Stig Terrebonne
Date: July 25th, 2018
"""

import numpy as np
import folium

sorted_data = np.load('../../data/interim/danish_sorted_data.npz')
df = sorted_data['sorted_data']

test = []
temp = []

# take out first column
second_column = df[:, 1]

k = 0
last_count = 0
unique_vals, unique_count = np.unique(second_column, return_counts=True)
for i in range(len(df)):
    temp.append(tuple([df[i][2], df[i][3]]))
    if (i - last_count) == unique_count[k]:
        test.append(temp)
        temp = []
        last_count = i
        k += 1

center = [df[i-1][2], df[i-1][3]]

m = folium.Map(location=center, tiles="Stamen Toner", zoom_start=12)

for i in range(len(test[600:700])):
    for j in range(len(test[i])):
        folium.Circle(
            radius=2,
            location = test[i][j],
        ).add_to(m)

m.save("danish_tracks.html")
