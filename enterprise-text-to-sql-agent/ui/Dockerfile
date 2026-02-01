FROM node:20-slim

WORKDIR /app

COPY package.json pnpm-lock.yaml ./
RUN corepack enable && corepack prepare pnpm@9.0.0 --activate
RUN pnpm install --frozen-lockfile

COPY . .
ARG NEXT_PUBLIC_AGENT_API_URL
ENV NEXT_PUBLIC_AGENT_API_URL=${NEXT_PUBLIC_AGENT_API_URL}
RUN pnpm build

ENV PORT=8080
EXPOSE 8080

CMD ["pnpm", "start"]
