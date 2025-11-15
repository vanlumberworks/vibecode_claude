import { useState } from 'react'
import { motion } from 'motion/react'
import {
  Search,
  Home,
  TrendingUp,
  History,
  Wallet,
  Bitcoin,
  DollarSign,
  Settings,
  HelpCircle,
  ChevronRight,
} from 'lucide-react'
import { Card, CardContent } from './ui/card'
import { Input } from './ui/input'
import { Button } from './ui/button'
import { Badge } from './ui/badge'
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarInset,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarMenuSub,
  SidebarMenuSubButton,
  SidebarMenuSubItem,
  SidebarProvider,
  SidebarTrigger,
} from './ui/sidebar'
import { Separator } from './ui/separator'
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from './ui/collapsible'

interface ChatInterfaceProps {
  onSubmit: (query: string) => void
  isAnalyzing: boolean
}

const SUGGESTED_PROMPTS = [
  {
    icon: '💱',
    title: 'EUR/USD Analysis',
    query: 'Analyze EUR/USD trading opportunity',
    category: 'Forex'
  },
  {
    icon: '🥇',
    title: 'Gold Trading',
    query: 'Should I buy gold right now?',
    category: 'Commodity'
  },
  {
    icon: '₿',
    title: 'Bitcoin Setup',
    query: 'What\'s the technical setup for Bitcoin?',
    category: 'Crypto'
  },
  {
    icon: '🛢️',
    title: 'Oil Markets',
    query: 'Analyze crude oil trading outlook',
    category: 'Commodity'
  },
  {
    icon: '💷',
    title: 'GBP/JPY',
    query: 'GBP/JPY swing trade analysis',
    category: 'Forex'
  },
  {
    icon: '⚡',
    title: 'Quick Scalp',
    query: 'EUR/GBP scalping opportunity',
    category: 'Forex'
  }
]

