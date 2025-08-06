# Interactive Canvas Project Tree

## Overview

This project now features a modern, interactive Canvas-based project tree visualization that replaces the previous Graphviz implementation. The new implementation provides a much more interactive and user-friendly experience.

## Features

### 🎨 **Interactive Visualization**

- **Drag & Pan**: Click and drag to navigate around the tree
- **Zoom**: Mouse wheel or zoom controls to zoom in/out (10% - 500%)
- **Smooth Animations**: Animated transitions when changing layouts
- **High DPI Support**: Crisp rendering on all screen types

### 🎯 **Navigation Controls**

- **Center View**: Automatically center the tree in the viewport
- **Fit to View**: Automatically scale and center to show all nodes
- **Reset View**: Return to default zoom and position
- **Search**: Real-time search through project names with highlighting

### 📱 **Responsive Design**

- **Mobile Support**: Touch-enabled for mobile devices
- **Responsive UI**: Adapts to different screen sizes
- **Modern Glass-morphism UI**: Beautiful translucent control panels

### 🌳 **Tree Layouts**

- **Vertical Layout**: Traditional top-to-bottom tree layout
- **Horizontal Layout**: Left-to-right tree layout
- **Dynamic Switching**: Change layouts on-the-fly

### 🎨 **Visual Features**

- **Color-coded Nodes**: Different colors for different node types
- **Hover Effects**: Visual feedback on mouse hover
- **Selection Highlighting**: Click to select and highlight nodes
- **Node Information Panel**: Detailed information about selected nodes
- **Legend**: Color legend explaining node types

### 🔍 **Node Types & Colors**

- 🔵 **Root Projects** (#3498db) - Top-level project containers
- 🟢 **Projects** (#2ecc71) - Individual projects
- 🟠 **Assigned Resources** (#f39c12) - Resources assigned to projects
- 🟣 **Resource Groups** (#9b59b6) - Groups of resources
- 🔷 **Individual Resources** (#1abc9c) - Specific team members
- 🔴 **POC (Point of Contact)** (#e74c3c) - Project points of contact

## Technical Implementation

### Frontend Technology

- **HTML5 Canvas**: Hardware-accelerated rendering
- **Vanilla JavaScript**: No heavy framework dependencies
- **Bootstrap 5**: Modern responsive UI components
- **Font Awesome**: Beautiful icon set

### Backend Integration

- **Django REST API**: Efficient data loading via JSON API
- **Real-time Data**: Loads current project data from database
- **Error Handling**: Graceful fallbacks for connection issues

### Performance Features

- **Efficient Rendering**: Only redraws when necessary
- **Request Animation Frame**: Smooth 60fps animations
- **Memory Optimized**: Efficient node management
- **Fast Search**: Real-time filtering without lag

## Usage

### Basic Navigation

1. **Panning**: Click and drag to move around the tree
2. **Zooming**: Use mouse wheel or +/- buttons
3. **Node Selection**: Click on any node to see details
4. **Search**: Type in the search box to filter nodes

### Advanced Features

1. **Layout Switching**: Use Vertical/Horizontal buttons to change tree orientation
2. **Auto-fit**: Click "Fit All" to automatically scale the view
3. **Animation Toggle**: Turn animations on/off for better performance
4. **Reset**: Return to default view with the Reset button

### Mobile Usage

- **Touch Support**: Full touch navigation support
- **Pinch to Zoom**: Natural pinch gestures for zooming
- **Touch Drag**: Drag with finger to pan around

## Advantages over Graphviz

### 🚀 **Performance**

- No server-side image generation required
- Instant loading and interaction
- No external dependencies (Graphviz installation not needed)

### 💫 **User Experience**

- Real-time interactions
- Smooth animations and transitions
- Responsive to user input
- Better mobile experience

### 🛠 **Maintainability**

- Pure web technologies (HTML5, CSS3, JavaScript)
- No external executable dependencies
- Easier deployment and setup
- Cross-platform compatibility

### 🎨 **Customization**

- Easy to modify colors and styling
- Extensible for new node types
- Customizable layouts and animations

## Browser Compatibility

- ✅ Chrome 60+
- ✅ Firefox 55+
- ✅ Safari 12+
- ✅ Edge 79+
- ✅ Mobile browsers (iOS Safari, Chrome Mobile)

## Future Enhancements

### Planned Features

- **Export Options**: Save tree as PNG/SVG
- **Collapsible Nodes**: Expand/collapse tree branches
- **Filter Options**: Filter by project type, status, etc.
- **Minimap**: Overview minimap for large trees
- **Clustering**: Group related nodes automatically

### Performance Improvements

- **Virtual Rendering**: Only render visible nodes for very large trees
- **WebGL Support**: Hardware acceleration for complex visualizations
- **Worker Threads**: Background processing for large datasets

## Migration from Graphviz

The old Graphviz implementation has been completely replaced. All URLs remain the same:

- `/project-tree-view/` - Main interactive tree page
- `/project-tree/` - JSON API endpoint (unchanged)

No data migration is required as the same JSON API is used.

## Development

### Adding New Node Types

1. Update the `determineNodeColor()` function in the JavaScript
2. Add new color to the `nodeColors` object
3. Update the legend in the HTML template

### Customizing Layouts

1. Modify the `layoutNodes()` function
2. Adjust spacing and positioning algorithms
3. Update animation targets

### Performance Tuning

1. Adjust animation frame rates in `animateToTargets()`
2. Modify render frequency based on node count
3. Optimize canvas clearing and drawing operations

## Support

For issues or questions about the Canvas tree implementation:

1. Check browser console for JavaScript errors
2. Verify API endpoints are working (`/project-tree/`)
3. Test with different browsers
4. Check network connectivity for data loading
