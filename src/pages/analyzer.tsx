import { useState } from "react";
import { useQueryClient, useMutation } from "@tanstack/react-query";
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Upload, Camera, AlertCircle, CheckCircle2, AlertTriangle, HelpCircle, Loader2, Play, ShieldAlert } from "lucide-react";
import { Progress } from "@/components/ui/progress";
import { Textarea } from "@/components/ui/textarea";

export default function AnalyzerPage() {
  const queryClient = useQueryClient();
  const [selectedImage, setSelectedImage] = useState<{ url: string; file: File } | null>(null);
  const [notes, setNotes] = useState("");
  const [analyzing, setAnalyzing] = useState(false);

  const analyzeMutation = useMutation({
    mutationFn: async (data: { imageBase64: string; mimeType: string; notes?: string }) => {
      const res = await fetch("/api/analysis/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
      });
      if (!res.ok) throw new Error("Analysis failed");
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["analysisHistory"] });
      queryClient.invalidateQueries({ queryKey: ["analysisStats"] });
    }
  });

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.[0]) {
      const file = e.target.files[0];
      setSelectedImage({ url: URL.createObjectURL(file), file });
      analyzeMutation.reset();
    }
  };

  const fileToBase64 = (file: File): Promise<string> =>
    new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => resolve((reader.result as string).split(",")[1]);
      reader.onerror = reject;
    });

  const handleAnalyze = async () => {
    if (!selectedImage) return;
    setAnalyzing(true);
    try {
      const base64 = await fileToBase64(selectedImage.file);
      await analyzeMutation.mutateAsync({
        imageBase64: base64,
        mimeType: selectedImage.file.type,
        notes: notes.trim() || undefined
      });
    } finally {
      setAnalyzing(false);
    }
  };

  const renderRiskBadge = (level: string) => {
    const badges: Record<string, JSX.Element> = {
      high: <div className="flex items-center gap-2 px-3 py-1.5 bg-destructive/10 text-destructive rounded-full font-medium border border-destructive/20"><AlertCircle className="w-5 h-5" />High Risk</div>,
      medium: <div className="flex items-center gap-2 px-3 py-1.5 bg-yellow-500/10 text-yellow-600 rounded-full font-medium border border-yellow-500/20"><AlertTriangle className="w-5 h-5" />Medium Risk</div>,
      low: <div className="flex items-center gap-2 px-3 py-1.5 bg-emerald-500/10 text-emerald-600 rounded-full font-medium border border-emerald-500/20"><CheckCircle2 className="w-5 h-5" />Low Risk</div>,
    };
    return badges[level] ?? <div className="flex items-center gap-2 px-3 py-1.5 bg-muted text-muted-foreground rounded-full font-medium border border-border"><HelpCircle className="w-5 h-5" />Inconclusive</div>;
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Risk Assessment</h1>
        <p className="text-muted-foreground text-lg max-w-2xl mt-1">Upload environmental or clinical photographs for an AI-powered hantavirus risk evaluation.</p>
      </div>
      <div className="grid md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Image Upload</CardTitle>
            <CardDescription>Select a clear, well-lit photo of the environment, droppings, or clinical signs.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="relative border-2 border-dashed border-border rounded-xl aspect-video bg-muted/30 hover:bg-muted/50 transition-colors overflow-hidden flex flex-col items-center justify-center">
              {selectedImage ? (
                <>
                  <img src={selectedImage.url} alt="Selected" className="w-full h-full object-cover" />
                  <div className="absolute inset-0 bg-black/40 flex items-center justify-center opacity-0 hover:opacity-100 transition-opacity">
                    <label className="cursor-pointer">
                      <input type="file" className="hidden" accept="image/*" onChange={handleFileChange} />
                      <div className="px-4 py-2 bg-white text-black font-medium rounded-md flex items-center gap-2"><Camera className="w-4 h-4" />Change Photo</div>
                    </label>
                  </div>
                </>
              ) : (
                <label className="cursor-pointer w-full h-full flex flex-col items-center justify-center gap-4 text-muted-foreground">
                  <input type="file" className="hidden" accept="image/*" onChange={handleFileChange} />
                  <div className="w-12 h-12 rounded-full bg-primary/10 text-primary flex items-center justify-center"><Upload className="w-6 h-6" /></div>
                  <div className="text-center"><p className="font-medium text-foreground">Click to upload photo</p><p className="text-sm mt-1">JPEG, PNG up to 10MB</p></div>
                </label>
              )}
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Clinical Notes (Optional)</label>
              <Textarea placeholder="Add context about the location or patient symptoms..." value={notes} onChange={(e) => setNotes(e.target.value)} className="resize-none" rows={3} />
            </div>
          </CardContent>
          <CardFooter>
            <Button onClick={handleAnalyze} disabled={!selectedImage || analyzing} className="w-full" size="lg">
              {analyzing ? <><Loader2 className="w-4 h-4 mr-2 animate-spin" />Analyzing Image...</> : <><Play className="w-4 h-4 mr-2 fill-current" />Run Assessment</>}
            </Button>
          </CardFooter>
        </Card>

        <div>
          {analyzing ? (
            <Card className="h-full flex items-center justify-center min-h-[400px]">
              <div className="flex flex-col items-center gap-4 text-center p-6">
                <div className="w-16 h-16 border-4 border-primary/20 border-t-primary rounded-full animate-spin" />
                <div><h3 className="font-semibold text-lg">Evaluating risk factors</h3><p className="text-sm text-muted-foreground">Our AI model is cross-referencing indicators...</p></div>
              </div>
            </Card>
          ) : analyzeMutation.data ? (
            <Card className="h-full">
              <CardHeader className="border-b border-border pb-4 mb-4">
                <div className="flex items-start justify-between gap-4">
                  <div><CardTitle>Assessment Complete</CardTitle><CardDescription>Generated on {new Date(analyzeMutation.data.createdAt).toLocaleDateString()}</CardDescription></div>
                  {renderRiskBadge(analyzeMutation.data.riskLevel)}
                </div>
              </CardHeader>
              <CardContent className="space-y-6">
                <div><h3 className="font-medium mb-1">Summary</h3><p className="text-muted-foreground text-sm leading-relaxed">{analyzeMutation.data.summary}</p></div>
                <div className="grid gap-6 sm:grid-cols-2">
                  <div><h3 className="font-medium text-sm mb-2">Observed Indicators</h3>
                    <ul className="space-y-1.5">{analyzeMutation.data.indicators.map((ind: string, i: number) => <li key={i} className="text-sm text-muted-foreground flex items-start gap-2"><span className="mt-1 w-1.5 h-1.5 rounded-full bg-primary/50 shrink-0" />{ind}</li>)}</ul>
                  </div>
                  <div><h3 className="font-medium text-sm mb-2">Recommended Actions</h3>
                    <ul className="space-y-1.5">{analyzeMutation.data.recommendations.map((rec: string, i: number) => <li key={i} className="text-sm text-muted-foreground flex items-start gap-2"><CheckCircle2 className="w-4 h-4 text-primary shrink-0 mt-0.5" />{rec}</li>)}</ul>
                  </div>
                </div>
                <div className="space-y-2 pt-4 border-t border-border">
                  <div className="flex items-center justify-between text-sm"><span className="font-medium">AI Confidence Score</span><span className="font-semibold">{analyzeMutation.data.confidence}%</span></div>
                  <Progress value={analyzeMutation.data.confidence} className="h-2" />
                </div>
              </CardContent>
            </Card>
          ) : (
            <Card className="h-full flex items-center justify-center min-h-[400px] bg-muted/20 border-dashed">
              <div className="flex flex-col items-center gap-4 text-center p-6 text-muted-foreground max-w-[280px]">
                <ShieldAlert className="w-12 h-12 opacity-40" />
                <div><h3 className="font-medium text-foreground">Awaiting Input</h3><p className="text-sm">Upload a photo and run the assessment to see detailed AI analysis results here.</p></div>
              </div>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
