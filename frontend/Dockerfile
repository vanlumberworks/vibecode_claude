# Frontend Dockerfile for Railway deployment
# Multi-stage build for optimized production image

# Stage 1: Build
FROM node:20-alpine AS builder

WORKDIR /app

# Enable pnpm
RUN corepack enable && corepack prepare pnpm@latest --activate

# Copy package files
COPY package.json pnpm-lock.yaml ./

# Install dependencies
RUN pnpm install --frozen-lockfile

# Copy source code
COPY . .

# Accept build argument for API URL
ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL

# Build the app (environment variables are baked in at build time)
RUN pnpm build

# Stage 2: Production
FROM node:20-alpine

WORKDIR /app

# Enable pnpm
RUN corepack enable && corepack prepare pnpm@latest --activate

# Copy built files from builder
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/node_modules ./node_modules

# Expose port (Railway will override with $PORT)
EXPOSE 3000

# Start the app using pnpm exec to run vite from node_modules
# Note: Railway automatically sets $PORT environment variable
CMD ["sh", "-c", "pnpm exec vite preview --host 0.0.0.0 --port ${PORT:-3000}"]
