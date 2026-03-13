# AMAW MVP - Agentic Multimodal AI Workspace

This is the MVP implementation of AMAW (Agentic Multimodal AI Workspace) as described in the PRD.

## Features

- **Full-screen Canvas**: React-based canvas with background color #002147
- **Zoom & Pan**: Interactive canvas with zoom and pan capabilities
- **D3.js Integration**: Random dots rendered using D3.js for visual elements
- **React Flow**: Built on React Flow for professional canvas functionality
- **Tailwind CSS**: Modern styling framework for responsive design
- **PC-Optimized**: Designed for desktop/PC usage with full-screen layout

## Tech Stack

- **Frontend**: React 18 + Vite
- **Canvas**: React Flow (@xyflow/react)
- **Styling**: Tailwind CSS
- **Visualization**: D3.js
- **Build Tool**: Vite

## Setup Instructions

1. **Install Dependencies**:
   ```bash
   npm install
   ```

2. **Start Development Server**:
   ```bash
   npm run dev
   ```

3. **Build for Production**:
   ```bash
   npm run build
   ```

## Project Structure

```
src/
├── components/
│   └── CanvasComponent.jsx    # Main canvas component
├── App.jsx                     # Main app component
├── main.jsx                    # React entry point
└── index.css                   # Global styles + Tailwind
```

## Canvas Features

- **Background**: Deep blue (#002147) as specified
- **Interactive**: Zoom with mouse wheel, pan with drag
- **Visual Elements**: 150 randomly placed dots using D3.js
- **Controls**: Built-in zoom controls and fit-to-view
- **Responsive**: Full-screen layout optimized for PC

## Next Steps

This MVP implements the basic canvas foundation. Future development will include:
- Node-based UI for files and media
- Multimodal input handling
- AI agent integration
- Workflow automation features
- Enterprise collaboration tools

## PRD Compliance

This implementation follows the PRD specifications:
- Uses React + Tailwind + D3.js as specified
- Implements canvas-based UI foundation
- Follows the technical requirements for frontend
- Maintains the vision of a multimodal AI workspace
