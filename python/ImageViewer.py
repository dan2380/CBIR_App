# ImageViewer.py
# Program to start evaluating an image in python
#
# Show the image with:
# os.startfile(imageList[n].filename)


from tkinter import *
import math, os
from PixInfo import PixInfo


# Main app.
class ImageViewer(Frame):
    # Constructor.
    def __init__(self, master, pixInfo, resultWin):

        Frame.__init__(self, master)
        self.chosen_image = " "
        self.master = master
        self.pixInfo = pixInfo
        self.resultWin = resultWin
        self.image_sizes = self.pixInfo.get_image_sizes()
        self.check_var = 0
        self.current_page = 0
        self.colorCode = pixInfo.get_colorCode()
        self.intenCode = pixInfo.get_intenCode()

        # Full-sized images.
        self.imageList = pixInfo.get_imageList()

        # file names of images
        self.fileList = pixInfo.get_file_list()

        # Thumbnail sized images.
        self.photoList = pixInfo.get_photoList()

        # Image size for formatting.
        self.xmax = pixInfo.get_xmax()
        self.ymax = pixInfo.get_ymax()

        # Create Main frame.
        mainFrame = Frame(master)
        mainFrame.pack(fill=BOTH, expand=True)

        # Create Picture chooser frame.
        listFrame = Frame(mainFrame)
        listFrame.pack(side=LEFT)

        # Create Control frame.
        controlFrame = Frame(mainFrame)
        controlFrame.pack(side=RIGHT)

        # Create Preview frame.
        previewFrame = Frame(mainFrame,
                             width=self.xmax + 45, height=self.ymax)
        previewFrame.pack_propagate(0)
        previewFrame.pack(fill=BOTH, expand=True)
        previewFrame.grid_rowconfigure(0, weight=1)
        previewFrame.grid_columnconfigure(0, weight=1)

        # Create Results frame.
        resultsFrame = Frame(self.resultWin)
        resultsFrame.pack(side=TOP)
        self.canvas = Canvas(resultsFrame)
        self.resultsScrollbar = Scrollbar(resultsFrame)
        self.resultsScrollbar.pack(side=RIGHT, fill=Y)

        # Layout Picture Listbox.
        self.listScrollbar = Scrollbar(listFrame)
        self.listScrollbar.pack(side=RIGHT, fill=Y)
        self.list = Listbox(listFrame,
                            yscrollcommand=self.listScrollbar.set,
                            selectmode=BROWSE,
                            height=10)
        for i in range(len(self.imageList)):
            self.list.insert(i, "Image " + str(i + 1))
        self.list.pack(side=LEFT, fill=BOTH)
        self.list.activate(1)
        self.list.bind('<<ListboxSelect>>', self.update_preview)
        self.listScrollbar.config(command=self.list.yview)

        # Layout Controls.
        self.b1 = Button(controlFrame, text="Color-Code",
                         padx=10, width=10,
                         command=lambda: self.find_distance(method='color_code_method'))
        self.b1.grid(row=1, sticky=EW)

        b2 = Button(controlFrame, text="Intensity",
                    padx=10, width=10,
                    command=lambda: self.find_distance(method='intensity_method'))
        b2.grid(row=2, sticky=EW)

        b3 = Button(controlFrame, text="Color code & Intensity",
                    padx=10, width=20,
                    command=lambda: self.find_distance(method="inten_color_method"))
        b3.grid(row=3, sticky=EW)
        
        b4 = Button(controlFrame, text="Reset relevance",
                    padx=10, width=20,
                    command=lambda: self.reset_weights())
        b4.grid(row=4, sticky=EW)

        self.relevant_text = StringVar()
        self.relevance_textbox = Entry(controlFrame, textvariable=self.relevant_text)
        self.relevance_textbox.grid(row=5, sticky=EW)
        self.submit_relevant = Button(controlFrame, text="Submit relevant", padx=10, width=20,
                                      command=lambda: self.update_weights_procedure())
        self.submit_relevant.grid(row=6, sticky=EW)

        # self.var = Checkbutton(controlFrame, text="Relevant", onvalue=1, offvalue=0)
        # self.check_list = []

        # Layout Preview.
        self.selectImg = Label(previewFrame,
                               image=self.photoList[0], width=100)
        self.selectImg.grid(sticky='nesw', column=0, row=0)

        # Initialize the canvas with dimensions equal to the
        # number of results.
        fullsize = (0, 0, (self.xmax * 50), (self.ymax * 50))
        self.canvas.delete(ALL)
        self.canvas.config(
            width=self.xmax * 100,
            height=self.ymax * 100 / 2,
            yscrollcommand=self.resultsScrollbar.set,
            scrollregion=fullsize)
        self.canvas.pack(fill='both')
        self.resultsScrollbar.config(command=self.canvas.yview)

        # array of tuples
        self.page_images = [None] * 5

        # buttons for the pages
        previous_button = Button(resultsFrame, text="Previous page",
                                 padx=10, width=10,
                                 command=lambda: self.previous_page())
        previous_button.pack(side=LEFT)

        next_button = Button(resultsFrame, text="Next page",
                             padx=10, width=10,
                             command=lambda: self.next_page())
        next_button.pack(side=RIGHT)

        self.page_label = Label(resultsFrame, text="Page " + str(self.current_page + 1),
                                font="Times 18 bold")
        self.page_label.pack(padx=100)

    def reset_weights(self):
        pixInfo.weights = [1/89] * 89
        self.relevant_text.set('')
        
    def update_weights_procedure(self):
        raw_text = self.relevant_text.get()
        str_list = raw_text.split(" ")
        query_img_number = int(str(self.chosen_image)[7:])
        relevant_list = [int(i) for i in str_list if i != '']
        relevant_list.insert(0, query_img_number)
        pixInfo.update_weights(relevant_imgs=relevant_list)

    def get_relevant(self):
        relevant = self.relevant_text.get()
        self.relevant_list = relevant.split()
        chosen_image_index = int(str(self.chosen_image)[7:]) - 1
        self.relevant_list.insert(0, chosen_image_index)
        int_array = [int(numeric_string) for numeric_string in relevant_list]

    # Event "listener" for listbox change.
    def update_preview(self, event):

        i = self.list.curselection()[0]
        self.chosen_image = self.photoList[int(i)]
        self.selectImg.configure(
            image=self.chosen_image)

    def previous_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.page_label['text'] = "Page " + str(self.current_page + 1)
        self.update_results()

    def next_page(self):
        if self.current_page < 4:  # change hard-coded 6 to be len(imgs/# of imgs per page) later..
            self.current_page += 1
            self.page_label['text'] = "Page " + str(self.current_page + 1)
        self.update_results()

    # Find the Manhattan Distance of each image and return a
    # list of distances between image i and each image in the
    # directory uses, the comparison method of the passed
    # binList

    # the "method" argument can have one of the two following values(as strings):
    # color_code_method
    # intensity_method
    def find_distance(self, method):
        # "chosen_image_index" is the index of the chosen image in the
        # image list
        chosen_image_index = int(str(self.chosen_image)[7:]) - 1
        weights = []
        bins_to_compare = []
        if method == "color_code_method":
            bins_to_compare = self.colorCode
            for i in range(89):
                weights.append(1)
        elif method == "intensity_method":
            bins_to_compare = self.intenCode
            for i in range(89):
                weights.append(1)
        elif method == "inten_color_method":
            bins_to_compare = pixInfo.get_normalized_feature()

        # now apply the manhattan distance technique,
        # compute the distance between the chosen index image
        # and all other images
        chosen_image_bin = bins_to_compare[chosen_image_index]

        image_info = []
        for i in range(len(bins_to_compare)):
            other_image_bin = bins_to_compare[i]
            other_image_img = self.photoList[i]
            other_image_file = self.fileList[i] # all the images file name

            manhattan_distance = 0
            if (i != chosen_image_index):
                chosen_image_size = self.image_sizes[chosen_image_index]
                other_image_size = self.image_sizes[i]
                # iterate through the items in each bin
                for j in range(len(chosen_image_bin)):
                    chosen_image_bin_value = chosen_image_bin[j]
                    other_image_bin_value = other_image_bin[j]
                    manhattan_distance += pixInfo.weights[j] * abs(chosen_image_bin_value / chosen_image_size
                                                                   - other_image_bin_value / other_image_size)

            # tuple of the form (image, image file name, manhattan distance)
            info = (other_image_img, other_image_file, manhattan_distance)
            image_info.append(info)

        # sort the image info by their manhattan distances
        image_info.sort(key=lambda x: x[2])
        self.put_sorted_images_in_pages_array(image_info)
        self.update_results()

        return image_info

    # places image info(image file name, image) into the page buckets that they belong to
    # in "self.page_images"
    def put_sorted_images_in_pages_array(self, image_info):
        curr_index = 0
        for i in range(0, 5):
            page_image_info = []
            for j in range(0, 20):
                page_image_info.append(image_info[curr_index])
                curr_index += 1
            self.page_images[i] = (page_image_info)

    # Update the results window with the sorted results.
    def update_results(self):

        cols = int(math.ceil(math.sqrt(len(self.page_images[self.current_page]))))
        fullsize = (0, 0, (self.xmax * cols), (self.ymax * (cols - 1)))

        # Initialize the canvas with dimensions equal to the
        # number of results.
        self.canvas.delete(ALL)
        self.canvas.config(
            width=self.xmax * cols,
            height=self.ymax * cols / 2,
            yscrollcommand=self.resultsScrollbar.set,
            scrollregion=fullsize)
        self.canvas.pack()
        self.resultsScrollbar.config(command=self.canvas.yview)

        # photo remain is the list of photos to be placed
        # each item in "photoRemain" is a tuple of the form
        # (filename, img)
        photoRemain = []

        for photo_item in self.page_images[self.current_page]:
            photo_file_name = photo_item[1]
            photo_image = photo_item[0]
            photoRemain.append((photo_file_name, photo_image))

        # Place images on buttons, then on the canvas in order
        # by distance.  Buttons envoke the inspect_pic method.
        rowPos = 0
        while photoRemain:
            photoRow = photoRemain[:cols]
            photoRemain = photoRemain[cols:]
            colPos = 0
            for (filename, img) in photoRow:
                link = Button(self.canvas, image=img, text=filename)
                handler = lambda f=filename: self.inspect_pic(f)
                link.config(command=handler)
                link.pack(side=LEFT, expand=YES)

                self.canvas.create_window(
                    colPos,
                    rowPos,
                    anchor=NW,
                    window=link,
                    width=self.xmax,
                    height=self.ymax)

                img_label = Label(link, text=filename[7:])
                img_label.pack(side=BOTTOM)
                # if self.var.getint() == 1:
                #     img_checkbox = Checkbutton(link, text="Relevant", variable=self.relevant_list[self.counter])
                #     img_checkbox.pack(side=BOTTOM)
                # else:
                #     self.relevant_list.clear()
                # self.counter += 1
                colPos += self.xmax
            rowPos += self.ymax

    # Open the picture with the default operating system image
    # viewer.
    def inspect_pic(self, filename):
        os.startfile(filename)


# Executable section.
if __name__ == '__main__':
    root = Tk()
    root.title('Image Analysis Tool')

    resultWin = Toplevel(root)
    resultWin.title('Result Viewer')
    resultWin.protocol('WM_DELETE_WINDOW', lambda: None)
    resultWin.geometry("500x290")

    pixInfo = PixInfo(root)

    imageViewer = ImageViewer(root, pixInfo, resultWin)

    root.mainloop()