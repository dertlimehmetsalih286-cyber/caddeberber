# -*- coding: utf-8 -*-
"""
Created on Wed May 20 22:54:07 2026

@author: Dell
"""

import { Router, type IRouter } from "express";
import healthRouter from "./health";
import analysisRouter from "./analysis";

const router: IRouter = Router();
router.use(healthRouter);
router.use(analysisRouter);

export default router;