# Forex Agent Frontend

Production-ready React frontend for the Forex Agent System with real-time streaming capabilities.

## 🎯 Features

- **Chat Interface** - Interactive chat-style UI for submitting queries
- **Real-Time Streaming** - Live updates from LangGraph workflow
- **Event Visualization** - See all agent events, web searches, and reasoning
- **Full Report Generation** - Comprehensive analysis report with trade parameters
- **shadcn/ui Components** - Beautiful, accessible UI components
- **Tailwind CSS** - Utility-first styling
- **TypeScript** - Full type safety

## 🚀 Quick Start

### Install Dependencies

```bash
cd frontend
npm install
```

### Start Development Server

```bash
npm run dev
```

The app will run at `http://localhost:3000`

### Build for Production

```bash
npm run build
```

## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/        # React components
│   │   ├── ui/           # shadcn/ui components
│   │   ├── Chat.tsx      # Main chat interface
│   │   ├── MessageList.tsx
│   │   ├── EventStream.tsx
│   │   └── AnalysisReport.tsx
│   ├── hooks/
│   │   └── useForexAnalysis.tsx
│   ├── types/
│   │   └── forex-api.ts  # TypeScript types
│   ├── lib/
│   │   └── utils.ts      # Utility functions
│   ├── App.tsx
│   ├── main.tsx
│   └── index.css
├── public/
├── package.json
├── vite.config.ts
├── tailwind.config.js
└── README.md
```

## 🎨 UI Components

### Chat Interface
- Query input with streaming status
- Real-time message display
- Event timeline
- Loading states

### Event Stream Display
- **start** - Analysis initiated
- **query_parsed** - Query context
- **agent_update** - Agent completion (News, Technical, Fundamental)
- **risk_update** - Risk assessment
- **decision** - Final decision
- **complete** - Full report

### Analysis Report
- Decision card with confidence
- Key factors
- Trade parameters
- Source citations
- Risk analysis

## 🔧 Configuration

### Environment Variables

Create `.env` in the frontend directory:

```env
VITE_API_URL=http://localhost:8000
```

### Vite Proxy

The Vite config proxies API requests to the backend:

```typescript
server: {
  port: 3000,
  proxy: {
    '/analyze': 'http://localhost:8000',
    '/health': 'http://localhost:8000',
    '/info': 'http://localhost:8000'
  }
}
```

## 📝 Development

### Running Both Frontend and Backend

From the project root:

```bash
npm run dev
```

This runs both:
- Backend: `http://localhost:8000`
- Frontend: `http://localhost:3000`

### Code Structure

#### Types (`src/types/forex-api.ts`)
- All API event types
- Decision, QueryContext, Agent results
- Fully typed EventSource events

#### Hooks (`src/hooks/useForexAnalysis.tsx`)
- `analyze(query)` - Start analysis
- `cancel()` - Cancel analysis
- `state` - Current analysis state
- `isAnalyzing` - Loading state
- `error` - Error state

#### Components
- **Chat.tsx** - Main interface
- **MessageList.tsx** - Event stream display
- **EventStream.tsx** - Real-time events
- **AnalysisReport.tsx** - Final report card

## 🎯 Key Features to Implement

### Phase 1: Core Chat (Current)
- [x] Project setup
- [x] Tailwind + shadcn/ui
- [ ] Chat UI
- [ ] Message components
- [ ] Input form

### Phase 2: Streaming
- [ ] EventSource integration
- [ ] Event display
- [ ] Loading states
- [ ] Error handling

### Phase 3: Report Generation
- [ ] Decision card
- [ ] Trade parameters
- [ ] Key factors
- [ ] Source citations

### Phase 4: Enhancements
- [ ] Analysis history
- [ ] Export report
- [ ] Dark mode
- [ ] Mobile responsive

## 🚧 Implementation Status

**Current Status:** Configuration complete, components in progress

**Next Steps:**
1. Create shadcn/ui base components (Button, Card, Input, ScrollArea)
2. Build chat interface
3. Implement streaming logic
4. Create report components
5. Add polish and animations

## 📦 Dependencies

### Core
- React 18
- TypeScript
- Vite

### UI
- shadcn/ui
- Tailwind CSS
- Radix UI primitives
- Lucide React (icons)

### Utilities
- class-variance-authority
- clsx
- tailwind-merge

## 🔗 Links

- [Main README](../README.md)
- [Backend API](../backend/README.md)
- [Streaming API Docs](../docs/STREAMING_API.md)
- [Frontend Examples](../frontend-examples/README.md)

## 📝 License

Same as main project (MIT)
