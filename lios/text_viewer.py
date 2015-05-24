# coding: latin-1

###########################################################################
#    Lios - Linux-Intelligent-Ocr-Solution
#    Copyright (C) 2011-2015 Nalin.x.Linux GPL-3
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
###########################################################################
import os
import enchant

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import Pango
from gi.repository import PangoCairo

from espeak import espeak


from lios import global_var
from lios import text_to_audio_gtk_ui




class BasicTextView(Gtk.TextView):
	def __init__(self):
		Gtk.TextView.__init__(self)
		self.textbuffer = self.get_buffer()

	def go_to_line(self,wedget,data=None):
		insert_mark = self.textbuffer.get_insert()
		offset = self.textbuffer.get_iter_at_mark(insert_mark)
		current_line = offset.get_line()
		maximum_line = self.textbuffer.get_line_count()
		adj = Gtk.Adjustment(value=1, lower=1, upper=maximum_line, step_incr=1, page_incr=5, page_size=0) 
		spinbutton_line = Gtk.SpinButton()
		spinbutton_line.set_adjustment(adj)
		spinbutton_line.set_value(current_line)		
		spinbutton_line.show()

		dialog =  Gtk.Dialog("Go to Line ",None,True,("Go", Gtk.ResponseType.ACCEPT,"Close!", Gtk.ResponseType.REJECT))
		spinbutton_line.connect("activate",lambda x : dialog.response(Gtk.ResponseType.ACCEPT))
		box = dialog.get_content_area();
		box.add(spinbutton_line)
		spinbutton_line.grab_focus()
		dialog.show_all()
		response = dialog.run()
		if response == Gtk.ResponseType.ACCEPT:
			to = spinbutton_line.get_value_as_int()
			iter = self.textbuffer.get_iter_at_line(to)
			self.textbuffer.place_cursor(iter)
			self.scroll_to_iter(iter, 0.0,False,0.0,0.0)
			dialog.destroy()
		else:
			dialog.destroy()
			
				

	
	def new(self,wedget,data=None):
		if (self.textbuffer.get_modified() == True):
			dialog =  Gtk.Dialog("Start new without saving ?",None,True,
			("Save", Gtk.ResponseType.ACCEPT,"Start-New!", Gtk.ResponseType.REJECT))                           						

			label = Gtk.Label("Start new without saving ?")
			box = dialog.get_content_area();
			box.add(label)
			dialog.show_all()

			response = dialog.run()
			dialog.destroy()				
			if response == Gtk.ResponseType.ACCEPT:
				self.save(self)
		start, end = self.textbuffer.get_bounds()
		self.textbuffer.delete(start, end)
		self.grab_focus();

	def open(self,wedget,data=None):
		open_file = Gtk.FileChooserDialog("Select the file to open",None,Gtk.FileChooserAction.OPEN,buttons=(Gtk.STOCK_OPEN,Gtk.ResponseType.OK))
		open_file.set_current_folder(global_var.home_dir)
		filter = Gtk.FileFilter()
		filter.add_pattern("*.txt")
		filter.add_pattern("*.text")
		open_file.add_filter(filter)
		response = open_file.run()
		if response == Gtk.ResponseType.OK:
			to_read = open("%s" % (open_file.get_filename()))
			to_open = to_read.read()
			try:
				self.textbuffer.set_text(to_open)
			except FileNotFoundError:
					pass
			else:
				self.save_file_name = open_file.get_filename()
				self.textbuffer.place_cursor(self.textbuffer.get_end_iter())
		open_file.destroy()


	def save(self,wedget,data=None):
		start,end = self.textbuffer.get_bounds()
		text = self.textbuffer.get_text(start,end,False)
		try:
			self.save_file_name
		except AttributeError:
			save_file = Gtk.FileChooserDialog("Save ",None,Gtk.FileChooserAction.SAVE,
		                    buttons=(Gtk.STOCK_SAVE,Gtk.ResponseType.OK))    
			save_file.set_current_folder(global_var.home_dir)
			save_file.set_current_name(text[0:10]);
			save_file.set_do_overwrite_confirmation(True);
			filter = Gtk.FileFilter()
			filter.add_pattern("*.txt")
			filter.add_pattern("*.text")
			save_file.add_filter(filter)
			response = save_file.run()
			if response == Gtk.ResponseType.OK:
				self.save_file_name = "%s"%(save_file.get_filename())
				open("%s" %(self.save_file_name),'w').write(text)
				self.textbuffer.set_modified(False)	
				save_file.destroy()
				return True
			else:
				save_file.destroy()
				return False
		else:
			open("%s" %(self.save_file_name),'w').write(text)
			self.textbuffer.set_modified(False)
			return True		

	def save_as(self,wedget,data=None):
		del self.save_file_name
		self.save(self);
	def append(self,wedget,data=None):
		append_file_dialog = Gtk.FileChooserDialog("Select the file to append",None,Gtk.FileChooserAction.OPEN,buttons=(Gtk.STOCK_OPEN,Gtk.ResponseType.OK))
		append_file_dialog.set_current_folder(global_var.home_dir)
		append_file_dialog.run()
		with open(append_file_dialog.get_filename()) as file:
			text_to_append = file.read()
			end = self.textbuffer.get_end_iter()
			self.textbuffer.insert(end,text_to_append)
		append_file_dialog.destroy()
	
	def punch(self,wedget,data=None):
		insert_at_cursor_dialog = Gtk.FileChooserDialog("Select the file to insert at cursor",None,Gtk.FileChooserAction.OPEN,buttons=(Gtk.STOCK_OPEN,Gtk.ResponseType.OK))
		insert_at_cursor_dialog.set_current_folder(global_var.home_dir)
		insert_at_cursor_dialog.run()
		with open(insert_at_cursor_dialog.get_filename()) as file:
			text_to_insert_at_cursor = file.read()
			self.textbuffer.insert_at_cursor(text_to_insert_at_cursor)
		insert_at_cursor_dialog.destroy()

	def quit(self,wedget,data=None):
		if self.textbuffer.get_modified() == True:
			dialog =  Gtk.Dialog(None,None,1,
			("Close without saving",Gtk.ResponseType.YES,"Save", Gtk.ResponseType.NO,"Cancel", Gtk.ResponseType.CANCEL))			
			label = Gtk.Label("Close without saving ?.")
			box = dialog.get_content_area();
			box.add(label)
			dialog.show_all()
			
			response = dialog.run()
			dialog.destroy()
			if response == Gtk.ResponseType.YES:
				Gtk.main_quit()			
			elif response == Gtk.ResponseType.NO:
				if (self.save(self)):
					Gtk.main_quit()
			else:
				return True
		else:
			Gtk.main_quit()


	def copy(self,wedget,data=None):
		self.clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
		self.textbuffer.copy_clipboard(self.clipboard)
	def cut(self,wedget,data=None):
		self.clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
		self.textbuffer.cut_clipboard(self.clipboard, True)
	def paste(self,wedget,data=None):
		self.clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
		self.textbuffer.paste_clipboard(self.clipboard, None, True)


	def print_with_action(self, action=None,filename = None):
		if (self.textbuffer.get_has_selection()):
			start,end = self.textbuffer.get_selection_bounds()
		else:
			start,end = self.textbuffer.get_bounds()
		self.print_text = self.textbuffer.get_text(start,end,False)		
		self.layout = None
		self.page_breaks = None
		self.font_size=12
		if action==None:
			action = Gtk.PrintOperationAction.PREVIEW
		
		#paper_size = Gtk.PaperSize(Gtk.PAPER_NAME_A4)
		#paper_size = Gtk.PaperSize.get_default()
		#paper_size = Gtk.PaperSize(paper_size)
		
		setup = Gtk.PageSetup()
		#setup.set_paper_size(paper_size)
		
		# PrintOperation
		print_ = Gtk.PrintOperation()
		print_.set_default_page_setup(setup)
		print_.set_unit(Gtk.Unit.MM)
		
		print_.connect("begin_print", self.begin_print)
		print_.connect("draw_page", self.draw_page)
		
		if action == Gtk.PrintOperationAction.EXPORT:
			print_.set_export_filename(filename)
		res = print_.run(action,None)
    
	def begin_print(self, operation, context):
		width = context.get_width()
		height = context.get_height()
		print (height)
		self.layout = context.create_pango_layout()
		self.layout.set_font_description(Pango.FontDescription("Sans " + str(self.font_size)))
		self.layout.set_width(int(width*Pango.SCALE))

		self.layout.set_text(self.print_text,len(self.print_text))

		num_lines = self.layout.get_line_count()
		print ("num_lines: ", num_lines)
		
		page_breaks = []
		page_height = 0
		
		for line in range(num_lines):
			layout_line = self.layout.get_line(line)
			ink_rect, logical_rect = layout_line.get_extents()
			
			x_bearing, y_bearing, lwidth, lheight = logical_rect.x,logical_rect.y,logical_rect.width,logical_rect.height;
			
			line_height = lheight / 1024.0 # 1024.0 is float(pango.SCALE)
			page_height += line_height
			
			print ("page_height ", page_height)
			if page_height + line_height > height:
				page_breaks.append(line)
				page_height = 0
				page_height += line_height
		operation.set_n_pages(len(page_breaks) + 1)
		self.page_breaks = page_breaks
    
	def draw_page (self, operation, context, page_number):
		assert isinstance(self.page_breaks, list)
		#print page_number
		if page_number == 0:
			start = 0
		else:
			start = self.page_breaks[page_number - 1]
		try:
			end = self.page_breaks[page_number]
		except IndexError:
			end = self.layout.get_line_count()
		
		cr = context.get_cairo_context()
		cr.set_source_rgb(0, 0, 0)
		i = 0
		start_pos = 0
		iter = self.layout.get_iter()
		while 1:
			if i >= start:
				line = iter.get_line()
				_, logical_rect = iter.get_line_extents()
				x_bearing, y_bearing, lwidth, lheight = logical_rect.x,logical_rect.y,logical_rect.width,logical_rect.height;
				baseline = iter.get_baseline()
				if i == start:
					start_pos = y_bearing / 1024.0 # 1024.0 is float(pango.SCALE)
				cr.move_to(x_bearing / 1024.0, baseline / 1024.0 - start_pos)
				PangoCairo.show_layout_line(cr, line)
			i += 1
			if not (i < end and iter.next_line()):
				break


	def print_preview(self,widget):
		action = Gtk.PrintOperationAction.PREVIEW
		printer = self.print_with_action(action)
			
	def print_text(self,widget):
		action = Gtk.PrintOperationAction.PRINT_DIALOG
		printer = self.print_with_action(action)

	def print_to_pdf(self,widget):
		dialog = Gtk.FileChooserDialog("Save Text as Pdf",None,Gtk.FileChooserAction.SAVE,buttons=(Gtk.STOCK_SAVE,Gtk.ResponseType.OK))    
		dialog.set_current_folder(global_var.home_dir)
		dialog.set_do_overwrite_confirmation(True);
		filter = Gtk.FileFilter()
		filter.add_pattern("*.pdf")
		dialog.add_filter(filter)
		response = dialog.run()
		if response == Gtk.ResponseType.OK:
			save_file_name = "%s"%(dialog.get_filename())
			action = Gtk.PrintOperationAction.EXPORT
			printer = self.print_with_action(action,save_file_name)
			dialog.destroy()
			

	def find(self,widget):
		find(self,self.textbuffer).window.show()
	def find_and_replace(self,widget):
		find_and_replace(self,self.textbuffer).window.show()
	def delete(self,wedget,data=None):
		self.textbuffer.delete_selection(True, True)		


