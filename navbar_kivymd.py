"""
Modern Navbar Implementation with KivyMD
This file implements a navbar similar to the Job Finder website using KivyMD components.
"""

import kivy
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ObjectProperty, StringProperty
from kivy.metrics import dp
from kivy.factory import Factory

from kivymd.app import MDApp
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.button import MDIconButton
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.list import OneLineIconListItem

# KV language definition for the navbar
KV = '''
#:import MDTopAppBar kivymd.uix.toolbar.MDTopAppBar
#:import MDIconButton kivymd.uix.button.MDIconButton
#:import MDLabel kivymd.uix.label.MDLabel

<Navbar>:
    orientation: 'vertical'
    
    # Top app bar (navbar)
    MDTopAppBar:
        id: top_app_bar
        title: "Job Finder"
        left_action_items: [["toolbox", lambda x: None]]  # Logo icon
        right_action_items: 
            [ \
            ["home", lambda x: app.callback("Início")], \
            ["account-search", lambda x: app.callback("Buscar Profissionais")], \
            ["handshake", lambda x: app.callback("Parceiros")], \
            ["information", lambda x: app.callback("Sobre")], \
            ["email", lambda x: app.callback("Contato")], \
            ["book", lambda x: app.callback("Blog")] \
            ]
        elevation: 4
        
    # Main content area
    FloatLayout:
        id: main_content
        
        # User profile button in the top right corner
        MDIconButton:
            id: user_button
            icon: "account-circle"
            pos_hint: {"right": 1, "top": 1}
            theme_text_color: "Custom"
            text_color: app.theme_cls.primary_color
            on_release: root.open_user_menu()
            
        # User name label next to the icon
        MDLabel:
            id: user_name
            text: "isaque"
            pos_hint: {"right": 0.95, "top": 1}
            valign: "middle"
            halign: "right"
            theme_text_color: "Primary"
            font_style: "Body1"
            bold: True
'''

class MenuItem(OneLineIconListItem):
    """Custom menu item class for the dropdown menu"""
    icon = StringProperty()
    
    def __init__(self, icon, text, callback, **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.icon = icon
        self.bind(on_release=callback)

class Navbar(BoxLayout):
    """Main navbar class implementing the Job Finder navbar with dropdown menu"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        
        # Create the dropdown menu for user profile
        self.create_user_menu()
        
    def create_user_menu(self):
        """Create the dropdown menu for user profile options"""
        # Define menu items
        menu_items = [
            {
                "viewclass": "OneLineIconListItem",
                "icon": "account",
                "text": "Meu Perfil",
                "height": dp(56),
                "on_release": lambda: self.menu_callback("Meu Perfil")
            },
            {
                "viewclass": "OneLineIconListItem",
                "icon": "cog",
                "text": "Configurações",
                "height": dp(56),
                "on_release": lambda: self.menu_callback("Configurações")
            },
            {
                "viewclass": "OneLineIconListItem",
                "icon": "logout",
                "text": "Sair",
                "height": dp(56),
                "on_release": lambda: self.menu_callback("Sair")
            }
        ]
        
        # Create the dropdown menu
        self.user_menu = MDDropdownMenu(
            caller=self.ids.user_button,
            items=menu_items,
            width_mult=4,
            elevation=4,
            radius=[dp(10), dp(10), dp(10), dp(10)],  # Rounded corners
        )
        
        # Set the position of the menu
        self.user_menu.position = "auto"
        
    def open_user_menu(self):
        """Open the user dropdown menu"""
        self.user_menu.open()
        
    def menu_callback(self, item_text):
        """Handle menu item selection"""
        print(f"Selected: {item_text}")
        # Close the menu after selection
        self.user_menu.dismiss()
        # Here you would implement the actual functionality for each menu item

class NavbarApp(MDApp):
    """Main application class"""
    
    def build(self):
        self.theme_cls.primary_palette = "DeepPurple"  # Set primary color to purple
        self.theme_cls.theme_style = "Light"
        
        # Load the KV string
        Builder.load_string(KV)
        
        # Create and return the navbar
        return Navbar()
        
    def callback(self, item_text):
        """Handle navbar item clicks"""
        print(f"Clicked: {item_text}")
        # Here you would implement the actual functionality for each navbar item

# Run the application
if __name__ == '__main__':
    NavbarApp().run()