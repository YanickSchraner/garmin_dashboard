# ---- Build Stage ----
FROM oven/bun:1.1.34 AS builder

WORKDIR /app

# Install dependencies with frozen lockfile for deterministic builds
COPY package.json bun.lock ./
RUN bun install --frozen-lockfile

# Build the Nuxt app
COPY . .
RUN bun run build


# ---- Runtime Stage ----
FROM node:22-alpine AS runner

# Create a non-root user
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

WORKDIR /app

# Copy the built output from builder
COPY --from=builder /app/.output ./.output

# Set environment variables
ENV NITRO_PORT=3000
ENV NITRO_HOST=0.0.0.0
ENV NODE_ENV=production

# Switch to non-root user
USER appuser

EXPOSE 3000

# Healthcheck for frontend
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:3000/ || exit 1

CMD ["node", ".output/server/index.mjs"]
