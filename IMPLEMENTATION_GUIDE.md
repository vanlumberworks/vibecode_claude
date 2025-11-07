# Frontend Implementation Guide

Complete guide for the Vite + React + shadcn/ui + Tailwind CSS frontend.

## ✅ What's Been Completed

### 1. Project Structure ✓
```
frontend/
├── src/
│   ├── components/        # React components (empty, ready for implementation)
│   ├── hooks/            # Custom hooks
│   ├── types/            # TypeScript types
│   │   └── forex-api.ts  # ✓ Copied from frontend-examples
│   ├── lib/
│   │   └── utils.ts      # ✓ shadcn/ui utility
│   ├── App.tsx           # ✓ Basic placeholder
│   ├── main.tsx          # ✓ Entry point
│   └── index.css         # ✓ Tailwind + CSS variables
├── index.html            # ✓
├── package.json          # ✓ All dependencies
├── vite.config.ts        # ✓ Configured with proxy
├── tsconfig.json         # ✓
├── tailwind.config.js    # ✓
├── postcss.config.js     # ✓
└── components.json       # ✓ shadcn/ui config
```

### 2. Configuration ✓
- **Vite** - Configured with React plugin and proxy to backend
- **TypeScript** - Strict mode enabled, path aliases configured
- **Tailwind CSS** - Installed with custom theme
- **shadcn/ui** - Configured, ready to add components
- **Proxy** - `/analyze`, `/health`, `/info` → `http://localhost:8000`

### 3. Dependencies Installed ✓
- React 18
- TypeScript 5.2
- Vite 5.0
- Tailwind CSS 3.4
- All Radix UI primitives for shadcn/ui
- Lucide React (icons)

### 4. Monorepo Setup ✓
- Root `package.json` with workspace
- Scripts for running both backend and frontend
- Concurrently for parallel dev servers

## 🚀 Quick Start

### Install Dependencies

```bash
# Install root dependencies (concurrently)
npm install

# Install frontend dependencies
npm run install:frontend
```

### Run Development Servers

```bash
# Start both backend and frontend
npm run dev
```

This runs:
- Backend: `http://localhost:8000`
- Frontend: `http://localhost:3000`

## 📋 Next Steps - Implementation Checklist

### Phase 1: shadcn/ui Components (HIGH PRIORITY)

Add the following shadcn/ui components:

```bash
cd frontend

# Install required components
npx shadcn-ui@latest add button
npx shadcn-ui@latest add card
npx shadcn-ui@latest add input
npx shadcn-ui@latest add scroll-area
npx shadcn-ui@latest add separator
npx shadcn-ui@latest add badge
npx shadcn-ui@latest add avatar
npx shadcn-ui@latest add toast
```

These will be added to `src/components/ui/`

### Phase 2: Core Components

Create these components in `src/components/`:

#### 1. `ChatMessage.tsx`
```tsx
type: 'user' | 'assistant' | 'event'
content: string
timestamp: string
eventType?: EventType
```

Display individual messages in the chat

#### 2. `MessageList.tsx`
```tsx
messages: ChatMessage[]
isAnalyzing: boolean
```

Scrollable list of all messages with auto-scroll

#### 3. `EventCard.tsx`
```tsx
eventType: EventType
data: any
timestamp: string
```

Display individual LangGraph events (start, query_parsed, agent_update, etc.)

#### 4. `AnalysisReport.tsx`
```tsx
decision: Decision
queryContext: QueryContext
agentResults: AgentResults
```

Final comprehensive report card

#### 5. `ChatInput.tsx`
```tsx
onSubmit: (query: string) => void
isDisabled: boolean
```

Input form with send button

### Phase 3: Streaming Logic

#### 1. Copy and adapt `useForexAnalysis` hook

```bash
cp ../frontend-examples/useForexAnalysis.tsx src/hooks/
```

Modify to work with new component structure

#### 2. Integrate EventSource

Update `App.tsx` to use the hook:

```tsx
import { useForexAnalysis } from './hooks/useForexAnalysis'

const { analyze, state, isAnalyzing, error } = useForexAnalysis({
  apiUrl: 'http://localhost:8000'
})
```

#### 3. Handle All Event Types

