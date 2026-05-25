import { Router } from "express";
import { z } from "zod";

const router = Router();

const AnalyzeInputSchema = z.object({
  imageBase64: z.string().min(1),
  mimeType: z.string().min(1),
  notes: z.string().optional().nullable(),
});

router.post("/analysis/analyze", async (req, res) => {
  // Şimdilik sistemin çökmemesi için sahte (mock) veri dönüyoruz.
  // İleride buraya OpenAI API kodlarını ekleyeceğiz.
  res.json({
    id: Math.floor(Math.random() * 1000),
    riskLevel: "medium",
    summary: "Sistem test ediliyor. Bu bir simülasyon sonucudur.",
    indicators: ["Test Bulgu 1", "Test Bulgu 2"],
    recommendations: ["Maske takın", "Teması kesin"],
    confidence: 85,
    createdAt: new Date().toISOString()
  });
});

router.get("/analysis/history", async (req, res) => {
  res.json([]);
});

router.get("/analysis/stats", async (req, res) => {
  res.json({ 
    totalAnalyses: 0, 
    highRiskCount: 0, 
    mediumRiskCount: 0, 
    lowRiskCount: 0, 
    inconclusiveCount: 0, 
    averageConfidence: 0 
  });
});

export default router;