class TextViewer(Gtk.HPaned):
	def __init__(self):
		Gtk.HPaned.__init__(self)
		self.set_border_width(5)
		
		self.page_numbering_type = 0
		self.language = "en"
		box = Gtk.VBox()
		
		#Text Area		
		self.textview = BasicTextView()
		self.textview.connect("button-press-event",self.textview_button_press_event)
		self.highlight_tag = self.textview.textbuffer.create_tag('Reading')
		self.textview.set_wrap_mode(Gtk.WrapMode.WORD)

		
		scrolled = Gtk.ScrolledWindow()
		scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
		scrolled.add(self.textview);
		box.pack_end(scrolled,True,True,0);
		

		#TextView Popup Menu
		self.textview_popup_menu = Gtk.Menu()

		item = Gtk.MenuItem.new_with_label("Cut")
		item.connect("activate",self.textview.cut)
		self.textview_popup_menu.append(item)

		item = Gtk.MenuItem.new_with_label("Copy")
		item.connect("activate",self.textview.copy)
		self.textview_popup_menu.append(item)

		item = Gtk.MenuItem.new_with_label("Paste")
		item.connect("activate",self.textview.paste)
		self.textview_popup_menu.append(item)
		
		self.textview_popup_menu_no_selection = Gtk.Menu()
		item = Gtk.MenuItem.new_with_label("Paste")
		item.connect("activate",self.textview.paste)
		self.textview_popup_menu_no_selection.append(item)

		
		#Toolbar
		toolbar = Gtk.Toolbar()
		
		button = Gtk.ToolButton(Gtk.STOCK_NEW)
		button.connect("clicked",self.textview.new)
		toolbar.add(button)

		button = Gtk.ToolButton(Gtk.STOCK_SAVE)
		button.connect("clicked",self.textview.save)
		toolbar.add(button)		

		button = Gtk.ToolButton(Gtk.STOCK_OPEN)
		button.connect("clicked",self.textview.open)
		toolbar.add(button)

		button = Gtk.ToolButton(Gtk.STOCK_SPELL_CHECK)
		button.connect("clicked",self.spell_checker)
		toolbar.add(button)				

		button = Gtk.ToolButton(Gtk.STOCK_FIND)
		button.connect("clicked",self.textview.find)
		toolbar.add(button)		

		self.button_read_stop = Gtk.ToolButton(Gtk.STOCK_MEDIA_PLAY)
		self.button_read_stop.connect("clicked",self.read_stop)
		toolbar.add(self.button_read_stop)

		
		box.pack_end(toolbar, False, False, 0)
		self.add(box)
		
		self.show_all()

	def textview_button_press_event(self, treeview, event):
		if event.button == 3:
			x = int(event.x)
			y = int(event.y)
			time = event.time
			if self.textview.textbuffer.get_has_selection():
				self.textview_popup_menu.popup(None, None, None, None,event.button,time)
				self.textview_popup_menu.show_all()
			else:
				self.textview_popup_menu_no_selection.popup(None, None,
				None, None,event.button,time)
				
				self.textview_popup_menu_no_selection.show_all()
			return True
			
	def set_page_numbering_type(self,value):
		self.page_numbering_type = value
	
	def set_max_page_number(self,value):
		self.starting_page_number = value
	
	def set_text(self,text):
		self.textview.textbuffer.set_text(text)
		start = self.textview.textbuffer.get_start_iter()
		self.textview.textbuffer.place_cursor(start)

	def go_to_page(self,wedget,data=None):
		iter,end = self.textview.textbuffer.get_bounds()
		adj = Gtk.Adjustment(value=1, lower=1, upper=self.starting_page_number-1,
		step_incr=1, page_incr=5, page_size=0) 
		
		spinbutton_line = Gtk.SpinButton()
		spinbutton_line.set_adjustment(adj)
		spinbutton_line.set_value(0)		
		spinbutton_line.show()

		dialog =  Gtk.Dialog("Go to Page ",None,True,
		("Go", Gtk.ResponseType.ACCEPT,"Close!", Gtk.ResponseType.REJECT))
		
		spinbutton_line.connect("activate",lambda x : dialog.response(Gtk.ResponseType.ACCEPT))
		box = dialog.get_content_area();
		box.add(spinbutton_line)
		spinbutton_line.grab_focus()
		dialog.show_all()
		response = dialog.run()
		if response == Gtk.ResponseType.ACCEPT:
			to_go = spinbutton_line.get_value_as_int()
			if self.page_numbering_type == 0:
				word = "Page-{0}".format(to_go)
			else:
				if to_go % 2 == 0:
					word = "Page-{0}-{1}".format(to_go-1,to_go)
				else:
					word = "Page-{0}-{1}".format(to_go,to_go+1)	
			
			results = iter.forward_search(word, 0, end)
			if results:
				start,end = results
				self.textview.textbuffer.place_cursor(start)
				self.textview.scroll_to_iter(start, 0.0,False,0.0,0.0)
			dialog.destroy()
		else:
			dialog.destroy()

	def audio_converter(self,widget):
		try:
			start,end = self.textview.textbuffer.get_selection_bounds()
		except ValueError:
			start,end = self.textview.textbuffer.get_bounds()
		text = self.textview.textbuffer.get_text(start,end,False)		
		text_to_audio_gtk_ui.record_ui(text)
	
	def set_language(self,language):
		self.language = language

	def spell_checker(self,widget):
		spell_check(self.textview,self.language)
	
	def set_tags(self,highlight_color,highlight_font_color,background_highlight_color):
		self.highlight_tag.set_property('foreground',Gdk.color_parse(highlight_color).to_string())
		self.highlight_tag.set_property('font',highlight_font_color)
		self.highlight_tag.set_property('background',Gdk.color_parse(background_highlight_color).to_string())
	
	def set_font_and_color(self,font,font_color,background_color):
		pangoFont = Pango.FontDescription(font)
		self.textview.modify_font(pangoFont)
		self.textview.modify_fg(Gtk.StateFlags.NORMAL, Gdk.color_parse(font_color))
		self.textview.modify_bg(Gtk.StateFlags.NORMAL, Gdk.color_parse(background_color))
	
	def grab_focus(self):
		self.textview.grab_focus()
	
	def insert_text(self,text,insert_position=0,place_cursor=False):
		if (insert_position == 0):
			iter = self.textview.textbuffer.get_start_iter()
		elif (insert_position == 1):
			mark = self.textview.textbuffer.get_insert()
			iter = self.textview.textbuffer.get_iter_at_mark(mark)
		else:
			iter = self.textview.textbuffer.get_end_iter()
		
		start = self.textview.textbuffer.get_start_iter()
		length = len(self.textview.textbuffer.get_text(start,iter,False))
			
		self.textview.textbuffer.insert(iter,text)
		if(place_cursor):
			iter = self.textview.textbuffer.get_iter_at_offset(length)
			self.textview.textbuffer.place_cursor(iter)
	
	def get_text(self):
		start,end = self.textview.textbuffer.get_bounds()
		text = self.textview.textbuffer.get_text(start,end,False)
		return text


    # Read the text
	def read_stop(self,wedget,data=None):
		print("Pressed")
		if espeak.is_playing() == False:
			self.textview.textbuffer.remove_tag(self.highlight_tag, self.textview.textbuffer.get_start_iter(),
			self.textview.textbuffer.get_end_iter())
			
			mark = self.textview.textbuffer.get_insert()
			start = self.textview.textbuffer.get_iter_at_mark(mark)
			end = self.textview.textbuffer.get_end_iter()
			self.to_count = start.get_offset()
			text = self.textview.textbuffer.get_text(start,end,False)
			espeak.set_SynthCallback(self.espeak_event)
			espeak.synth(text)
			self.textview.set_editable(False)
		else:
			#self.button_read_stop.new_from_stock(Gtk.STOCK_MEDIA_PLAY)
			espeak.cancel()
			espeak.set_SynthCallback(None)
			self.textview.textbuffer.remove_tag(self.highlight_tag, self.textview.textbuffer.get_start_iter(),
			self.textview.textbuffer.get_end_iter())
			
			self.textview.set_editable(True)
			
		
	def espeak_event(self, event, pos, length):
		Gdk.threads_enter()
		if event == espeak.core.event_WORD:
			pos += self.to_count-1
			s = self.textview.textbuffer.get_iter_at_offset(pos)
			e = self.textview.textbuffer.get_iter_at_offset(length+pos)			
			
			self.textview.textbuffer.remove_all_tags(self.textview.textbuffer.get_start_iter(),
			self.textview.textbuffer.get_end_iter())
			
			self.textview.textbuffer.apply_tag(self.highlight_tag, s, e)

		if event == espeak.event_END:
			point = self.textview.textbuffer.get_iter_at_offset(pos+self.to_count)
			self.textview.textbuffer.place_cursor(point)
			self.textview.scroll_to_iter(point, 0.0, use_align=True, xalign=0.0, yalign=0.2)
							
					
		if event == espeak.event_MSG_TERMINATED:
			espeak._playing = False
			self.textview.set_editable(True)
			try:
				self.textview.textbuffer.remove_all_tags(self.textview.textbuffer.get_start_iter(),
				self.textview.textbuffer.get_end_iter())
			except:
				pass

		if not espeak.is_playing():
			mark = self.textview.textbuffer.get_insert()
			start = self.textview.textbuffer.get_iter_at_mark(mark)
			end = self.textview.textbuffer.get_end_iter()
			self.to_count = start.get_offset()
			text = self.textview.textbuffer.get_text(start,end,False)
			if (text != ""):
				espeak.synth(text)

		Gdk.threads_leave()		
		return True

		