Create message/event objects for:
- `start` → "Analysis started..."
- `query_parsed` → Show pair and context
- `agent_update` → "📰 News agent completed"
- `risk_update` → "⚖️ Risk: APPROVED/REJECTED"
- `decision` → Show decision badge
- `complete` → Render full report
- `error` → Show error message

### Phase 4: UI Implementation

#### Update `App.tsx`

```tsx
return (
  <div className="min-h-screen bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500">
    <div className="container mx-auto p-4 h-screen flex flex-col">
      <Header />

      <Card className="flex-1 flex flex-col">
        <MessageList messages={messages} />
        <Separator />
        <ChatInput onSubmit={analyze} isDisabled={isAnalyzing} />
      </Card>

      {state.decision && (
        <AnalysisReport
          decision={state.decision}
          queryContext={state.queryContext}
        />
      )}
    </div>
  </div>
)
```

### Phase 5: Event Streaming UI

#### Real-Time Event Display

Show events as they arrive:

```tsx
{state.progress.stage === 'analyzing' && (
  <div className="space-y-2">
    <Badge>Analyzing...</Badge>
    <Progress value={(state.progress.agentsCompleted / 3) * 100} />
  </div>
)}

{state.newsResult && <EventCard event="news" data={state.newsResult} />}
{state.technicalResult && <EventCard event="technical" data={state.technicalResult} />}
{state.fundamentalResult && <EventCard event="fundamental" data={state.fundamentalResult} />}
```

#### Reasoning Display

For each agent, show:
- Agent name + emoji
- Status (pending → running → complete)
- Summary text
- Timestamp

### Phase 6: Report Generation

#### Decision Card

```tsx
<Card className="p-6">
  <div className="flex items-center gap-4">
    <div className="text-6xl">
      {decision.action === 'BUY' && '🟢'}
      {decision.action === 'SELL' && '🔴'}
      {decision.action === 'WAIT' && '🟡'}
    </div>
    <div>
      <h2 className="text-3xl font-bold">{decision.action}</h2>
      <p className="text-xl text-muted-foreground">
        Confidence: {(decision.confidence * 100).toFixed(0)}%
      </p>
    </div>
  </div>

  <Separator className="my-6" />

  <div className="space-y-4">
    <div>
      <h3 className="font-semibold mb-2">Summary</h3>
      <p>{decision.reasoning.summary}</p>
    </div>

    <div>
      <h3 className="font-semibold mb-2">Key Factors</h3>
      <ul className="list-disc list-inside space-y-1">
        {decision.reasoning.key_factors.map((factor, i) => (
          <li key={i}>{factor}</li>
        ))}
      </ul>
    </div>

    {decision.trade_parameters && (
      <div>
        <h3 className="font-semibold mb-2">Trade Parameters</h3>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <span className="text-sm text-muted-foreground">Entry</span>
            <p className="font-medium">{decision.trade_parameters.entry_price}</p>
          </div>
          {/* ... more parameters */}
        </div>
      </div>
    )}

    {decision.grounding_metadata?.sources && (
      <div>
        <h3 className="font-semibold mb-2">🌐 Sources</h3>
        {decision.grounding_metadata.sources.map((source, i) => (
          <a
            key={i}
            href={source.url}
            target="_blank"
            className="block text-sm text-blue-600 hover:underline"
          >
            {i + 1}. {source.title}
          </a>
        ))}
      </div>
    )}
  </div>
</Card>
```

## 🎨 Styling Guidelines

### Colors
- **Primary**: Indigo/Purple gradient (already in CSS variables)
- **Success**: Green for BUY decisions
- **Destructive**: Red for SELL decisions
- **Warning**: Yellow for WAIT decisions

### Spacing
- Use Tailwind spacing scale
- Cards: `p-6` for padding
- Gap between elements: `gap-4` or `gap-6`

### Typography
- Headers: `text-3xl` or `text-4xl` with `font-bold`
- Body: `text-base`
- Muted text: `text-muted-foreground`

### Components
- Use `Card` for containers
- Use `Badge` for status indicators
- Use `Separator` between sections
- Use `ScrollArea` for message list

## 🔧 Advanced Features (Optional)

### 1. Analysis History
Store past analyses in localStorage:

