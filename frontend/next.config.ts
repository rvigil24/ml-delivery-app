import type { NextConfig } from "next";
import { PHASE_DEVELOPMENT_SERVER } from "next/constants";
import path from "node:path";

const nextConfig = (phase: string): NextConfig => ({
  poweredByHeader: false,
  // Evita que un build borre las rutas de un servidor dev que sigue activo.
  distDir: phase === PHASE_DEVELOPMENT_SERVER ? ".next" : ".next-production",
  // Comparte los fixtures versionados sin mantener una copia divergente.
  turbopack: { root: path.resolve(__dirname, "..") },
});

export default nextConfig;