class find():
	def __init__ (self,textview,textbuffer,glade_file="find"):
		self.textbuffer = textbuffer;
		self.textview = textview;
				
		mark = self.textbuffer.get_insert()
		self.iter = self.textbuffer.get_iter_at_mark(mark)
		self.match_start = self.iter.copy()
		self.match_start.backward_word_start()
		self.match_end = self.iter.copy()
		self.match_end.forward_word_end()
		
		
		self.tag = self.textbuffer.create_tag(foreground = "Blue")


		#Builder And Gui
		self.builder = Gtk.Builder()
		self.builder.add_from_file("{0}/ui/{1}.glade".format(global_var.data_dir,glade_file))
		self.window = self.builder.get_object("window")
		self.builder.connect_signals(self)
		self.entry = self.builder.get_object("entry_word")
		self.context_label = self.builder.get_object("context_label")
		
				

	def close(self,widget,data=None):
		start,end = self.textbuffer.get_bounds()
		self.textbuffer.remove_all_tags(start,end)
		self.window.destroy()	

	def correct_context(self,text):
		"""cut the line if it is too lengthy (more than 10 words)
		without rearranging existing lines. This will avoid the resizing of spell window"""
		new_text = ""
		for line in text.split('\n'):
			if (len(line.split(' ')) > 10):
				new_line = ""
				pos = 1
				for word in line.split(" "):
					new_line += word
					pos += 1
					if (pos % 10 == 0):
						new_line += '\n'
					else:
						new_line += ' '

				new_text += new_line
				if (pos % 10 > 3):
					new_text += '\n'
			else:
				new_text += line + '\n'
		return new_text
	
	def find_next(self,widget,data=None):
		self.find(True)

	def find_previous(self,widget,data=None):
		self.find(False)		
		
	def find(self,data):
		word = self.entry.get_text()
		start , end = self.textbuffer.get_bounds()
		if (data == True):
			self.match_start.forward_word_end()
			results = self.match_start.forward_search(word, 0, end)
		else:
			self.match_end.backward_word_start()
			results = self.match_end.backward_search(word, 0,start)
		
		if results:
			self.textbuffer.remove_all_tags(start,end)
			self.match_start, self.match_end = results
			self.textbuffer.place_cursor(self.match_start)
			self.textbuffer.apply_tag(self.tag,self.match_start, self.match_end)
			self.textview.scroll_to_iter(self.match_start, 0.2, use_align=False, xalign=0.5, yalign=0.5)
			sentence_start=self.match_start.copy()
			sentence_start.backward_sentence_start()
			sentence_end=self.match_start.copy()
			sentence_end.forward_sentence_end()
			sentence = self.textbuffer.get_text(sentence_start,sentence_end,True)
			self.context_label.set_text(self.correct_context(sentence))
		else:
			self.context_label.set_text("Word {0} Not found".format(word))
			

