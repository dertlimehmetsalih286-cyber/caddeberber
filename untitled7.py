# -*- coding: utf-8 -*-
"""
Created on Wed May 20 22:54:07 2026

@author: Dell
"""

import { pgTable, serial, text, integer, real, timestamp } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod/v4";

export const analysesTable = pgTable("analyses", {
  id: serial("id").primaryKey(),
  riskLevel: text("risk_level").notNull(),
  summary: text("summary").notNull(),
  indicators: text("indicators").notNull(),        // JSON string
  recommendations: text("recommendations").notNull(), // JSON string
  confidence: real("confidence").notNull(),
  createdAt: timestamp("created_at").defaultNow().notNull(),
});

export const insertAnalysisSchema = createInsertSchema(analysesTable).omit({ id: true, createdAt: true });
export type InsertAnalysis = z.infer<typeof insertAnalysisSchema>;
export type Analysis = typeof analysesTable.$inferSelect;