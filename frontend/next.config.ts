import type { NextConfig } from "next";
import path from "node:path";

const nextConfig: NextConfig = {
  poweredByHeader: false,
  // Comparte los fixtures versionados sin mantener una copia divergente.
  turbopack: { root: path.resolve(__dirname, "..") },
};

export default nextConfig;