```tsx
const [history, setHistory] = useState<AnalysisResult[]>([])

useEffect(() => {
  const saved = localStorage.getItem('analysis-history')
  if (saved) setHistory(JSON.parse(saved))
}, [])

const saveToHistory = (result: AnalysisResult) => {
  const updated = [result, ...history].slice(0, 10) // Keep last 10
  setHistory(updated)
  localStorage.setItem('analysis-history', JSON.stringify(updated))
}
```

### 2. Export Report
Add export functionality:

```tsx
const exportReport = (result: AnalysisResult) => {
  const blob = new Blob([JSON.stringify(result, null, 2)], {
    type: 'application/json'
  })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `forex-analysis-${Date.now()}.json`
  a.click()
}
```

### 3. Dark Mode
Add theme toggle:

```tsx
import { useTheme } from 'next-themes' // or implement custom

const { theme, setTheme } = useTheme()

<Button
  variant="ghost"
  onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
>
  {theme === 'dark' ? '🌞' : '🌙'}
</Button>
```

### 4. Mobile Responsive
Already handled by Tailwind, but verify:
- Stack on mobile: `flex flex-col md:flex-row`
- Hide sidebar on mobile: `hidden md:block`
- Full-width cards on mobile

## 📝 Development Workflow

### 1. Start Development

```bash
# Terminal 1: Backend + Frontend
npm run dev
```

### 2. Add shadcn Components

```bash
cd frontend
npx shadcn-ui@latest add [component-name]
```

### 3. Test Streaming

1. Open `http://localhost:3000`
2. Enter query: "Analyze gold trading"
3. Verify events stream in real-time
4. Check final report generation

### 4. Debug

- **Backend logs**: Check terminal running `dev:backend`
- **Frontend logs**: Check browser console
- **Network**: Check browser DevTools → Network → EventSource

## 🚨 Common Issues

### Proxy Not Working
- Verify backend is running on port 8000
- Check `vite.config.ts` proxy configuration
- Restart Vite dev server

### TypeScript Errors
- Run `npm install` in frontend/
- Check `tsconfig.json` paths
- Verify all imports use `@/` alias

### Tailwind Not Working
- Check `index.css` is imported in `main.tsx`
- Verify `tailwind.config.js` content paths
- Restart Vite dev server

### EventSource Not Connecting
- Check CORS on backend (should allow localhost:3000)
- Verify API URL is correct
- Check browser console for errors

## ✅ Testing Checklist

Before committing:

- [ ] Backend starts without errors
- [ ] Frontend starts on port 3000
- [ ] Can submit query via input
- [ ] Events stream in real-time
- [ ] All 7 event types display correctly
- [ ] Final report renders
- [ ] Trade parameters show (when applicable)
- [ ] Sources display with links
- [ ] Error handling works
- [ ] Mobile responsive
- [ ] No console errors

## 📦 Deployment

### Build Frontend

```bash
npm run build:frontend
```

### Serve with FastAPI (Optional)

Add to `backend/server.py`:

```python
from fastapi.staticfiles import StaticFiles

# After all API routes
app.mount("/", StaticFiles(directory="../frontend/dist", html=True), name="static")
```

Then access everything at `http://localhost:8000`

## 🔗 Resources

- [shadcn/ui Components](https://ui.shadcn.com/docs/components)
- [Tailwind CSS Docs](https://tailwindcss.com/docs)
- [Radix UI](https://www.radix-ui.com/)
- [Lucide Icons](https://lucide.dev/)
- [Vite Guide](https://vitejs.dev/guide/)

## 💡 Next Implementation Steps

**Priority Order:**

1. ✅ Setup complete (DONE)
2. 🔄 Add shadcn/ui components (NEXT)
3. 🔄 Create chat UI components
4. 🔄 Implement streaming logic
5. 🔄 Build report component
6. 🔄 Polish and test

**Estimated Time:**
- shadcn components: 10 minutes
- Chat UI: 30 minutes
- Streaming: 20 minutes
- Report: 20 minutes
- Polish: 20 minutes

**Total:** ~1.5 hours for complete implementation

---

**Ready to continue?** Start with Phase 1 (shadcn components) and work through the checklist!
