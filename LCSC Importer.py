"""
LCSC to KiCad Importer Plugin
Imports parts from LCSC library into KiCad
"""

import pcbnew
import wx
import os
import sys
import logging

# Configure logging
log_file = os.path.join(os.path.dirname(__file__), "lcsc2kicad.log")
logging.basicConfig(
    filename=log_file,
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logging.info("LCSC to KiCad Importer Plugin initializing...")

# Check for required dependencies
def check_dependencies():
    """Check if all required Python packages are installed"""
    required_packages = ['requests', 'pydantic']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        raise ImportError(
            f"Missing required packages: {', '.join(missing_packages)}\n"
            f"Install with: pip install {' '.join(missing_packages)}"
        )

try:
    check_dependencies()
    logging.info("All dependencies satisfied")
except ImportError as e:
    logging.error(f"Dependency check failed: {e}")
    raise e

# Add lcsc2kicad module to path
plugin_dir = os.path.dirname(__file__)
lcsc2kicad_path = os.path.join(plugin_dir, "lcsc2kicad")
sys.path.insert(0, lcsc2kicad_path)

try:
    from lcsc2kicad.__main__ import main
    logging.info("Successfully imported lcsc2kicad module")
except Exception as e:
    logging.error(f"Failed to import lcsc2kicad: {e}")
    wx.MessageBox(
        f"Error loading lcsc2kicad module:\n{e}\n\nCheck lcsc2kicad.log for details",
        "Import Error",
        style=wx.ICON_ERROR
    )
    raise e


class LCSCImporterPlugin(pcbnew.ActionPlugin):
    """KiCad Action Plugin for importing LCSC parts"""
    
    def defaults(self):
        """Set plugin metadata"""
        self.name = "LCSC Part Importer"
        self.category = "Manufacturing"
        self.description = "Import symbols, footprints, and 3D models from LCSC library"
        self.show_toolbar_button = True
        self.icon_file_name = os.path.join(lcsc2kicad_path, "icon.png")
        logging.info("Plugin defaults configured")
    
    def Run(self):
        """Execute the plugin"""
        logging.info("LCSC Importer plugin started")
        
        # Create dialog with modern styling
        dialog = LCSCInputDialog(None)
        
        if dialog.ShowModal() == wx.ID_OK:
            part_number = dialog.get_part_number().strip()
            logging.info(f"User requested import of part: {part_number}")
            
            if not part_number:
                wx.MessageBox(
                    "Please enter a valid LCSC part number",
                    "Invalid Input",
                    style=wx.ICON_WARNING
                )
                dialog.Destroy()
                return
            
            # Show progress dialog
            progress = wx.ProgressDialog(
                "Importing Part",
                f"Downloading {part_number} from LCSC...",
                maximum=100,
                style=wx.PD_APP_MODAL | wx.PD_AUTO_HIDE
            )
            
            try:
                progress.Update(30, f"Processing {part_number}...")
                
                # Call the main import function
                result = main(["--full", f"--lcsc_id={part_number}"])
                
                progress.Update(100, "Complete!")
                
                if result == 0:
                    logging.info(f"Successfully imported part: {part_number}")
                    wx.MessageBox(
                        f"Part {part_number} imported successfully!\n\n"
                        f"You can now find it in your symbol and footprint libraries.",
                        "Import Successful",
                        style=wx.ICON_INFORMATION
                    )
                else:
                    logging.error(f"Import failed with code: {result}")
                    wx.MessageBox(
                        f"Failed to import part {part_number}.\n"
                        f"Please check the part number and try again.\n\n"
                        f"See lcsc2kicad.log for details.",
                        "Import Failed",
                        style=wx.ICON_ERROR
                    )
                    
            except Exception as e:
                error_message = f"Error importing part {part_number}:\n{str(e)}"
                logging.error(error_message)
                wx.MessageBox(
                    error_message + "\n\nCheck lcsc2kicad.log for details.",
                    "Execution Error",
                    style=wx.ICON_ERROR
                )
            finally:
                progress.Destroy()
        else:
            logging.info("User cancelled import dialog")
        
        dialog.Destroy()
        logging.info("Plugin execution completed")


class LCSCInputDialog(wx.Dialog):
    """Custom dialog for LCSC part number input with modern styling"""
    
    def __init__(self, parent):
        super().__init__(
            parent,
            title="LCSC Part Importer",
            size=(450, 250),
            style=wx.DEFAULT_DIALOG_STYLE
        )
        
        self.init_ui()
        self.Centre()
    
    def init_ui(self):
        """Initialize the dialog UI"""
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        # Title with icon area
        title_box = wx.BoxSizer(wx.HORIZONTAL)
        
        title = wx.StaticText(
            panel,
            label="Import Part from LCSC",
            style=wx.ALIGN_LEFT
        )
        title_font = title.GetFont()
        title_font.PointSize += 3
        title_font = title_font.Bold()
        title.SetFont(title_font)
        
        title_box.Add(title, proportion=1, flag=wx.ALL, border=10)
        vbox.Add(title_box, flag=wx.EXPAND)
        
        # Separator line
        vbox.Add(wx.StaticLine(panel), flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=10)
        
        # Instructions
        instructions = wx.StaticText(
            panel,
            label="Enter the LCSC part number (e.g., C2040, C5171):"
        )
        vbox.Add(instructions, flag=wx.ALL | wx.EXPAND, border=15)
        
        # Input field
        hbox_input = wx.BoxSizer(wx.HORIZONTAL)
        label = wx.StaticText(panel, label="Part Number:")
        self.part_input = wx.TextCtrl(panel, size=(250, -1))
        self.part_input.SetHint("C2040")
        
        hbox_input.Add(label, flag=wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border=15)
        hbox_input.Add(self.part_input, flag=wx.LEFT | wx.EXPAND, border=10)
        vbox.Add(hbox_input, flag=wx.ALL | wx.EXPAND, border=10)
        
        # Info text
        info_text = wx.StaticText(
            panel,
            label="This will import the symbol, footprint, and 3D model."
        )
        info_font = info_text.GetFont()
        info_font.PointSize -= 1
        info_text.SetFont(info_font)
        info_text.SetForegroundColour(wx.Colour(128, 128, 128))
        vbox.Add(info_text, flag=wx.LEFT | wx.RIGHT | wx.BOTTOM, border=15)
        
        # Buttons
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        ok_button = wx.Button(panel, wx.ID_OK, "Import")
        cancel_button = wx.Button(panel, wx.ID_CANCEL, "Cancel")
        
        ok_button.SetDefault()
        
        button_sizer.Add(ok_button, flag=wx.ALL, border=5)
        button_sizer.Add(cancel_button, flag=wx.ALL, border=5)
        
        vbox.Add(button_sizer, flag=wx.ALIGN_RIGHT | wx.ALL, border=10)
        
        panel.SetSizer(vbox)
        
        # Bind enter key to OK
        self.part_input.Bind(wx.EVT_TEXT_ENTER, self.on_ok)
        ok_button.Bind(wx.EVT_BUTTON, self.on_ok)
    
    def on_ok(self, event):
        """Handle OK button click"""
        if self.get_part_number().strip():
            self.EndModal(wx.ID_OK)
        else:
            wx.MessageBox(
                "Please enter a part number",
                "Invalid Input",
                style=wx.ICON_WARNING
            )
    
    def get_part_number(self):
        """Get the entered part number"""
        return self.part_input.GetValue()


# Register the plugin with KiCad
LCSCImporterPlugin().register()
logging.info("LCSC Part Importer Plugin registered successfully")
