import type { NextConfig } from "next";

// Proxies API calls through the Next.js server so the browser only ever
// talks to one origin. Required for the httpOnly auth cookie: two separate
// *.vercel.app subdomains are different sites under the Public Suffix List,
// so SameSite=Lax would silently drop the cookie on cross-origin requests.
const BACKEND_URL =
  process.env.BACKEND_URL ?? "https://filmfund-africa-backend-el-man.vercel.app";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${BACKEND_URL}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;