export function ChatInterface({ onSubmit, isAnalyzing }: ChatInterfaceProps) {
  const [query, setQuery] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (query.trim() && !isAnalyzing) {
      onSubmit(query.trim())
    }
  }

  const handleSuggestedPrompt = (promptQuery: string) => {
    if (!isAnalyzing) {
      setQuery(promptQuery)
      onSubmit(promptQuery)
    }
  }

  return (
    <SidebarProvider>
      <Sidebar>
        <SidebarHeader>
          <SidebarMenu>
            <SidebarMenuItem>
              <SidebarMenuButton size="lg" asChild>
                <div className="flex items-center gap-2">
                  <div className="flex aspect-square size-8 items-center justify-center rounded-lg bg-sidebar-primary text-sidebar-primary-foreground">
                    <TrendingUp className="size-4" />
                  </div>
                  <div className="flex flex-col gap-0.5 leading-none">
                    <span className="font-semibold">Trading Agent</span>
                    <span className="text-xs text-muted-foreground">AI Analysis</span>
                  </div>
                </div>
              </SidebarMenuButton>
            </SidebarMenuItem>
          </SidebarMenu>
        </SidebarHeader>

        <SidebarContent>
          {/* Main Navigation */}
          <SidebarGroup>
            <SidebarGroupLabel>Main</SidebarGroupLabel>
            <SidebarGroupContent>
              <SidebarMenu>
                <SidebarMenuItem>
                  <SidebarMenuButton isActive={true}>
                    <Home className="size-4" />
                    <span>Home</span>
                  </SidebarMenuButton>
                </SidebarMenuItem>
                <SidebarMenuItem>
                  <SidebarMenuButton>
                    <TrendingUp className="size-4" />
                    <span>Active Analysis</span>
                  </SidebarMenuButton>
                </SidebarMenuItem>
                <SidebarMenuItem>
                  <SidebarMenuButton>
                    <History className="size-4" />
                    <span>History</span>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              </SidebarMenu>
            </SidebarGroupContent>
          </SidebarGroup>

          {/* Markets */}
          <SidebarGroup>
            <SidebarGroupLabel>Markets</SidebarGroupLabel>
            <SidebarGroupContent>
              <SidebarMenu>
                <Collapsible defaultOpen={false} className="group/collapsible">
                  <SidebarMenuItem>
                    <CollapsibleTrigger asChild>
                      <SidebarMenuButton>
                        <DollarSign className="size-4" />
                        <span>Forex</span>
                        <ChevronRight className="ml-auto size-4 transition-transform group-data-[state=open]/collapsible:rotate-90" />
                      </SidebarMenuButton>
                    </CollapsibleTrigger>
                    <CollapsibleContent>
                      <SidebarMenuSub>
                        <SidebarMenuSubItem>
                          <SidebarMenuSubButton>EUR/USD</SidebarMenuSubButton>
                        </SidebarMenuSubItem>
                        <SidebarMenuSubItem>
                          <SidebarMenuSubButton>GBP/JPY</SidebarMenuSubButton>
                        </SidebarMenuSubItem>
                        <SidebarMenuSubItem>
                          <SidebarMenuSubButton>USD/JPY</SidebarMenuSubButton>
                        </SidebarMenuSubItem>
                      </SidebarMenuSub>
                    </CollapsibleContent>
                  </SidebarMenuItem>
                </Collapsible>

                <Collapsible defaultOpen={false} className="group/collapsible">
                  <SidebarMenuItem>
                    <CollapsibleTrigger asChild>
                      <SidebarMenuButton>
                        <Wallet className="size-4" />
                        <span>Commodities</span>
                        <ChevronRight className="ml-auto size-4 transition-transform group-data-[state=open]/collapsible:rotate-90" />
                      </SidebarMenuButton>
                    </CollapsibleTrigger>
                    <CollapsibleContent>
                      <SidebarMenuSub>
                        <SidebarMenuSubItem>
                          <SidebarMenuSubButton>Gold (XAU)</SidebarMenuSubButton>
                        </SidebarMenuSubItem>
                        <SidebarMenuSubItem>
                          <SidebarMenuSubButton>Silver (XAG)</SidebarMenuSubButton>
                        </SidebarMenuSubItem>
                        <SidebarMenuSubItem>
                          <SidebarMenuSubButton>Crude Oil</SidebarMenuSubButton>
                        </SidebarMenuSubItem>
                      </SidebarMenuSub>
                    </CollapsibleContent>
                  </SidebarMenuItem>
                </Collapsible>

                <Collapsible defaultOpen={false} className="group/collapsible">
                  <SidebarMenuItem>
                    <CollapsibleTrigger asChild>
                      <SidebarMenuButton>
                        <Bitcoin className="size-4" />
                        <span>Crypto</span>
                        <ChevronRight className="ml-auto size-4 transition-transform group-data-[state=open]/collapsible:rotate-90" />
                      </SidebarMenuButton>
                    </CollapsibleTrigger>
                    <CollapsibleContent>
                      <SidebarMenuSub>
                        <SidebarMenuSubItem>
                          <SidebarMenuSubButton>Bitcoin</SidebarMenuSubButton>
                        </SidebarMenuSubItem>
                        <SidebarMenuSubItem>
                          <SidebarMenuSubButton>Ethereum</SidebarMenuSubButton>
                        </SidebarMenuSubItem>
                        <SidebarMenuSubItem>
                          <SidebarMenuSubButton>Solana</SidebarMenuSubButton>
                        </SidebarMenuSubItem>
                      </SidebarMenuSub>
                    </CollapsibleContent>
                  </SidebarMenuItem>
                </Collapsible>
              </SidebarMenu>
            </SidebarGroupContent>
          </SidebarGroup>
        </SidebarContent>

        <SidebarFooter>
          <SidebarMenu>
            <SidebarMenuItem>
              <SidebarMenuButton>
                <Settings className="size-4" />
                <span>Settings</span>
              </SidebarMenuButton>
            </SidebarMenuItem>
            <SidebarMenuItem>
              <SidebarMenuButton>
                <HelpCircle className="size-4" />
                <span>Help</span>
              </SidebarMenuButton>
            </SidebarMenuItem>
          </SidebarMenu>
        </SidebarFooter>
      </Sidebar>

      <SidebarInset>
        <div className="min-h-screen flex flex-col">
          {/* Header with Trigger */}
          <header className="flex h-16 shrink-0 items-center gap-2 border-b px-4">
            <SidebarTrigger />
            <Separator orientation="vertical" className="h-6" />
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
              <span className="text-sm text-muted-foreground">
                API Connected • Multi-Agent System
              </span>
            </div>
          </header>

          {/* Main Content */}
          <div className="flex-1 flex items-center justify-center relative bg-background p-6">
            {/* Subtle gradient background */}
            <div className="absolute inset-0 bg-gradient-to-br from-background via-background to-muted/20 pointer-events-none" />

            {/* Main Content */}
            <div className="relative z-10 w-full max-w-4xl">
        {/* Header */}
        <motion.div
          className="text-center mb-12"
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
        >
          <h1 className="text-6xl font-semibold mb-3 tracking-tight">
            Trading Agent System
          </h1>
          <p className="text-lg text-muted-foreground">
            AI-Powered Multi-Agent Trading Analysis
          </p>
        </motion.div>

        {/* Search Box */}
        <motion.form
          onSubmit={handleSubmit}
          className="mb-12"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.1 }}
        >
          <Card>
            <CardContent className="p-3">
              <div className="flex items-center gap-3">
                <Search className="h-5 w-5 text-muted-foreground flex-shrink-0" />
                <Input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Enter trading query... (e.g., 'Analyze EUR/USD', 'Should I buy Bitcoin?')"
                  className="border-0 focus-visible:ring-0 focus-visible:ring-offset-0 text-base"
                  disabled={isAnalyzing}
                />
                <Button
                  type="submit"
                  disabled={!query.trim() || isAnalyzing}
                  size="default"
                  className="flex-shrink-0"
                >
                  {isAnalyzing ? (
                    <>
                      <span className="inline-block w-4 h-4 border-2 border-t-transparent border-current rounded-full animate-spin mr-2" />
                      Analyzing
                    </>
                  ) : (
                    'Analyze'
                  )}
                </Button>
              </div>
            </CardContent>
          </Card>
        </motion.form>

        {/* Suggested Prompts */}
        {!isAnalyzing && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: 0.2 }}
          >
            <div className="text-center mb-6">
              <p className="text-sm text-muted-foreground uppercase tracking-wider">
                Try these popular prompts
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {SUGGESTED_PROMPTS.map((prompt, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3, delay: 0.3 + index * 0.05 }}
                >
                  <Card
                    className="cursor-pointer hover:bg-accent transition-colors"
                    onClick={() => handleSuggestedPrompt(prompt.query)}
                  >
                    <CardContent className="p-4">
                      <div className="flex items-start gap-3">
                        <div className="text-2xl">{prompt.icon}</div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center justify-between mb-2 gap-2">
                            <h3 className="font-medium text-sm">
                              {prompt.title}
                            </h3>
                            <Badge variant="secondary" className="text-xs flex-shrink-0">
                              {prompt.category}
                            </Badge>
                          </div>
                          <p className="text-sm text-muted-foreground line-clamp-2">
                            {prompt.query}
                          </p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}

            </div>
          </div>
        </div>
      </SidebarInset>
    </SidebarProvider>
  )
}
