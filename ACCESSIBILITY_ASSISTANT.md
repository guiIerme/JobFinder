# Accessibility Assistant with Libras Support

This document explains how to implement and use the accessibility assistant with Libras (Brazilian Sign Language) support for the Job Finder platform.

## Features

1. **Libras Translation**: Integration with VLibras widget for Brazilian Sign Language translation
2. **Font Size Adjustment**: Increase/decrease text size for better readability
3. **High Contrast Mode**: Toggle high contrast for visually impaired users
4. **Text Reader**: Future implementation for text-to-speech functionality
5. **Responsive Design**: Works on both desktop and mobile devices

## Implementation Details

### React Component (Admin Dashboard)

The accessibility assistant is implemented as a React component located at:
`src/components/AccessibilityAssistant.jsx`

It includes:
- Floating toggle button with Libras hand symbol
- Accessible panel with all features
- Local storage for user preferences
- Integration with VLibras API

### Traditional HTML/CSS/JS Implementation

For the main website, the accessibility assistant is implemented with:
- HTML structure in `templates/base.html`
- CSS styles in `src/styles/AccessibilityAssistant.css`
- JavaScript functionality in `static/js/accessibility.js`

## Setup Instructions

### 1. VLibras Integration

VLibras is already integrated and doesn't require an API token. The widget is provided by the Brazilian government and is free to use. No additional setup is required.

### 2. Hand Talk Alternative (if available)

If Hand Talk becomes available again and you prefer to use it instead of VLibras:

1. Register at [Hand Talk](https://www.handtalk.me/) to get an API token
2. Replace `SEU_TOKEN_AQUI` in both:
   - `src/components/AccessibilityAssistant.jsx` (line ~30)
   - `static/js/accessibility.js` (line ~180)
3. Update the loadLibrasWidget function to use Hand Talk instead of VLibras.

## Features Explained

### Libras Translation
- Users can toggle Libras translation on/off
- When activated, a sign language avatar appears on screen
- Translates all text content on the page
- Saves user preference in local storage

### Font Size Adjustment
- Increase text size up to 150%
- Decrease text size down to 80%
- Reset to default 100%
- Applies to all text elements on the page
- Saves user preference in local storage

### High Contrast Mode
- Toggles between normal and high contrast themes
- Improves readability for visually impaired users
- Applies to all UI elements
- Saves user preference in local storage

### Text Reader (Planned)
- Will read page content aloud
- Will support multiple voices and languages
- Will allow customization of reading speed

## Customization

### Styling
All CSS is contained in `src/styles/AccessibilityAssistant.css` and can be customized to match your brand colors.

### Positioning
The floating button is positioned at the bottom right of the screen by default. You can change this by modifying:
- `.accessibility-toggle` in the CSS file
- `bottom` and `right` properties

### Adding New Features
To add new accessibility features:
1. Add the UI elements to the React component or HTML structure
2. Implement the functionality in the JavaScript file
3. Add any necessary CSS styles
4. Save user preferences in local storage

## Testing

### Manual Testing
1. Click the accessibility button (hand icon) at the bottom right
2. Test all toggle functions:
   - Libras translation
   - Font size adjustment
   - High contrast mode
3. Refresh the page to ensure preferences are saved
4. Test on both desktop and mobile devices

### Automated Testing
For automated testing, you can:
1. Check that the accessibility button is present in the DOM
2. Verify that clicking the button opens the panel
3. Confirm that all features modify the page as expected
4. Validate that preferences are saved in local storage

## Browser Support

The accessibility assistant works on all modern browsers:
- Chrome 60+
- Firefox 55+
- Safari 12+
- Edge 79+

For older browsers, some CSS features may need vendor prefixes.

## Performance Considerations

1. The VLibras widget is loaded asynchronously to avoid blocking page rendering
2. All user preferences are stored in local storage for quick access
3. CSS animations are hardware-accelerated for smooth performance
4. The widget only loads when the user activates Libras translation

## Accessibility Compliance

This implementation follows WCAG 2.1 guidelines:
- Proper ARIA attributes for screen readers
- Sufficient color contrast ratios
- Keyboard navigable interface
- Focus management for interactive elements

## Future Enhancements

1. **Text Reader Implementation**: Integrate with Web Speech API
2. **Keyboard Shortcuts**: Add keyboard navigation for all features
3. **More Language Options**: Support for other sign languages
4. **Customization Panel**: Allow users to customize the assistant appearance
5. **Analytics**: Track usage to improve accessibility features

## Troubleshooting

### Libras Widget Not Appearing
1. Verify that the script is loading without errors
2. Ensure that no ad blockers are interfering
3. Check browser console for any JavaScript errors

### Preferences Not Saving
1. Check browser settings for local storage permissions
2. Verify that local storage is not full
3. Test in an incognito/private browsing window

### Styling Issues
1. Check for CSS conflicts with existing styles
2. Ensure that the CSS file is properly loaded
3. Verify z-index values for proper layering

## Support

For issues with the accessibility assistant, contact the development team or check the VLibras documentation for widget-specific issues.