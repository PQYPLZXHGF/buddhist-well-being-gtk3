
"""
Documentation:
https://developer.gnome.org/gtk3/stable/
http://lazka.github.io/pgi-docs/Gtk-3.0/index.html
https://python-gtk-3-tutorial.readthedocs.io/en/latest/index.html


"""

from gi.repository import Gtk
import bwb_model
import time
from functools import partial
import datetime

TEN_OBS_TEXT_WIDTH = 17 # in number of characters (so pixels can very)
TEN_OBS_TEXT_FONT_SIZE = 14
KARMA_TEXT_WIDTH = 30
KARMA_TEXT_FONT_SIZE = 10

DIARY_DATE_TEXT_WIDTH = 40
ADDING_TO_DIARY_TEXT_WIDTH = 80
DIARY_PIXEL_WIDTH = 300

### DIARY_TEXT_FONT_SIZE = 10


class WellBeingWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="Buddhist Well-Being")

        self.set_default_size(200, 300)

        self.diary_labels_lt = []  # Used in the gui update function
        t_observances_lt = bwb_model.ObservanceM.get_all()

        self.window_hbox = Gtk.Box(spacing = 16, orientation = Gtk.Orientation.HORIZONTAL)
        self.add(self.window_hbox)
        # Creating widgets..
        # ..ten practices

        self.left_vbox = Gtk.Box(orientation = Gtk.Orientation.VERTICAL, spacing = 16)
        ###self.left_vbox.set_size_request(10, 10)
        self.window_hbox.add(self.left_vbox)
        ########self.window_hbox.pack_start(self.left_vbox, True, True, 0)

        self.ten_observances_lb = Gtk.ListBox()
        self.ten_observances_lb.set_selection_mode(Gtk.SelectionMode.BROWSE)
        #- https://people.gnome.org/~gcampagna/docs/Gtk-3.0/Gtk.SelectionMode.html
        self.left_vbox.pack_start(self.ten_observances_lb, True, True, 0)
        for observance_item in t_observances_lt:
            row = Gtk.ListBoxRow()
            label = Gtk.Label(observance_item.short_name_sg, xalign=0)
            row.add(label)
            self.ten_observances_lb.add(row)

        self.ten_observances_lb.connect('row-activated', self.observance_selected_fn)

        self.ten_practices_details_ll = Gtk.Label("Nothing selected yet")
        self.left_vbox.pack_start(self.ten_practices_details_ll, True, True, 0)

        #..karma
        self.karma_lb = Gtk.ListBox()
        self.karma_lb.set_selection_mode(Gtk.SelectionMode.BROWSE)
        self.left_vbox.pack_start(self.karma_lb, True, True, 0)

        #..diary
        self.right_vbox = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
        self.window_hbox.add(self.right_vbox)
        self.diary_lb = Gtk.ListBox()
        self.diary_lb.set_selection_mode(Gtk.SelectionMode.NONE)
        self.right_vbox.pack_start(self.diary_lb, True, True, 0)

        """
        #..karma
        self.karma_lf = tkinter.ttk.LabelFrame(self, text="Karma") #, width=250, height=250
        self.karma_lf.pack(side=tkinter.LEFT, fill=tkinter.Y)
        self.karma_font = tkinter.font.Font(size=KARMA_TEXT_FONT_SIZE)
        self.karma_lb = tkinter.Listbox(
            self.karma_lf,
            selectbackground="yellow",
            selectmode=tkinter.SINGLE,
            width=KARMA_TEXT_WIDTH, height=18,
            font=self.karma_font,
            exportselection=False)
        self.karma_lb.bind("<Button-3>", self.open_karma_context_menu)
        self.karma_lb.pack(side=tkinter.TOP)
        self.karma_context_menu = tkinter.Menu(self, tearoff=0)
        self.karma_context_menu.add_command(label="Delete", command=partial(self.delete_karma, 42))

        #..adding new karma
        self.adding_new_karma_ey = tkinter.Entry(
            self.karma_lf,
            width=KARMA_TEXT_WIDTH)
        self.adding_new_karma_ey.pack(side=tkinter.TOP)
        #TODO: Limiting the text input area: http://stackoverflow.com/questions/11491161/limiting-entry-on-a-tk-widget
        self.adding_new_karma_bn = tkinter.Button(
            self.karma_lf,
            text="Add new karma",
            command=self.add_new_karma_button_pressed_fn
        )
        self.adding_new_karma_bn.pack(side=tkinter.TOP)

        # ..text area for adding to diary
        self.adding_text_to_diary_lf = tkinter.ttk.LabelFrame(self, text="Adding new")
        self.adding_text_to_diary_lf.pack(side = tkinter.TOP, anchor=tkinter.NW)
        self.adding_to_diary_date_ey = tkinter.Entry(
            self.adding_text_to_diary_lf,
            width=DIARY_DATE_TEXT_WIDTH)
        self.adding_to_diary_date_ey.insert(tkinter.END, "2015-01-09 13:42")
        self.adding_to_diary_date_ey.pack()
        ###self.adding_to_diary_font = tkinter.font.Font(size=TEN_OBS_TEXT_FONT_SIZE)
        self.adding_text_to_diary_tt = tkinter.Text(
            self.adding_text_to_diary_lf,
            width=ADDING_TO_DIARY_TEXT_WIDTH,
            height=4)
        self.adding_new_text_scrollbar = tkinter.Scrollbar(
            self.adding_text_to_diary_lf, orient=tkinter.VERTICAL, command=self.adding_text_to_diary_tt.yview)
        self.adding_new_text_scrollbar.pack(side = tkinter.RIGHT, fill=tkinter.Y)
        self.adding_text_to_diary_tt['yscrollcommand'] = self.adding_new_text_scrollbar.set
        self.adding_text_to_diary_tt.pack(side = tkinter.LEFT)
        self.adding_new_button = tkinter.ttk.Button(self, text="Add to Diary", command=self.add_text_to_diary_button_pressed_fn)
        self.adding_new_button.pack(side = tkinter.TOP)

        # ..diary
        # Scrollbar solution inspired by
        # http://stackoverflow.com/questions/3085696/adding-a-scrollbar-to-a-group-of-widgets-in-tkinter
        self.diary_lf = tkinter.ttk.LabelFrame(self, text="Diary")
        self.diary_lf.pack(side = tkinter.LEFT, fill=tkinter.BOTH, expand=1)

        self.diary_canvas = tkinter.Canvas(self.diary_lf)
        self.diary_frame = tkinter.Frame(self.diary_canvas)
        self.diary_frame.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)
        self.diary_scrollbar = tkinter.Scrollbar(
            self.diary_lf, orient=tkinter.VERTICAL, command=self.diary_canvas.yview)
        self.diary_canvas.configure(yscrollcommand=self.diary_scrollbar.set)

        self.diary_scrollbar.pack(side = tkinter.RIGHT, fill=tkinter.Y)
        self.diary_canvas.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=1)  # , fill=tkinter.BOTH, expand=1
        self.diary_canvas.create_window((10, 10), window=self.diary_frame, anchor="nw", tags="self.diary_frame")

        self.diary_frame.bind("<Configure>", self.on_diary_frame_configure)

        self.pack()
        self.update_gui()

        """

        self.update_gui()

    def on_diary_frame_configure(self, i_event):
        self.diary_canvas.configure(scrollregion=self.diary_canvas.bbox("all"))

    def observance_selected_fn(self, i_listbox, i_row):
        #- http://lazka.github.io/pgi-docs/#Gtk-3.0/classes/ListBox.html#Gtk.ListBox.signals.row_activated
        t_selection_it = i_row.get_index() ###i_event.widget.curselection()[0]
        t_observance = bwb_model.ObservanceM.get(t_selection_it)
        self.ten_practices_details_ll.set_text(t_observance.sutra_text_sg)

        """
        for diary_item in bwb_model.DiaryM.get_all():
            if diary_item.observance_ref == t_selection_it:
                diary_item.marked_bl = True
        """

        self.update_gui()  # Showing habits for practice etc

    def add_new_karma_button_pressed_fn(self):
        t_cur_observance_sel_te = self.ten_observances_lb.curselection()
        t_observance_pos_it = -1
        if len(t_cur_observance_sel_te) > 0:
            t_observance_pos_it = t_cur_observance_sel_te[0]
        else:
            return
        t_text_sg = self.adding_new_karma_ey.get().strip() # strip is needed to remove a newline at the end (why?)
        if not (t_text_sg and t_text_sg.strip()):
            #TODO: Clear (there might be white space left)
            return
        t_last_pos_it = len(bwb_model.KarmaM.get_all_for_observance(t_observance_pos_it))
        bwb_model.KarmaM.add(t_observance_pos_it, t_last_pos_it, t_text_sg)

        self.adding_new_karma_ey.delete(0, tkinter.END)
        self.update_gui()

    def add_text_to_diary_button_pressed_fn(self):
        t_cur_observance_sel_te = self.ten_observances_lb.curselection()
        t_observance_pos_it = -1
        if len(t_cur_observance_sel_te) > 0:
            t_observance_pos_it = t_cur_observance_sel_te[0]
        if t_observance_pos_it == -1:
            return

        t_cur_karma_sel_te = self.karma_lb.curselection()
        t_karma_pos_it = -1
        if len(t_cur_karma_sel_te) > 0:
            t_karma_pos_it = t_cur_karma_sel_te[0]

        notes_pre_sg = self.adding_text_to_diary_tt.get(1.0, tkinter.END).strip()
        if notes_pre_sg == "":
            notes_sg = notes_pre_sg
        else:
            notes_sg = notes_pre_sg + "\n"
        bwb_model.DiaryM.add(int(time.time()), t_observance_pos_it, t_karma_pos_it, notes_sg)

        self.adding_text_to_diary_tt.delete(1.0, tkinter.END)
        self.ten_observances_lb.selection_clear(0)  # Clearing the selection
        self.karma_lb.selection_clear(0)
        self.update_gui()

    def open_karma_context_menu(self, i_event):
        print("opening menu")
        self.karma_context_menu.post(i_event.x_root, i_event.y_root)

    def delete_karma(self, i_it):
        print("deleting karma. i_it = " + str(i_it))

    def update_gui(self):

        self.karma_lb.foreach(lambda x: self.karma_lb.remove(x))
        t_cur_sel_row = self.ten_observances_lb.get_selected_row()
        if t_cur_sel_row is not None:
            t_cur_sel_it = t_cur_sel_row.get_index()
            print("t_cur_sel_it = " + str(t_cur_sel_it))
            t_karma_lt = bwb_model.KarmaM.get_all_for_observance(t_cur_sel_it)
            for karma_item in t_karma_lt:
                row = Gtk.ListBoxRow()
                label = Gtk.Label(karma_item.description_sg, xalign=0)
                print("karma_item.description_sg = " + karma_item.description_sg)
                row.add(label)
                self.karma_lb.add(row)
        self.karma_lb.show_all()



        t_prev_diary_item = None
        for diary_item in bwb_model.DiaryM.get_all():
            t_diary_entry_obs_sg = bwb_model.ObservanceM.get(diary_item.observance_ref).short_name_sg
            t_karma = bwb_model.KarmaM.get_for_observance_and_pos(
                diary_item.observance_ref, diary_item.karma_ref)

            if t_prev_diary_item == None or not is_same_day(t_prev_diary_item.date_added_it, diary_item.date_added_it):
                t_date_sg = datetime.datetime.fromtimestamp(diary_item.date_added_it).strftime("%A")

                t_new_day_ll = Gtk.Label(t_date_sg)
                self.right_vbox.pack_start(t_new_day_ll, True, True, 0)

                """
                t_new_day_ll = tkinter.Label(
                    self.diary_frame,
                    text=t_date_sg
                )
                t_new_day_ll.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)
                """

            if t_karma == None:
                t_diary_entry_karma_sg = ""
            else:
                t_diary_entry_karma_sg = t_karma.description_sg.strip() + " "

            """
            t_cur_observance_sel_te = self.ten_observances_lb.curselection()
            t_observance_pos_it = -1
            if len(t_cur_observance_sel_te) > 0:
                t_observance_pos_it = t_cur_observance_sel_te[0]
            # Message widget: http://effbot.org/tkinterbook/message.htm
            """

            t_label_text_sg = t_diary_entry_karma_sg + "[" + t_diary_entry_obs_sg.strip() + "] " + diary_item.notes_sg.strip()
            t_diary_entry_ll = Gtk.Label(t_label_text_sg)
            print("t_label_text_sg = " + t_label_text_sg)
            """
            t_diary_entry_ll = tkinter.Label(
                self.diary_frame,
                text=t_diary_entry_karma_sg + "[" + t_diary_entry_obs_sg.strip() + "] " + diary_item.notes_sg.strip(),
                justify=tkinter.LEFT, anchor=tkinter.W,
                width=52, wraplength=500,
                padx=15, pady=10,
                borderwidth="1", relief="raised",
                font=t_diary_entry_font
            )
            """
            """
            if t_observance_pos_it == diary_item.observance_ref:
                t_diary_entry_ll.configure(background="yellow")
            """

            # width=300,
            # relief="solid"raised
            # anchor=tkinter.E,
            # state=tkinter.ACTIVE
            ###t_diary_entry_ll.bind("<Button-1>", self.diary_entry_clicked)
            #######self.right_vbox.pack_start(t_diary_entry_ll, True, True, 0)
            ###t_diary_entry_ll.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

            row = Gtk.ListBoxRow()
            row.add(t_diary_entry_ll)
            self.diary_lb.add(row)

            t_prev_diary_item = diary_item

        self.diary_lb.show_all()

        """
        self.karma_lb.delete(0, tkinter.END)  # clearing all items

        t_cur_sel_te = self.ten_observances_lb.curselection()
        if len(t_cur_sel_te) > 0:
            t_observance_id_it = t_cur_sel_te[0]
            t_karma_lt = bwb_model.KarmaM.get_all_for_observance(t_observance_id_it)
            for karma_item in t_karma_lt:
                self.karma_lb.insert(tkinter.END, karma_item.description_sg)

        for widget in self.diary_frame.winfo_children():
            widget.destroy()
        t_prev_diary_item = None
        for diary_item in bwb_model.DiaryM.get_all():
            t_diary_entry_obs_sg = bwb_model.ObservanceM.get(diary_item.observance_ref).short_name_sg
            t_karma = bwb_model.KarmaM.get_for_observance_and_pos(
                diary_item.observance_ref, diary_item.karma_ref)

            if t_prev_diary_item == None or not is_same_day(t_prev_diary_item.date_added_it, diary_item.date_added_it):
                t_date_sg = datetime.datetime.fromtimestamp(diary_item.date_added_it).strftime("%A")
                t_new_day_ll = tkinter.Label(
                    self.diary_frame,
                    text=t_date_sg
                )
                t_new_day_ll.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

            if t_karma == None:
                t_diary_entry_karma_sg = ""
            else:
                t_diary_entry_karma_sg = t_karma.description_sg.strip() + " "

            t_cur_observance_sel_te = self.ten_observances_lb.curselection()
            t_observance_pos_it = -1
            if len(t_cur_observance_sel_te) > 0:
                t_observance_pos_it = t_cur_observance_sel_te[0]
            t_diary_entry_font = tkinter.font.Font(size=11)
            # Message widget: http://effbot.org/tkinterbook/message.htm
            t_diary_entry_ll = tkinter.Label(
                self.diary_frame,
                text=t_diary_entry_karma_sg + "[" + t_diary_entry_obs_sg.strip() + "] " + diary_item.notes_sg.strip(),
                justify=tkinter.LEFT, anchor=tkinter.W,
                width=52, wraplength=500,
                padx=15, pady=10,
                borderwidth="1", relief="raised",
                font=t_diary_entry_font
            )

            if t_observance_pos_it == diary_item.observance_ref:
                t_diary_entry_ll.configure(background="yellow")

            # width=300,
            # relief="solid"raised
            # anchor=tkinter.E,
            # state=tkinter.ACTIVE
            t_diary_entry_ll.bind("<Button-1>", self.diary_entry_clicked)
            t_diary_entry_ll.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)
            self.diary_labels_lt.append(t_diary_entry_ll)
            t_prev_diary_item = diary_item

        """

    def diary_entry_clicked(self, i_event):
        print("Diary entry clicked")
        print(i_event.widget)
        i_event.widget.config(relief="sunken")


def pixels_from_monospace_characters(i_nr_of_chars_it):
    # i_font,
    '''
    t_width_it = i_font.measure("0")
    return i_nr_of_chars_it * t_width_it
    '''
    return i_nr_of_chars_it * 8

def is_same_day(i_first_date_it, i_second_date_it):
    t_first = datetime.datetime.fromtimestamp(i_first_date_it)
    t_second = datetime.datetime.fromtimestamp(i_second_date_it)

    return t_first.date() == t_second.date()

if __name__ == "__main__":
    t_win = WellBeingWindow()
    t_win.connect('delete-event', Gtk.main_quit)
    t_win.show_all()
    Gtk.main()

    ##root.resizable(width=False, height=True)

    # Menu
    '''
    menubar = tkinter.Menu(root)
    file_menu = tkinter.Menu(menubar, tearoff=0)
    file_menu.add_command(label="Export", command=bwb_model.export_all)
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=root.quit)
    menubar.add_cascade(label="File", menu=file_menu)
    root.config(menu=menubar)

    root.mainloop()
    '''