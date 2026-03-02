import type { NextConfig } from "next";

const normalizeProxyTarget = (target?: string): string | null => {
  if (!target) {
    return null;
  }

  const normalizedTarget = target.trim().replace(/\/+$/, "");
  return normalizedTarget.length > 0 ? normalizedTarget : null;
};

const nextConfig: NextConfig = {
  devIndicators: false,
  async rewrites() {
    const proxyTarget = normalizeProxyTarget(process.env.NEXT_PROXY_TARGET);
    if (!proxyTarget) {
      return [];
    }

    return [
      {
        source: "/api/:path*",
        destination: `${proxyTarget}/api/:path*`
      }
    ];
  }
};

export default nextConfig;
