
"""
Gtk3 Documentation:
https://developer.gnome.org/gtk3/stable/
http://lazka.github.io/pgi-docs/Gtk-3.0/index.html
https://python-gtk-3-tutorial.readthedocs.io/en/latest/index.html
"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import time
import datetime
#from functools import partial
import bwb_model

TEN_OBS_TEXT_WIDTH = 17 # in number of characters (so pixels can very)
TEN_OBS_TEXT_FONT_SIZE = 14
KARMA_TEXT_WIDTH = 30
KARMA_TEXT_FONT_SIZE = 10

DIARY_DATE_TEXT_WIDTH = 40
ADDING_TO_DIARY_TEXT_WIDTH = 80
DIARY_PIXEL_WIDTH = 300


class WellBeingWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Buddhist Well-Being")

        self.set_default_size(800, 700)

        self.diary_labels_lt = []  # Used in the gui update function
        t_observances_lt = bwb_model.ObservanceM.get_all()

        self.window_hbox = Gtk.Box(spacing = 16, orientation = Gtk.Orientation.HORIZONTAL)
        self.add(self.window_hbox)

        # Creating widgets..
        # ..ten practices
        self.left_vbox = Gtk.Box(orientation = Gtk.Orientation.VERTICAL, spacing = 16)
        self.left_vbox.set_size_request(100, 100)
        self.left_vbox.set_hexpand(False)
        self.window_hbox.pack_start(self.left_vbox, False, False, 0)

        self.ten_observances_lb = Gtk.ListBox()
        self.ten_observances_lb.set_selection_mode(Gtk.SelectionMode.BROWSE)
        self.ten_observances_lb.set_hexpand(False)
        #- https://people.gnome.org/~gcampagna/docs/Gtk-3.0/Gtk.SelectionMode.html
        self.left_vbox.pack_start(self.ten_observances_lb, False, False, 0)
        for observance_item in t_observances_lt:
            row = Gtk.ListBoxRow()
            label = Gtk.Label(observance_item.short_name_sg, xalign=0)
            row.add(label)
            self.ten_observances_lb.add(row)

        self.ten_observances_lb.connect('row-activated', self.observance_selected_fn)

        self.ten_practices_details_ll = Gtk.Label("Nothing selected yet")
        self.ten_practices_details_ll.set_line_wrap(True)
        self.ten_practices_details_ll.set_max_width_chars(10)
        #self.ten_practices_details_ll.set_width_chars(10)
        #self.ten_practices_details_ll.set_size_request(100, 100)
        #self.ten_practices_details_ll.set_hexpand(False)
        self.left_vbox.pack_start(self.ten_practices_details_ll, False, False, 0)

        #..karma
        self.karma_lb = Gtk.ListBox()
        self.karma_lb.set_selection_mode(Gtk.SelectionMode.BROWSE)
        self.karma_lb.set_hexpand(False)
        self.left_vbox.pack_start(self.karma_lb, False, False, 0)

        #..diary
        self.middle_vbox = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
        self.diary_frame = Gtk.Frame()
        self.scrolled_window = Gtk.ScrolledWindow() #hadjustment=None, vadjustment=None
        self.diary_lb = Gtk.ListBox()

        self.scrolled_window.add(self.diary_lb)
        self.diary_frame.add(self.scrolled_window)
        self.middle_vbox.pack_start(self.diary_frame, True, True, 0)
        self.window_hbox.pack_start(self.middle_vbox, False, False, 0)

        self.diary_lb.set_selection_mode(Gtk.SelectionMode.MULTIPLE)
        self.scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.ALWAYS)
        self.diary_frame.set_border_width(10)
        self.diary_lb.set_margin_left(10)

        # ..adding to diary
        self.add_to_diary_text_view = Gtk.TextView()
        self.middle_vbox.pack_end(self.add_to_diary_text_view, False, False, 0)
        self.add_to_diary_text_view.set_size_request(-1, 40)
        #self.add_to_diary_text_view.set_hexpand(False)
        self.add_to_diary_text_view.set_wrap_mode(True)
        #.set_max_width_chars(10)

        self.add_to_diary_button = Gtk.Button("Add new")
        self.add_to_diary_button.connect('clicked', self.add_text_to_diary_button_pressed_fn)
        self.middle_vbox.pack_end(self.add_to_diary_button, False, False, 0)

        #experimental
        self.right_vbox = Gtk.Box(orientation = Gtk.Orientation.VERTICAL, spacing = 16)
        self.window_hbox.pack_start(self.right_vbox, False, False, 0)
        self.diary_entry_cal = Gtk.Calendar()
        self.diary_entry_cal.show()
        #self.diary_entry_cal.mark_day(7)
        self.right_vbox.pack_end(self.diary_entry_cal, False, False, 0)

        self.slider_label = Gtk.Label("Loving Kindness")
        self.right_vbox.pack_start(self.slider_label, False, False, 0)
        self.slider = Gtk.HScale()
        self.slider.set_range(0,100)
        self.right_vbox.pack_start(self.slider, False, False, 0)
        self.right_vbox.set_margin_right(20)


        self.context_menu = Gtk.Menu()
        self.context_menu_item = Gtk.MenuItem("Delete")
        self.context_menu_item.connect('button-press-event', self.on_delete_menu_item_pressed)
        self.context_menu.append(self.context_menu_item)
        self.context_menu.show_all()


        self.update_gui()

    def on_diary_frame_configure(self, i_event):
        self.diary_canvas.configure(scrollregion=self.diary_canvas.bbox("all"))

    def observance_selected_fn(self, i_listbox, i_row):
        #- http://lazka.github.io/pgi-docs/#Gtk-3.0/classes/ListBox.html#Gtk.ListBox.signals.row_activated
        t_selection_it = i_row.get_index() ###i_event.widget.curselection()[0]
        t_observance = bwb_model.ObservanceM.get(t_selection_it)
        self.ten_practices_details_ll.set_text(t_observance.sutra_text_sg)

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

    def add_text_to_diary_button_pressed_fn(self, i_widget):
        t_observance_pos_it = self.ten_observances_lb.get_selected_row().get_index()

        t_karma_pos_it = -1
        if self.karma_lb.get_selected_row() is not None:
            t_karma_pos_it = self.karma_lb.get_selected_row().get_index()

        start = self.add_to_diary_text_view.get_buffer().get_start_iter()
        end = self.add_to_diary_text_view.get_buffer().get_end_iter()
        notes_pre_sg = self.add_to_diary_text_view.get_buffer().get_text(start, end, True) #.strip()

        bwb_model.DiaryM.add(int(time.time()), t_observance_pos_it, t_karma_pos_it, notes_pre_sg)

        self.add_to_diary_text_view.set_buffer(Gtk.TextBuffer()) #-clearing

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
                label.set_max_width_chars(10)
                #label.set_width_chars(10)
                label.set_line_wrap(True)
                print("karma_item.description_sg = " + karma_item.description_sg)
                row.add(label)
                self.karma_lb.add(row)
        self.karma_lb.show_all()


        self.diary_lb.foreach(lambda x: self.diary_lb.remove(x))
        list_of_rows = []
        t_prev_diary_item = None
        for diary_item in bwb_model.DiaryM.get_all():
            t_diary_entry_obs_sg = bwb_model.ObservanceM.get(diary_item.observance_ref).short_name_sg
            t_karma = bwb_model.KarmaM.get_for_observance_and_pos(
                diary_item.observance_ref, diary_item.karma_ref)

            if t_prev_diary_item == None or not is_same_day(t_prev_diary_item.date_added_it, diary_item.date_added_it):
                t_date_sg = datetime.datetime.fromtimestamp(diary_item.date_added_it).strftime("%A")
                t_new_day_ll = Gtk.Label(t_date_sg)
                self.diary_lb.add(t_new_day_ll)

            if t_karma == None:
                t_diary_entry_karma_sg = ""
            else:
                t_diary_entry_karma_sg = t_karma.description_sg.strip() + " "

            t_label_text_sg = t_diary_entry_karma_sg + "[" + t_diary_entry_obs_sg.strip() + "] " + diary_item.notes_sg.strip()
            t_diary_entry_ll = Gtk.Label(t_label_text_sg)
            #t_diary_entry_ll.set_justify(Gtk.Justification.LEFT)
            #t_diary_entry_ll.set_alignment()
            t_diary_entry_ll.set_xalign(0)
            t_diary_entry_ll.set_line_wrap(True)

            """
            if t_observance_pos_it == diary_item.observance_ref:
                t_diary_entry_ll.configure(background="yellow")
            """

            event_box = Gtk.EventBox()
            #- Please note that the eventbox is not itself connected to the event, instead it wraps the widget that
            #  is connected to the event
            event_box.add(t_diary_entry_ll)

            row = Gtk.ListBoxRow()
            row.set_name(str(diary_item.date_added_it))
            print("row.get_name = " + row.get_name())
            row.connect('button-press-event', self.diary_entry_clicked)
            row.add(event_box)
            self.diary_lb.add(row)

            t_prev_diary_item = diary_item

        self.diary_lb.show_all()

    def on_delete_menu_item_pressed(self, i_widget, i_event):
        bwb_model.DiaryM.remove(self.last_row_clicked_it)
        self.update_gui()

    #http://lazka.github.io/pgi-docs/#Gdk-3.0/str
    def diary_entry_clicked(self, i_widget, i_event):
        print("Diary entry clicked")
        if i_event.button == 1:
            print("Left click")
        elif i_event.button == 3:
            print("Right click")
        else:
            print("Click with other button")

        self.last_row_clicked_it = int(i_widget.get_name())
        #print(i_event.widget)
        #i_event.widget.config(relief="sunken")


        print("i_widget.get_name() = " + i_widget.get_name())


        print("i_event.get_root_coords()[0] = " + str(i_event.get_root_coords()[0]))
        print("i_event.get_root_coords()[1] = " + str(i_event.get_root_coords()[1]))

        self.context_menu.popup(
            None,
            None,
            self.menu_positioning_function,
            None,
            i_event.button,
            i_event.time
        )
        ######lambda menu, x, y, data: (i_event.get_root_coords()[0], i_event.get_root_coords()[1], True)
        return True

    def menu_positioning_function(self, menu, x, y, data):
        return (x, y, True)

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

class NonExpandingLabel(Gtk.Label):
    def __init__(self, i_title):
        Gtk.Label.__init__(self, i_title)
    #overriding
    def compute_expand(self, i_orientation):
        return False

if __name__ == "__main__":
    t_win = WellBeingWindow()
    t_win.set_icon_from_file("icon.png")
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
