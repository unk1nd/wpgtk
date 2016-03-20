#!/usr/bin/env python3
from gi import require_version
require_version( "Gtk", "3.0" )
from os import walk
from subprocess import call
import os.path #fetch filenames
#making sure it uses v3.0
from gi.repository import Gtk, GdkPixbuf, GLib
from colorparser import execute_gcolorchange
from time import sleep

version = "2.3"

class fileList():

    def __init__( self, path ):
        self.files = []
        self.file_names_only = []
        number_list = []
        elem_counter = 1
        for( dirpath, dirnames, filenames ) in walk( GLib.get_home_dir() + "/.wallpapers" ):
            self.files.extend( filenames )

        self.files = [ elem for elem in self.files if not ".Xres" in elem ]
        self.files = [ elem for elem in self.files if not ".sample" in elem ]
        self.files = [ elem for elem in self.files if not ".colors" in elem ]
        self.files = [ elem for elem in self.files if not ".current" in elem ]
        self.files = [ elem for elem in self.files if not ".sh" in elem ]
        # filter function goes up there
        self.file_names_only = self.files

    def show_list( self ):
        print( self.files )
    
    def show_files_only( self ):
        print( self.file_names_only )

#-------------------------------------------------------------------------------------
class mainWindow( Gtk.Window ):

    def __init__( self ):
        Gtk.Window.__init__( self, title = "wpgtk " + version )
        
        filepath = GLib.get_home_dir() + "/.wallpapers/"
        current_walls = fileList( filepath )
        current_walls.show_files_only()
        image_name = filepath + ".current"
        image_name = os.path.realpath( image_name )
        print( "CURRENT WALLPAPER: " + image_name )

        #these variables are just to get the image and preview of current wallpaper
        route_list = image_name.split( "/", image_name.count("/") )
        file_name = route_list[4]
        sample_name = filepath + "." + file_name + ".sample.png"

        option_list = Gtk.ListStore( str )
        for elem in list(current_walls.files):
            option_list.append( [elem] )
        self.option_combo = Gtk.ComboBox.new_with_model( option_list )
        self.renderer_text = Gtk.CellRendererText()
        self.option_combo.pack_start( self.renderer_text, True )
        self.option_combo.add_attribute( self.renderer_text, "text", 0 )
        self.option_combo.set_entry_text_column( 0 )

        self.textbox = Gtk.Label()
        self.textbox.set_text( "Select colorscheme" )
        self.colorscheme = Gtk.ComboBox.new_with_model( option_list )
        self.colorscheme.pack_start( self.renderer_text, True )
        self.colorscheme.add_attribute( self.renderer_text, "text", 0 )
        self.colorscheme.set_entry_text_column( 0 )

        self.set_border_width( 10 )
        self.grid = Gtk.Grid()
        self.grid.set_column_homogeneous( 1 )
        self.grid.set_row_spacing( 10 )
        self.grid.set_column_spacing( 10 )
        self.add( self.grid )
        self.preview = Gtk.Image()
        self.sample = Gtk.Image()
        if( os.path.isfile( image_name ) and os.path.isfile(sample_name) ):
            self.pixbuf_preview = GdkPixbuf.Pixbuf.new_from_file_at_scale( image_name, width=500, height=333, preserve_aspect_ratio=False )
            self.pixbuf_sample = GdkPixbuf.Pixbuf.new_from_file_at_size( sample_name, width=500, height=500 )
            self.preview.set_from_pixbuf( self.pixbuf_preview )
            self.sample.set_from_pixbuf( self.pixbuf_sample )
        self.add_button = Gtk.Button( label = "Add" )
        self.set_button = Gtk.Button( label = "Set" )
        self.rm_button = Gtk.Button( label = "Remove" )
        self.grid.attach( self.option_combo, 1, 1, 2, 1 ) #adds to first cell in grid
        self.grid.attach( self.colorscheme, 1, 2, 2, 1 )
        self.grid.attach( self.set_button, 3, 1, 1, 1 )
        self.grid.attach( self.add_button, 3, 2, 2, 1 )
        self.grid.attach( self.rm_button, 4, 1, 1, 1 )
        self.grid.attach( self.preview, 1, 3, 4, 1 )
        self.grid.attach( self.sample, 1, 4, 4, 1 )
        self.add_button.connect( "clicked", self.on_add_clicked )
        self.set_button.connect( "clicked", self.on_set_clicked )
        self.rm_button.connect( "clicked", self.on_rm_clicked )
        self.option_combo.connect( "changed", self.combo_box_change )
        self.colorscheme.connect( "changed", self.colorscheme_box_change )
        self.entry = Gtk.Entry()
        self.current_walls = Gtk.ComboBox()

    def on_add_clicked( self, widget ):
        print( "Adding..." )
        filechooser = Gtk.FileChooserDialog( "Select an Image", self, Gtk.FileChooserAction.OPEN,
                (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                 Gtk.STOCK_OPEN, Gtk.ResponseType.OK) )
        response = filechooser.run()

        if response == Gtk.ResponseType.OK:
            print( "Open Clicked" )
            filepath = filechooser.get_filename()
            filechooser.destroy()
            if( "\\" in filepath ):
                filepath = filepath.replace( "\\", "\\\\" )
            if( " " in filepath ):
                filepath = filepath.replace( " ", "\ " )
                filename = filepath.split( "/", len(filepath) )
                filename = filename.pop()
                if( " " in filename ):
                    filename = filename.replace( " ", "\ " )
                elif( "\\" in filename ):
                    filename = filename.replace( "\\", "\\\\" )
                call( "cp " + filepath + " ./" + filename, shell=True )
                call( "wpcscript add " + "./" + filename, shell=True )
                call( "rm ./" + filename, shell=True )
            else:
                call( "wpcscript add " + filepath, shell=True )
            option_list = Gtk.ListStore( str )
            current_walls = fileList( filepath )

            for elem in list(current_walls.files):
                option_list.append( [elem] )
            self.option_combo.set_model( option_list )
            self.option_combo.set_entry_text_column( 0 )
            self.colorscheme.set_model( option_list )
            self.colorscheme.set_entry_text_column( 0 )
        elif response == Gtk.ResponseType.CANCEL:
            filechooser.destroy()
        print( "Done." )


    def on_set_clicked( self, widget ):
        print( "Setting..." )
        x = self.option_combo.get_active()
        y = self.colorscheme.get_active()
        path = GLib.get_home_dir() + "/.wallpapers/"
        current_walls = fileList( path )
        filepath = current_walls.file_names_only[x]
        colorscheme_file = current_walls.file_names_only[y]
        colorscheme = "." + colorscheme_file + ".Xres"
        colorscheme_sample = "." + current_walls.file_names_only[y] + ".sample.png"
        if( not os.path.isfile( path + colorscheme ) or not os.path.isfile( path + colorscheme_sample ) ):
            print( ":: " + path + colorscheme + " NOT FOUND" )
            print( ":: GENERATING COLORS" )
            call( [ "wpcscript", "add", path + filepath ] )
            self.pixbuf_sample = GdkPixbuf.Pixbuf.new_from_file_at_size( path + colorscheme_sample, width=500, height=500 )
            self.sample.set_from_pixbuf( self.pixbuf_sample )
        call( [ "wpcscript", "change", filepath ] )
        call( [ "xrdb", "-merge", path + colorscheme] )
        init_file = open( GLib.get_home_dir() + "/.wallpapers/wp_init.sh", "w" )
        init_file.writelines( [ "#!/bin/bash\n", "wpcscript change " + filepath + " && " ] )
        init_file.writelines( "xrdb -merge " + path + colorscheme + "\n" )
        init_file.close()
        call( [ "chmod", "+x", GLib.get_home_dir() + "/.wallpapers/wp_init.sh" ] )
        if( os.path.isfile(GLib.get_home_dir() + "/.themes/colorbamboo/openbox-3/themerc.base") ):
            execute_gcolorchange( colorscheme_file )
        print( "Done." )

    def on_rm_clicked( self, widget ):
        print( "Deleting..." )
        x = self.option_combo.get_active()
        current_walls = fileList( GLib.get_home_dir() + "/.wallpapers" )
        filepath = current_walls.file_names_only[x]
        call( [ "wpcscript", "rm", filepath ] )
        call( [ "rm", GLib.get_home_dir() + "/.wallpapers/" + "." + filepath + ".sample.png" ] )
        option_list = Gtk.ListStore( str )
        current_walls = fileList( filepath )
        for elem in list(current_walls.files):
            option_list.append( [elem] )
        self.option_combo.set_model( option_list )
        self.option_combo.set_entry_text_column( 0 )
        self.colorscheme.set_model( option_list )
        self.colorscheme.set_entry_text_column( 0 )
        print( "Done." )

    def combo_box_change( self, widget ):
        x = self.option_combo.get_active()
        self.colorscheme.set_active( x )
        current_walls = fileList( GLib.get_home_dir() + "/.wallpapers" )
        selected_file = current_walls.file_names_only[x]
        selected_sample = "." + selected_file + ".sample.png"
        filepath = GLib.get_home_dir() + "/.wallpapers/" + selected_file
        samplepath = GLib.get_home_dir() + "/.wallpapers/" + selected_sample
        self.pixbuf_preview = GdkPixbuf.Pixbuf.new_from_file_at_scale( filepath, width=500, height=333, preserve_aspect_ratio=False )
        self.preview.set_from_pixbuf( self.pixbuf_preview )

    def colorscheme_box_change( self, widget ):
        x = self.colorscheme.get_active()
        current_walls = fileList( GLib.get_home_dir() + "/.wallpapers" )
        selected_file = current_walls.file_names_only[x]
        selected_sample = "." + selected_file + ".sample.png"
        samplepath = GLib.get_home_dir() + "/.wallpapers/" + selected_sample
        nosamplepath = GLib.get_home_dir() + "/.wallpapers/" + ".no_sample.sample.png"
        if( os.path.isfile( samplepath ) ):
            self.pixbuf_sample = GdkPixbuf.Pixbuf.new_from_file_at_size( samplepath, width=500, height=500 )
        else:
            self.pixbuf_sample = GdkPixbuf.Pixbuf.new_from_file_at_size( nosamplepath, width=500, height=500 )
        self.sample.set_from_pixbuf( self.pixbuf_sample )

if __name__ == "__main__":
    win = mainWindow()
    win.connect( "delete-event", Gtk.main_quit )
    win.show_all()
    Gtk.main()
