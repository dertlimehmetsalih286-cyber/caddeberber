# -*- coding: utf-8 -*-
"""
Created on Wed May 20 22:54:06 2026

@author: Dell
"""

import { useGetAnalysisStats, getGetAnalysisStatsQueryKey } from "@workspace/api-client-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Activity, AlertCircle, AlertTriangle, CheckCircle2, ShieldAlert, PieChart, HelpCircle } from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";

export default function StatsPage() {
  const { data: stats, isLoading, isError } = useGetAnalysisStats({
    query: { queryKey: getGetAnalysisStatsQueryKey() }
  });

  return (
    <div className="space-y-6">
      <div><h1 className="text-3xl font-bold tracking-tight">System Statistics</h1><p className="text-muted-foreground text-lg">Aggregate metrics and risk distribution from all assessments.</p></div>
      {isLoading ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">{[1,2,3,4,5,6].map(i => <Card key={i}><CardContent className="p-6"><Skeleton className="w-12 h-12 mb-4 rounded-full" /><Skeleton className="w-1/2 h-4 mb-2" /><Skeleton className="w-1/3 h-8" /></CardContent></Card>)}</div>
      ) : !stats ? (
        <Card className="border-destructive/50 bg-destructive/5"><CardContent className="p-12 text-center text-destructive flex flex-col items-center"><Activity className="w-12 h-12 mb-4 opacity-50" />Failed to load statistics.</CardContent></Card>
      ) : (
        <div className="space-y-6">
          <div className="grid gap-4 md:grid-cols-2">
            <Card><CardContent className="p-6 flex flex-col gap-4"><div className="p-3 bg-primary/10 text-primary rounded-lg w-fit"><ShieldAlert className="w-6 h-6" /></div><div><p className="text-sm font-medium text-muted-foreground">Total Analyses</p><h2 className="text-3xl font-bold">{stats.totalAnalyses}</h2></div></CardContent></Card>
            <Card><CardContent className="p-6 flex flex-col gap-4"><div className="p-3 bg-blue-500/10 text-blue-600 rounded-lg w-fit"><Activity className="w-6 h-6" /></div><div><p className="text-sm font-medium text-muted-foreground">Avg. Confidence</p><h2 className="text-3xl font-bold">{stats.averageConfidence.toFixed(1)}%</h2></div></CardContent></Card>
          </div>
          <Card>
            <CardHeader><CardTitle className="flex items-center gap-2"><PieChart className="w-5 h-5 text-muted-foreground" />Risk Distribution</CardTitle><CardDescription>Breakdown of all analyses by assigned risk level.</CardDescription></CardHeader>
            <CardContent>
              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                {[
                  { label: "High Risk", count: stats.highRiskCount, icon: <AlertCircle className="w-4 h-4" />, cls: "text-destructive border-destructive/20 bg-destructive/5" },
                  { label: "Medium Risk", count: stats.mediumRiskCount, icon: <AlertTriangle className="w-4 h-4" />, cls: "text-yellow-600 border-yellow-500/20 bg-yellow-500/5" },
                  { label: "Low Risk", count: stats.lowRiskCount, icon: <CheckCircle2 className="w-4 h-4" />, cls: "text-emerald-600 border-emerald-500/20 bg-emerald-500/5" },
                  { label: "Inconclusive", count: stats.inconclusiveCount, icon: <HelpCircle className="w-4 h-4" />, cls: "text-muted-foreground border-border bg-muted/30" },
                ].map(({ label, count, icon, cls }) => (
                  <div key={label} className={`p-4 rounded-xl border flex flex-col gap-3 ${cls}`}>
                    <div className="flex items-center gap-2 font-medium">{icon}{label}</div>
                    <div className="text-2xl font-bold">{count}</div>
                    <div className="text-xs opacity-70 font-medium">{stats.totalAnalyses > 0 ? Math.round((count / stats.totalAnalyses) * 100) : 0}% of total</div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}