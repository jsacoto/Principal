/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  async rewrites() {
    const api = process.env.API_INTERNAL_URL || 'http://api:8000';
    return [{ source: '/backend/:path*', destination: `${api}/:path*` }];
  },
};
export default nextConfig;
