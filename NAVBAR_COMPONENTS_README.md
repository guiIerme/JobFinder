# Modern Responsive Navbar Components

This repository contains three implementations of a modern, responsive navbar inspired by the Job Finder website layout. Each implementation is designed for a different technology stack:

## 1. HTML + CSS + JavaScript

### Features:
- Pure HTML, CSS, and JavaScript implementation
- Responsive design with Bootstrap 5
- Smooth dropdown animation
- Clean, modern design with rounded corners and subtle shadows
- Automatic closing when clicking outside the dropdown

### Files:
- `navbar-html-css-js.html` - Complete HTML file with embedded CSS and JavaScript

### How to use:
Simply open the HTML file in a browser. All dependencies are loaded from CDNs.

## 2. React + TailwindCSS

### Features:
- React functional component with hooks
- TailwindCSS for styling
- Responsive design
- Smooth dropdown animation with CSS transitions
- Automatic closing when clicking outside the dropdown

### Files:
- `NavbarReact.jsx` - React component

### How to use:
1. Import the component into your React application
2. Make sure you have TailwindCSS configured in your project
3. Include Font Awesome for icons

```jsx
import Navbar from './NavbarReact';

function App() {
  return (
    <div>
      <Navbar />
      {/* Rest of your app */}
    </div>
  );
}
```

## 3. KivyMD (Python)

### Features:
- Python implementation using KivyMD
- Material Design components
- Responsive layout
- Dropdown menu with smooth animations
- Clean, modern design

### Files:
- `navbar_kivymd.py` - Python script with KivyMD implementation

### How to use:
1. Install Kivy and KivyMD:
   ```bash
   pip install kivy kivymd
   ```
2. Run the Python script:
   ```bash
   python navbar_kivymd.py
   ```

## Design Features (All Versions):

### Navbar Elements:
- Logo with icon and text ("Job Finder")
- Navigation links: "Início", "Buscar Profissionais", "Parceiros", "Sobre", "Contato", "Blog"
- User profile section with avatar (initial "i") and name ("isaque")

### Dropdown Menu:
- Smooth transition animations
- Rounded corners
- Subtle shadow
- Clean, modern design
- Options: "Meu Perfil", "Configurações", "Sair"
- Automatically closes when clicking outside

### Responsiveness:
- Collapses into hamburger menu on small screens
- Adapts to different screen sizes
- Mobile-friendly touch targets

## Customization:

All versions can be easily customized:
- Colors: Modify the color variables in CSS/Python
- Spacing: Adjust padding and margin values
- Fonts: Change font families and sizes
- Icons: Replace Font Awesome icons with your preferred icon set

## Browser/Platform Support:

- HTML/CSS/JS: All modern browsers
- React: Modern browsers with ES6 support
- KivyMD: Windows, macOS, Linux, Android, iOS

## Dependencies:

### HTML + CSS + JS:
- Bootstrap 5 (CDN)
- Font Awesome (CDN)

### React + TailwindCSS:
- React 17+
- TailwindCSS
- Font Awesome

### KivyMD:
- Python 3.7+
- Kivy
- KivyMD