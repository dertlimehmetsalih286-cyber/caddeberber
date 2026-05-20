# -*- coding: utf-8 -*-
"""
Created on Wed May 20 22:54:07 2026

@author: Dell
"""

import { Router } from "express";
import { openai } from "@workspace/integrations-openai-ai-server";
import { db } from "@workspace/db";
import { analysesTable } from "@workspace/db";
import { desc, avg, count, eq } from "drizzle-orm";
import { z } from "zod";

const router = Router();

const AnalyzeInputSchema = z.object({
  imageBase64: z.string().min(1),
  mimeType: z.string().min(1),
  notes: z.string().optional().nullable(),
});

router.post("/analysis/analyze", async (req, res) => {
  const parsed = AnalyzeInputSchema.safeParse(req.body);
  if (!parsed.success) { res.status(400).json({ error: "Invalid request body" }); return; }

  const { imageBase64, mimeType, notes } = parsed.data;

  const completion = await openai.chat.completions.create({
    model: "gpt-5.4",
    max_completion_tokens: 1024,
    messages: [
      { role: "system", content: `You are a specialized medical image analyst for hantavirus. 
        Respond ONLY with JSON: { riskLevel, summary, indicators[], recommendations[], confidence }` },
      { role: "user", content: [
        { type: "text", text: notes ? `Context: ${notes}` : "Analyze for hantavirus risk." },
        { type: "image_url", image_url: { url: `data:${mimeType};base64,${imageBase64}`, detail: "high" } }
      ]},
    ],
  });

  const raw = completion.choices[0]?.message?.content ?? "";
  const result = JSON.parse(raw.match(/\{[\s\S]*\}/)![0]);

  const [inserted] = await db.insert(analysesTable).values({
    riskLevel: result.riskLevel,
    summary: result.summary,
    indicators: JSON.stringify(result.indicators ?? []),
    recommendations: JSON.stringify(result.recommendations ?? []),
    confidence: Math.min(100, Math.max(0, result.confidence ?? 50)),
  }).returning();

  res.json({ ...inserted, indicators: JSON.parse(inserted.indicators), recommendations: JSON.parse(inserted.recommendations), createdAt: inserted.createdAt.toISOString() });
});

router.get("/analysis/history", async (req, res) => {
  const rows = await db.select().from(analysesTable).orderBy(desc(analysesTable.createdAt)).limit(50);
  res.json(rows.map(r => ({ ...r, createdAt: r.createdAt.toISOString() })));
});

router.get("/analysis/stats", async (req, res) => {
  const [total] = await db.select({ count: count() }).from(analysesTable);
  const [avgConf] = await db.select({ avg: avg(analysesTable.confidence) }).from(analysesTable);
  const byRisk = async (l: string) => Number((await db.select({ count: count() }).from(analysesTable).where(eq(analysesTable.riskLevel, l)))[0].count);
  const [high, medium, low, inc] = await Promise.all([byRisk("high"), byRisk("medium"), byRisk("low"), byRisk("inconclusive")]);
  res.json({ totalAnalyses: Number(total.count), highRiskCount: high, mediumRiskCount: medium, lowRiskCount: low, inconclusiveCount: inc, averageConfidence: Number(avgConf.avg ?? 0) });
});

export default router;
