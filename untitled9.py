# -*- coding: utf-8 -*-
"""
Created on Wed May 20 22:54:07 2026

@author: Dell
"""

import app from "./app";
import { logger } from "./lib/logger";

const port = Number(process.env["PORT"]);
if (!port) throw new Error("PORT environment variable is required.");

app.listen(port, (err) => {
  if (err) { logger.error({ err }, "Error listening on port"); process.exit(1); }
  logger.info({ port }, "Server listening");
});