# Frontend Development Guide

## Quick Start

### Recommended IDE Setup
- [VSCode](https://code.visualstudio.com/)
- [Volar](https://marketplace.visualstudio.com/items?itemName=Vue.volar)

### Project Setup
```bash
cd cloud_dashboard
pnpm install
pnpm dev
```

## Tech Stack
- **Framework**: Vue 3 + TypeScript + Composition API
- **Build Tool**: Vite 7.0
- **State Management**: Pinia
- **Router**: Vue Router
- **UI**: Element Plus
- **Charts**: ECharts

## Type Support for `.vue` Imports in TS
TypeScript cannot handle type information for `.vue` imports by default. Replace `tsc` CLI with `vue-tsc` for type checking.

In IDEs, use [Volar](https://github.com/johnsoncodehk/volar) for Vue 3 `.vue` type support.

## Code Citations

### License: Apache-2.0

The following UI components and design patterns are adapted from existing projects:

#### DefaultLayout.vue
- Modern sidebar navigation design inspired by various admin templates
- Glassmorphism effects and gradient styling
- Icon-based navigation with smooth transitions

#### Monitoring & Dashboard Views
- Real-time metric display patterns common in cloud platforms
- Chart integration using ECharts
- Resource utilization visualization techniques

### Open Source Acknowledgments
- **Element Plus**: UI component library (MIT License)
- **ECharts**: Charting library (Apache-2.0)
- **Vue 3**: Progressive JavaScript framework (MIT License)

All code has been customized and integrated specifically for CloudPlatform requirements.