class find_and_replace(find):
	def __init__(self,textview,textbuffer,glade_file="find_and_replace"):
		find.__init__(self,textview,textbuffer,glade_file="find_and_replace")
		self.replace_entry = self.builder.get_object("entry_replace_word")
		
	def replace(self,widget,data=None):
		replace_word = self.replace_entry.get_text()
		self.textbuffer.delete(self.match_start, self.match_end)
		self.textbuffer.insert(self.match_end,replace_word)
		self.match_start = self.match_end.copy()
		self.find(True)
	
	def replace_all(self,widget,data=None):
		word = self.entry.get_text()
		replace_word = self.replace_entry.get_text()
		end = self.textbuffer.get_end_iter()
		while(True):
			self.match_start.forward_word_end()
			results = self.match_start.forward_search(word, 0, end)
			if results:
				self.match_start, self.match_end = results
				self.textbuffer.delete(self.match_start, self.match_end)
				self.textbuffer.insert(self.match_end,replace_word)
				self.match_start = self.match_end.copy()
			else:
				break

# CHECK SPELLING
class spell_check:
	def __init__ (self,textview,enchant_language):
		self.textview = textview;
		self.textbuffer = self.textview.get_buffer()
		
		#Loading Dict
		try:
			self.dict = enchant.Dict(enchant_language)
		except:
			dialog = Gtk.MessageDialog(None, 0, Gtk.MessageType.ERROR,Gtk.ButtonsType.CANCEL, "Dict not found!")
			dialog.format_secondary_text("Please install the aspell dict for your language({0})".format(enchant_language))
			dialog.run()
			dialog.destroy()
			return
			
		
		#Builder And Gui
		builder = Gtk.Builder()
		builder.add_from_file("%s/ui/spell.glade" % (global_var.data_dir))
		self.spell_window = builder.get_object("window")
		builder.connect_signals(self)
		self.entry = builder.get_object("entry")
		self.context_label = builder.get_object("label_context")
		

		self.liststore = Gtk.ListStore(str)
		self.treeview = builder.get_object("treeview")
		self.treeview.connect("row-activated",self.activate_treeview)
		
		self.treeview.set_model(self.liststore)
		column = Gtk.TreeViewColumn("Suggestions : ")
		self.treeview.append_column(column)		
		cell = Gtk.CellRendererText()
		column.pack_start(cell, False)
		column.add_attribute(cell, "text", 0)
				
		#user dict for change all
		self.user_dict={}
		
		#Tag for misspelled
		size = self.textview.get_style().font_desc.get_size()/Pango.SCALE
		desc = self.textview.get_style().font_desc
		desc.set_size((size+size/2)*Pango.SCALE)
		self.tag = self.textbuffer.create_tag(font = desc)
		
		#get the current cursor position 
		mark = self.textbuffer.get_insert()
		pos = self.textbuffer.get_iter_at_mark(mark)
		
		#move the pos to end of the near word
		pos.backward_word_start()
		pos.forward_word_end()
		
		#get the position of last word end
		last_word_end = self.textbuffer.get_end_iter();
		last_word_end.backward_word_start()
		last_word_end.forward_word_end()
		 
		if (pos.equal(last_word_end)):
			#start the spell-check from begining if pos and last-word-end are same
			self.word_start = self.textbuffer.get_start_iter();
		else:
			self.word_start = pos.copy();
			self.word_start.backward_word_start()
						
		
		if (self.find_next_miss_spelled()):
			self.spell_window.show()


	def activate_treeview(self,widget, row, col):
		model = widget.get_model()
		text = model[row][0]
		self.entry.set_text(text)
		self.entry.grab_focus()
		left = self.textbuffer.get_text(self.sentence_start,self.word_start,False)
		right = self.textbuffer.get_text(self.word_end,self.sentence_end,False) 	
		self.context_label.set_label(self.correct_context(left+text+right))		
	
	def close(self,widget,data=None):
		start,end = self.textbuffer.get_bounds()
		self.textbuffer.remove_all_tags(start,end)
		self.spell_window.destroy()	
	
	def change(self,data=None):
		self.textbuffer.delete(self.word_start, self.word_end)
		self.textbuffer.insert(self.word_start, self.entry.get_text())
		self.find_next_miss_spelled()
		
		
	def change_all(self,data=None):
		self.textbuffer.delete(self.word_start, self.word_end)
		self.textbuffer.insert(self.word_start, self.entry.get_text())
		self.user_dict[self.word] = self.entry.get_text()		
		self.find_next_miss_spelled()

	def ignore(self,data=None):
		self.word_start.forward_word_ends(2)
		self.word_start.backward_word_starts(1)
		self.find_next_miss_spelled()	

	def ignore_all(self,data=None):
		if self.dict.is_added(self.word) == False:
			self.dict.add(self.word)	
		self.find_next_miss_spelled()
	
	def delete(self,data=None):
		self.textbuffer.delete(self.word_start, self.word_end)
		self.find_next_miss_spelled()	

	def find_next_miss_spelled(self):
		if (self.move_iters_to_next_misspelled()):
			start,end = self.textbuffer.get_bounds()
			self.textbuffer.remove_all_tags(start,end)
			self.textbuffer.apply_tag(self.tag,self.word_start,self.word_end)
			self.textview.scroll_to_iter(self.word_start, 0.2, use_align=False, xalign=0.5, yalign=0.5)
			
			self.entry.set_text("")
			self.word = self.textbuffer.get_text(self.word_start,self.word_end,False)		
			self.sentence_start=self.word_start.copy()
			self.sentence_start.backward_sentence_start()
			self.sentence_end=self.word_start.copy()
			self.sentence_end.forward_sentence_end()
			
			sentence = self.textbuffer.get_text(self.sentence_start,self.sentence_end,True)
			context = "Misspelled word {0} : -  {1}".format(self.word,sentence)
			self.context_label.set_text(self.correct_context(context))
			self.entry.set_text(self.word)
			
			self.liststore.clear()
			for item in self.dict.suggest(self.word):
				self.liststore.append([item])
			self.entry.grab_focus()
			return True
		else:
			self.spell_window.destroy()
			start,end = self.textbuffer.get_bounds()
			self.textbuffer.remove_all_tags(start,end)
			return False	
	

	def move_iters_to_next_misspelled(self):
		#loop till a misspelled word found
		while(True):
			self.word_end = self.word_start.copy()
			self.word_end.forward_word_end()
				
			self.word = self.textbuffer.get_text(self.word_start,self.word_end,False)			
			
			#check only non empty word
			if (len(self.word) > 1):
				if (self.dict.check(self.word) == False):
					if (self.word in self.user_dict.keys()):
						self.textbuffer.delete(self.word_start, self.word_end)
						self.textbuffer.insert(self.word_start,self.user_dict[self.word])
					else:
						return True
				
			#check for the end reached
			last_word_end = self.textbuffer.get_end_iter();
			last_word_end.backward_word_start()
			last_word_end.forward_word_end()	
			if (self.word_end.equal(last_word_end)):
				return False
			
			#move to next word
			self.word_start.forward_word_ends(2)
			self.word_start.backward_word_starts(1)
	
	
	def correct_context(self,text):
		"""cut the line if it is too lengthy (more than 10 words)
		without rearranging existing lines. This will avoid the resizing of spell window"""
		new_text = ""
		for line in text.split('\n'):
			if (len(line.split(' ')) > 10):
				new_line = ""
				pos = 1
				for word in line.split(" "):
					new_line += word
					pos += 1
					if (pos % 10 == 0):
						new_line += '\n'
					else:
						new_line += ' '

				new_text += new_line
				if (pos % 10 > 3):
					new_text += '\n'
			else:
				new_text += line + '\n'
		return new_text
		
################ Test Module #############################################
class TestWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="Hello World")
        self.set_default_size(400,500)
        
        self.btv = TextViewer()

        self.box = Gtk.VBox(spacing=6)
        self.add(self.box)
        self.box.pack_start(self.btv, True, True, 0)

        self.button2 = Gtk.Button(label="Exit")
        self.button2.connect("clicked", self.on_button2_clicked)        
        self.box.pack_start(self.button2, False, False, 0)

        self.add(self.box)

    def on_button2_clicked(self, widget):
        Gtk.main_quit()


if __name__ == "__main__":
	win = TestWindow()
	win.connect("delete-event", Gtk.main_quit)
	win.show_all()
	Gtk.main()