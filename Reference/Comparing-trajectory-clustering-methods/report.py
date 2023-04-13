import argos.util as util
import math
import matplotlib.pyplot as plt
import argos.noise as reduc
plt.rcParams["font.sans-serif"]=["SimHei"] #设置字体
plt.rcParams["axes.unicode_minus"]=False #该语句解决图像中的“-”负号的乱码问题

base_color = plt.rcParams['axes.prop_cycle'].by_key()['color'][0]
def plot_traj(x, color=base_color):  # To plot a set of points in 2D
  plt.scatter([x[0] for x in x], [x[1] for x in x], c=color, s = 20)
  plt.plot([x[0] for x in x], [x[1] for x in x], c=color)


def create_point( point, azimuth):
    az = (azimuth / 180) * math.pi
    p = util.get_point( point, az, 10)
    a = []
    a.append(p[0])
    a.append(p[1])
    a.append(0)
    a.append(azimuth)
    return a


traj = []
start = [0, 0, 0, 30]
p = start
for i in range(20):
    p = create_point(p, 30)
    traj.append(p)

for i in range(25):
    p = create_point(p, 10)
    traj.append(p)

az = 10
for i in range(20):
    az = az + 10
    p = create_point(p, az)
    traj.append(p)


fig,ax = plt.subplots(figsize=(12,6))
plot_traj(traj)
for point in traj:
    point[0] += 300
traj = reduc._segmentation(traj)
plot_traj(traj, "r")
# plt.axes().set_aspect(1)
plt.title("轨迹压缩")
plt.grid()
plt.savefig('轨迹分割.png',bbox_inches='tight')