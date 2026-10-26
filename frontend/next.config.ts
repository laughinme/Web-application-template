import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  poweredByHeader: false,
  async rewrites() {
    const target = (process.env.API_PROXY_TARGET ?? "http://localhost:8080").replace(/\/+$/, "");
    return [{ source: "/api/:path*", destination: `${target}/api/:path*` }];
  },
};

export default nextConfig;
