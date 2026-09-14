import type { NextConfig } from "next";

// Proxies API calls through the Next.js server so the browser only ever
// talks to one origin. Required for the httpOnly auth cookie: two separate
// *.vercel.app subdomains are different sites under the Public Suffix List,
// so SameSite=Lax would silently drop the cookie on cross-origin requests.
//
// Must be the bare project domain (filmfund-africa-backend.vercel.app), not
// the team-scoped -el-man alias: Vercel Authentication (SSO protection) is
// on by default for every deployment URL except the bare project domain,
// so the team alias 401s server-to-server calls like this rewrite.
const BACKEND_URL =
  process.env.BACKEND_URL ?? "https://filmfund-africa-backend.vercel.app";

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
