import tkinter as tk
from tkinter import *
from tkinter import filedialog, simpledialog
from PIL import ImageTk,Image
import time
import threading

from Annotator.frame import Frame
import cv2


class Annotator():
	# TODO: open folder instead of video so you can store original file and new file
	# TODO: export environment into github
	# TODO: hover over box edge to show identity -- increase box width
	# TODO: opening a second video

	def __init__(self):
	# Instance Variables
		# DISPLAY
		self.width, self.height = 960, 600
		self.leftPanelWidth = 200
		self.leftPanelHeight_Row0 = 200
		self.leftPanelHeight_Row1 = 100
		self.leftPanelHeight_Row2 = 50

		# FILLING VIDEO
		self.filling = False
		self.tempCount = 0

		# PLAYING VIDEO
		self.video = None
		self.stopEvent = threading.Event()
		self.playing = False
		self.frames = [Frame(frameNum=0)] #TODO: ADDING FRAME 1 TWICE?
		self.curr = None #Frame(frameNum=0) #, img=None, boxes=None)
		self.displayedImage = None

		# BOUNDING BOXES
		# self.idColors = {0: "white"} # colors for each index
		self.drawing = False
		self.edited = False
		self.rect = None
		self.minBoxSize = 10
		self.curr_box = {"x1":0, "y1":0, "x2":0, "y2":0}
		self.curr_id = 0
		self.saveBox = None
		self.topLevelOpen = False
		self.boxes = {}

		# INSTANCES

		# TEXT FILES
		self.frameswithboxes = []
		self.fillFiles()

	# Display
		# WINDOW
		self.window = Tk()
		self.window.title("Annotator")
		self.canvas = Canvas(master=self.window, width=self.width, height=self.height, relief=SUNKEN)
		self.window.minsize(self.width, self.height)

		# HEADER
		self.lbl_header = tk.Label(master=self.canvas,text="No file loaded")

		# TOOLBAR
		self.frm_toolbar = tk.Frame(master=self.canvas, height=10)
		self.btn_open = tk.Button(master=self.frm_toolbar, text="Open File", command=self.openDir)
		self.btn_next = tk.Button(master=self.frm_toolbar, text="Next Frame", command=self.btn_next)
		self.btn_prev = tk.Button(master=self.frm_toolbar, text="Prev Frame", command=self.btn_prev)
		self.btn_start = tk.Button(master=self.frm_toolbar, text="Start", command=self.start)
		self.btn_stop = tk.Button(master=self.frm_toolbar, text="Stop", command=self.stop)
		self.lbl_frameNum = tk.Label(master=self.frm_toolbar,text=" Frame Number: ")
		self.btn_open.grid(row=0, column=0)
		self.btn_next.grid(row=0, column=1)
		self.btn_prev.grid(row=0, column=2)
		self.btn_start.grid(row=0, column=3)
		self.btn_stop.grid(row=0, column=4)
		self.lbl_frameNum.grid(row=0, column=5)
		self.frm_toolbar.grid(row=1, column=0)

		# Main Elements
		# 		       Header
		#		      Tool Bar
		#            Main Frame
		#   LEFT PANEL (frm)   LABEL
		# |   edit buttons   | image |
		# | identities panel |       |
		# |    checkboxes    |       |
		self.frm_main = tk.Frame(master=self.canvas, width=10)
		self.frm_leftPanel = tk.Frame(master=self.frm_main)

		# LEFT PANEL (frm)
		# edit buttons
			# Draw New Box -- choose id in side panel, draw new box
			# Replace Box -- selectbox(), dialog = replace?, delete selected box, click again = draw new box
			# Change ID -- selectbox(), dialog = choose new id, update curr.boxes
				# selectbox() -- hover over box, highlight edge when over, click = select

		# identities panel

		# checkboxes
			# Show Prev Frame Boxes -- checkbox (swaps to "hide")
			# Show Next Frame Boxes -- checkbox (swaps to "hide") -- need in case bird enters frame but isn't detected immediately

		# On next or finish drawing -- error if any boxes share an id, confirm boxes and curr.commitEdits

		# edit buttons
		self.frm_editor = tk.Frame(master=self.frm_leftPanel)
		self.btn_editAndSave = tk.Button(master=self.frm_editor, text="Close Editor & Save", command=self.editAndSave, width=15)
		self.btn_newBox = tk.Button(master=self.frm_editor, text="Create new box", command=self.newBox)
		self.btn_redrawBox = tk.Button(master=self.frm_editor, text="Redraw box", command=self.redrawBox)
		self.btn_changeId = tk.Button(master=self.frm_editor, text="Change box ID", command=self.changeId)
		self.btn_editAndSave.grid(sticky=N+W, row=0, column=0)
		# in editAndSave()
		# self.btn_newBox.grid(row=1, column=0)
		# self.btn_redrawBox.grid(row=2, column=0)
		# self.btn_changeId.grid(row=3, column=0)
		self.editAndSave()
		self.frm_editor.grid(sticky=N+W, row=0, column=0)

		# identities panel

		# checkboxes

		# format
		self.frm_leftPanel.grid_rowconfigure(0, minsize=self.leftPanelHeight_Row0)
		self.frm_leftPanel.grid_rowconfigure(1, minsize=self.leftPanelHeight_Row1)
		self.frm_leftPanel.grid_rowconfigure(2, minsize=self.leftPanelHeight_Row2)


		# LABEL
		self.cvs_image = tk.Canvas(master=self.frm_main, width = self.width, height=self.height)

		self.frm_leftPanel.grid(row=0, column=0, sticky='nsew')
		self.cvs_image.grid(row=0,column=1, sticky='nsew')
		self.frm_main.grid_columnconfigure(0, minsize=self.leftPanelWidth)


	# Bindings
		# PLAYING VIDEO
		self.window.bind('<Left>', self.leftkey)
		self.window.bind('<Right>', self.rightkey)

		# BOUNDING BOXES
		# TODO: add undo button
		self.window.bind('<Escape>', self.key_esc)
		self.cvs_image.bind("<ButtonPress-1>", self.click)
		self.cvs_image.bind("<B1-Motion>", self.drag)
		self.cvs_image.bind("<ButtonRelease-1>", self.release)

	# Show
		self.showElements()
		self.canvas.pack()
		self.window.mainloop()

	# BOUNDING BOXES
	def selectBox(self):
		pass
		# hovering on image will highlight edges and let you select already drawn box

	def selectId(self):
		pass
		# hovering on ids will highlight rows and let you select existing id or create new one

	def newBox(self):
		self.penDown()
		# selectId(self)

	def redrawBox(self):
		pass
		# erase selectBox() but store its id
		# pendown()

	def changeId(self):
		pass
		# selectBox()
		# dialog asking to (1) select another box on screen (2) select id in list or create new id
		# (1) -> swapId() PUT ONTO STACK TO RUN AT CONFIRM
		# (2) -> updateId()

	def editAndSave(self):
		if self.btn_editAndSave['text'] == "Open Editor":
			self.btn_newBox.grid(sticky=N+W, row=1, column=0)
			self.btn_redrawBox.grid(sticky=N+W,row=2, column=0)
			self.btn_changeId.grid(sticky=N+W, row=3, column=0)
			self.btn_editAndSave.config(text="Close Editor & Save")
		else:
			self.btn_newBox.grid_forget()
			self.btn_redrawBox.grid_forget()
			self.btn_changeId.grid_forget()
			self.btn_editAndSave.config(text="Open Editor")

	def penDown(self):
		self.drawing = True

	def penUp(self):
		self.drawing = False

	def click(self, event):
		# select id first (or say new bird)
		if self.drawing:
			self.curr_box = {"x1":0, "y1":0, "x2":0, "y2":0}
			self.curr_box['x1'], self.curr_box['y1'] = event.x, event.y
			self.rect = self.cvs_image.create_rectangle(event.x, event.y, event.x, event.y, outline="white", width=2)

	def drag(self, event):
		if self.drawing:
			self.cvs_image.coords(self.rect, self.curr_box['x1'], self.curr_box['y1'], event.x, event.y)

	def release(self, event):
		if self.drawing:
			if abs(event.x - self.curr_box['x1']) < self.minBoxSize or abs(event.y - self.curr_box['y1']) < self.minBoxSize:
				self.cvs_image.delete(self.rect)
			elif not self.topLevelOpen:
				if self.saveOrCancel(event):
					self.curr_box['x2'], self.curr_box['y2'] = event.x, event.y
					self.curr_box['id'] = self.curr_id
					# self.curr.addBox(self.curr_box)
		if self.btn_editAndSave['text'] == "Close Editor & Save":
			self.drawing = True

	def saveOrCancel(self, event):
		self.topLevelOpen = True
		self.win = Toplevel()

		# Display
		self.win.geometry("+%d+%d" % (event.x, event.y))
		self.win.minsize(width=300, height=20)
		self.win.grid_columnconfigure(0, weight=1)
		self.win.grid_columnconfigure(1, weight=1)
		self.win.grid_rowconfigure(0, weight=1)
		self.win.grid_rowconfigure(1, weight=1)

		# Features
		self.win.title('New bounding box')
		message = "coords / identity"
		Label(self.win, text=message).grid(row=0, column=0, columnspan=23, sticky=W+E)
		Button(self.win, text='Cancel', command=self.btn_cancel).grid(row=1, column=0)
		Button(self.win, text='Confirm', command=self.btn_confirm).grid(row=1, column=1)

		# Window Cases
		self.win.protocol("WM_DELETE_WINDOW", self.miniClose)
		return self.saveBox

	def btn_cancel(self):
		self.cvs_image.delete(self.rect)
		self.saveBox = False
		self.rect = None
		self.win.destroy()
		self.topLevelOpen = False

	def btn_confirm(self):
		self.saveBox = True
		self.win.destroy()
		self.topLevelOpen = False

	def miniClose(self):
		self.btn_cancel()

	def key_esc(self, event):
		self.drawing = False
		if self.rect != None:
			self.cvs_image.delete(self.rect)


	# DISPLAY
	def showElements(self):
		self.lbl_header.grid(row=0, column=0)
		self.frm_toolbar.grid(row=1, column=0)
		self.frm_main.grid(row=2, column=0)

	def leftkey(self, event):
		self.prev()

	def rightkey(self, event):
		self.next()

	# OPENING VIDEO
	def openDir(self):
		self.fillFiles()
		fileTypes =  [('Videos', '*.mp4')]
		filename = tk.filedialog.askopenfilename(title = "Select file",filetypes = fileTypes)
		self.openVideo(filename)


	def openVideo(self, filename):
		self.video = cv2.VideoCapture(filename)
		self.lbl_header.config(text=filename)
		self.filling = True
		self.start()
		# self.stop()

		self.window.update()

	def frameToImage(self, freeze):
		rgb = cv2.cvtColor(freeze, cv2.COLOR_BGR2RGB)
		img = Image.fromarray(rgb)
		width = int(self.height/img.height*img.width)
		imgResized = img.resize((width, self.height), Image.NEAREST)
		return ImageTk.PhotoImage(imgResized)


	# PLAYING VIDEO
	# TODO check if there's a vid
	def newFrame(self):
		if not self.displayedImage is None:
			self.cvs_image.delete(self.displayedImage)
		self.displayedImage = self.cvs_image.create_image(0, 0, anchor="nw", image=self.curr.img)
		self.lbl_frameNum.config(text="Frame Number: " + str(self.curr.frameNum))

	def next(self):
		if not self.playing:
			self.stop()

		if self.edited:
			commitEdits()

		if self.curr.frameNum == len(self.frames) - 1:
			print("last frame - shouldn't be able to go past this")

		self.curr = self.frames[self.curr.frameNum + 1]
		print("loading frame: " + str(self.curr.frameNum))
		#self.lbl_frameNum.config(text="Frame Number: " + str(self.curr.frameNum))  # in newFrame
		self.newFrame()
		time.sleep(.1) # TODO: fps?

		# this case shouldn't happen anymore
		# else:
		# 	more, freeze = self.video.read()
		# 	if more:
		# 		self.img = self.frameToImage(freeze)
		# 		self.curr = Frame(frameNum=self.curr.frameNum + 1, img=self.img)
		# 		self.frames.append(self.curr)
		# 		self.lbl_frameNum.config(text="Frame Number: " + str(self.curr.frameNum))
		# 		self.newFrame()
		# 	else:
		# 		print("video's over")


	def prev(self):
		if not self.playing:
			self.stop()

		if self.edited:
			commmitEdits()

		if self.curr.frameNum > 1:
			self.curr = self.frames[self.curr.frameNum - 1]
			self.newFrame()

	def start(self):
		if not self.video is None:
			self.stopEvent.clear()
			self.thread = threading.Thread(target=self.videoLoop, args=())
			self.thread.start()

			# set a callback to handle when the window is closed
			# self.window.wm_protocol("WM_DELETE_WINDOW", self.onClose)

	def stop(self):
		self.playing = False
		self.stopEvent.set()

	def videoLoop(self):
		try:
			while not self.stopEvent.is_set():
				if self.filling:
					self.fillVideoNext()
				else:
					self.playing = True
					self.next()

		except RuntimeError as e:
			print("[INFO] caught a RuntimeError")

	def fillVideoNext(self):
		more, freeze = self.video.read()
		self.tempCount += 1
		if more:
			img = self.frameToImage(freeze)
			if self.tempCount >= len(self.frames): # file included no lines of instances on this frame
				curr = Frame(frameNum=self.tempCount, img=img)
				print("filled frame: " + str(curr.frameNum))
				self.frames.append(curr)
			else:
				self.frames[self.tempCount].img = img
		else: # finished loading
			self.stopEvent.set()
			self.filling = False
			self.curr = self.frames[1]
			for i in self.frames:
				print(str(i.frameNum))
			self.newFrame()


	def commitEdits(self):
		pass
		# self.curr.commit() -- update self.curr.boxes to include the new boxes and identities
		# self.frames[self.curr.frameNum - 1] = self.curr
		# self.edited = False

	def btn_next(self):
		self.playing = False
		self.next()

	def btn_prev(self):
		self.playing = False
		self.prev()


	# WINDOW CASES
	def onClose(self):
		# TODO save everything before closing
		self.stop()

	# TEXT FILES
	def fillFiles(self):
		frm_index = 0
		id_index = 1
		box_index = 2
		# each frame stores which identities are on its frame
		# each identity stores its box on each frame
		file = open("/Users/laurenkafkaloff/Desktop/TestData.txt","r")
		for line in file:
			# 1, 3, 794.27, 247.59, 71.245, 174.88, -1, -1, -1, -1
			textArray = line.split(",")
			a_frame = int(textArray[frm_index])
			if a_frame == len(self.frames):
				self.frames.append(Frame(frameNum=a_frame))
			x1 = textArray[box_index]
			y1 = textArray[box_index + 1]
			x2 = x1 + textArray[box_index + 2]
			y2 = y1 + textArray[box_index + 3]

			box =  {"x1":x1, "y1":y1, "x2":x2, "y2":y2}
			self.frames[a_frame].addInstance(textArray[id_index], box)
			# print(str(a_frame) + ":  " + str(textArray[id_index]) + "= " + x1 + " " + y1)
		for frame in self.frames:
			if not frame is None:
				for i in frame.instances.keys():
					print(str(i) + ": " + str(frame.instances[i]))

		# LOAD A SPECIFIED RANGE OF FRAMES AHEAD OF TIME -- WHEN SWAPPINNG IDS, DON'T LOAD PAST THIS EITHER
		# first create all the frames w instances and frame num
		# go back through and put all the images into the frames with a "show = false"


		# NEXT STEP: DRAW THE BOXES
			# run fillFiles()
			# run img into frames (or it'll just get overwritten in videoloop)
			# draw rects onto frame when next()
