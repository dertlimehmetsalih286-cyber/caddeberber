# -*- coding: utf-8 -*-
"""
Created on Wed May 20 22:54:06 2026

@author: Dell
"""

import { Switch, Route, Router as WouterRouter, Link, useLocation } from "wouter";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import { Stethoscope, Activity, History, ShieldAlert } from "lucide-react";
import NotFound from "@/pages/not-found";
import AnalyzerPage from "./pages/analyzer";
import HistoryPage from "./pages/history";
import StatsPage from "./pages/stats";

const queryClient = new QueryClient();

function Layout({ children }: { children: React.ReactNode }) {
  const [location] = useLocation();

  const links = [
    { href: "/", label: "Analyzer", icon: <Stethoscope className="w-4 h-4" /> },
    { href: "/history", label: "History", icon: <History className="w-4 h-4" /> },
    { href: "/stats", label: "Statistics", icon: <Activity className="w-4 h-4" /> },
  ];

  return (
    <div className="min-h-[100dvh] flex flex-col md:flex-row bg-background">
      <aside className="w-full md:w-64 border-b md:border-b-0 md:border-r border-border bg-card shrink-0 flex flex-col">
        <div className="p-6 flex items-center gap-3 border-b border-border">
          <div className="w-8 h-8 rounded-md bg-primary flex items-center justify-center text-primary-foreground">
            <ShieldAlert className="w-5 h-5" />
          </div>
          <div>
            <h1 className="font-semibold text-foreground tracking-tight">Hantavirus</h1>
            <p className="text-xs text-muted-foreground">Risk Analyzer</p>
          </div>
        </div>
        <nav className="p-4 flex-1 flex flex-col gap-1 overflow-y-auto">
          {links.map((link) => {
            const isActive = location === link.href;
            return (
              <Link key={link.href} href={link.href}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-md text-sm transition-colors ${
                  isActive ? "bg-primary/10 text-primary font-medium" : "text-muted-foreground hover:bg-accent hover:text-foreground"
                }`}
              >
                {link.icon}
                <span>{link.label}</span>
              </Link>
            );
          })}
        </nav>
      </aside>
      <main className="flex-1 overflow-y-auto relative bg-background">
        <div className="max-w-5xl mx-auto p-4 md:p-8">{children}</div>
      </main>
    </div>
  );
}

function Router() {
  return (
    <Layout>
      <Switch>
        <Route path="/" component={AnalyzerPage} />
        <Route path="/history" component={HistoryPage} />
        <Route path="/stats" component={StatsPage} />
        <Route component={NotFound} />
      </Switch>
    </Layout>
  );
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <WouterRouter base={import.meta.env.BASE_URL.replace(/\/$/, "")}>
          <Router />
        </WouterRouter>
        <Toaster />
      </TooltipProvider>
    </QueryClientProvider>
  );
}