import path from "node:path";

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  devIndicators: false,
  distDir: "../.next",
  turbopack: {
    root: path.resolve(process.cwd())
  }
};

export default nextConfig;
