import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { formatDistanceToNow } from "date-fns";
import { AlertCircle, AlertTriangle, CheckCircle2, HelpCircle, Activity } from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";

export default function HistoryPage() {
  const { data: history, isLoading, isError } = useQuery({
    queryKey: ["analysisHistory"],
    queryFn: async () => {
      const res = await fetch("/api/analysis/history");
      if (!res.ok) throw new Error("Failed to fetch history");
      return res.json();
    }
  });

  const riskIcon = (level: string) => ({
    high: <AlertCircle className="w-5 h-5 text-destructive" />,
    medium: <AlertTriangle className="w-5 h-5 text-yellow-500" />,
    low: <CheckCircle2 className="w-5 h-5 text-emerald-500" />,
  }[level] ?? <HelpCircle className="w-5 h-5 text-muted-foreground" />);

  const riskColor = (level: string) => ({
    high: "text-destructive border-destructive/20 bg-destructive/10",
    medium: "text-yellow-700 border-yellow-500/20 bg-yellow-500/10",
    low: "text-emerald-700 border-emerald-500/20 bg-emerald-500/10",
  }[level] ?? "text-muted-foreground border-border bg-muted/50");

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Analysis History</h1>
        <p className="text-muted-foreground text-lg">Review past hantavirus risk assessments.</p>
      </div>
      <Card>
        <CardHeader><CardTitle>Recent Assessments</CardTitle><CardDescription>Chronological log of all submitted image analyses.</CardDescription></CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-4">{[1,2,3,4].map(i => <div key={i} className="flex items-center gap-4 p-4 rounded-lg border"><Skeleton className="w-10 h-10 rounded-full" /><div className="flex-1 space-y-2"><Skeleton className="w-1/4 h-4" /><Skeleton className="w-3/4 h-3" /></div></div>)}</div>
          ) : isError ? (
            <div className="text-center py-12 text-destructive">Failed to load history.</div>
          ) : !history?.length ? (
            <div className="text-center py-16 flex flex-col items-center gap-4 text-muted-foreground"><Activity className="w-12 h-12 opacity-20" /><p>No analysis records found.</p></div>
          ) : (
            <div className="space-y-4">
              {history.map((record: any) => (
                <div key={record.id} className="flex flex-col sm:flex-row sm:items-center gap-4 p-4 rounded-lg border hover:bg-muted/30 transition-colors">
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center shrink-0 border ${riskColor(record.riskLevel)}`}>{riskIcon(record.riskLevel)}</div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-1">
                      <h4 className="font-medium truncate pr-4">Assessment #{record.id.toString().padStart(4, "0")}</h4>
                      <span className="text-xs text-muted-foreground">{formatDistanceToNow(new Date(record.createdAt), { addSuffix: true })}</span>
                    </div>
                    <p className="text-sm text-muted-foreground line-clamp-1">{record.summary}</p>
                  </div>
                  <div className="text-right shrink-0"><div className="text-xs font-medium">Confidence</div><div className="text-sm font-semibold">{record.confidence}%</div></div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
