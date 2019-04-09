# -*- coding:utf-8 _*-
"""
@author:Chexqi
@time: 2019/01/08
matplotlib套索交互式选点。按键功能说明：
1.按‘+’，套索添加点
2.按‘-’，套索删除点
3.按‘d’，保存选中的点，需要输入保存的文件名
4.按‘r’，复位，清空选中的点
"""
from matplotlib import colors as mcolors, path
from matplotlib.collections import RegularPolyCollection
import matplotlib.pyplot as plt
from matplotlib.widgets import Lasso
import numpy as np
import cv2


class Datum(object):  # 每个点坐标、颜色的类
	colorin = mcolors.to_rgba("red")  # 选中点为红色
	colorout = mcolors.to_rgba("blue")  # 未选中点为蓝色

	def __init__(self, x, y, include=False):
		self.x = x
		self.y = y
		if include:
			self.color = self.colorin
		else:
			self.color = self.colorout


class LassoManager(object):
	def __init__(self, fig, ax, data):
		self.fig = fig
		self.axes = ax
		self.canvas = ax.figure.canvas  # 画布
		self.data = data

		self.Nxy = len(data)  # 数据长度
		self.facecolors = [d.color for d in data]  # 所有点的颜色
		self.xys = [(d.y, d.x) for d in data]  # 所有点的坐标
		self.collection = RegularPolyCollection(  # 多边形集
			4, sizes=(10,),  # 4边形，大小
			facecolors=self.facecolors,  # 颜色
			offsets=self.xys,  # 位置
			transOffset=ax.transData)
		ax.add_collection(self.collection)
		self.cid = self.canvas.mpl_connect('button_press_event', self.MousePress)  # 事件连接，鼠标按键触发MousePress函数
		self.cid = self.canvas.mpl_connect('key_press_event', self.KeyboardPress)  # 事件连接，按键按下触发key_press_event
		self.KeyFun = '+'  # 当前按键功能 '+':添加点，'-':删除点
		ax.set_xlabel('+')  # 默认添加点

	def callback(self, verts):
		self.facecolors = self.collection.get_facecolors()
		p = path.Path(verts)
		ind = p.contains_points(self.xys)  # 路径中包含的点
		for i in range(len(self.xys)):
			if self.KeyFun == '+':  # 如果是添加点，则路径中的点变红色
				if ind[i]:
					self.facecolors[i] = Datum.colorin  # 路径中包含的点变红色
			elif self.KeyFun == '-':  # 如果是删除点，则路径中的点变蓝色
				if ind[i]:
					self.facecolors[i] = Datum.colorout  # 路径中包含的点变红色
		self.canvas.draw_idle()  # 套索路径不再显示
		# self.canvas.widgetlock.release(self.lasso)    # 释放lasso
		del self.lasso

	def MousePress(self, event):
		if self.canvas.widgetlock.locked():
			return
		if event.inaxes is None:
			return
		self.lasso = Lasso(event.inaxes,
		                   (event.xdata, event.ydata),
		                   self.callback)

	# acquire a lock on the widget drawing
	# self.canvas.widgetlock(self.lasso)      # 将widget锁定，此时lasso无效

	def KeyboardPress(self, event):
		# print('press', event.key)  # event.key按键信息
		if event.key in ['+', '-']:
			self.KeyFun = event.key
			self.axes.set_xlabel(event.key)
			self.fig.canvas.draw()  # 画布重绘
		elif event.key == 'd':  # download 保存选中的点
			SelPoints = np.empty((0, 2), dtype=np.float32)
			for i in range(len(self.xys)):
				if np.sum(np.array(self.facecolors[i]) == np.array(Datum.colorin)) == 4:
					SelPoints = np.vstack((SelPoints, self.xys[i]))
			FileName = str(input("Save File Name:"))
			np.savetxt(FileName + '.txt', SelPoints, '%f')  # 保存选中的点坐标，两位有效数字
			print('Save Done!!!')
		elif event.key == 'r':  # 复位，重新开始选点
			self.KeyFun = '+'  # 当前按键功能 '+':添加点，'-':删除点
			self.axes.set_xlabel('+')  # 默认添加点
			for i in range(len(self.xys)):  # 点颜色复位
				self.facecolors[i] = Datum.colorout


if __name__ == '__main__':
	# %% 输入图片文件面和特征点文件名
	ImgPath = '01.bmp'
	CenterPoints = np.loadtxt('points2D.txt')   # N*2

	# %% 套索去除光条上的杂点
	Img = cv2.imread(ImgPath, 0).astype(np.uint16)
	data = [Datum(*xy) for xy in CenterPoints]  # 所有数据，每个点是一个类
	fig = plt.figure()
	ax = plt.axes(xlim=(0, Img.shape[1]), ylim=(Img.shape[0], 0), autoscale_on=False)
	lman = LassoManager(fig, ax, data)
	plt.imshow(Img, 'gray')
	plt.show()

