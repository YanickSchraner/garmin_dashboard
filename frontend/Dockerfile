FROM oven/bun:latest AS builder

WORKDIR /app

# Install dependencies (layer cache)
COPY package.json bun.lock ./
RUN bun install --frozen-lockfile

# Build the Nuxt app
COPY . .
RUN bun run build

# ---- Runtime image ----
FROM node:lts-slim AS runner

WORKDIR /app

COPY --from=builder /app/.output ./.output

ENV NITRO_PORT=3000
ENV NITRO_HOST=0.0.0.0

EXPOSE 3000

CMD ["node", ".output/server/index.mjs"]
